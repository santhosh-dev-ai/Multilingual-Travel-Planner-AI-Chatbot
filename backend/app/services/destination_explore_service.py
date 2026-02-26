import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.services.data_manager import csv_manager
from app.services.india_locations import INDIA_CITY_DATASET


SYSTEM_PROMPT = (
    "You are a professional travel historian and tourism expert. "
    "Given an Indian state name, generate: "
    "1) A concise overview of the state (max 200 words). "
    "2) A list of 8 to 12 major tourist destinations within that state. "
    "3) For each destination provide: Summary (~100 words), History (~100 words), "
    "Architecture (if applicable), Cultural significance, Best time to visit, and 3 student-friendly tips. "
    "Keep content accurate, informative, structured JSON only, no markdown, no filler, no repetition."
)

VALIDATION_PROMPT = (
    "Validate factual accuracy. Remove incorrect or doubtful claims. "
    "Keep only verifiable historical and architectural information. "
    "Preserve JSON structure and keep it concise and student-friendly. "
    "Return JSON only."
)

JSON_SCHEMA_HINT = {
    "state": "Tamil Nadu",
    "overview": "Brief state overview",
    "popular_places": [
        {
            "name": "Mahabalipuram",
            "category": "Historical/Coastal",
            "summary": "...",
            "history": "...",
            "architecture": "...",
            "cultural_importance": "...",
            "best_time_to_visit": "...",
            "student_travel_tips": ["tip1", "tip2", "tip3"],
        }
    ],
}


class DestinationExploreService:
    def __init__(self):
        self.cache_table = "destination_cache"
        self.cache_ttl_hours = 168
        self.max_response_bytes = 10_000

    async def explore_state(
        self,
        state: str,
        include_google_places: bool = False,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        normalized_state = self._normalize_state(state)

        if not force_refresh:
            cached = self._get_cached_state(normalized_state)
            if cached:
                return cached

        generated = await self._generate_with_llm(normalized_state)

        validated = await self._validate_with_llm(generated, normalized_state)
        if not validated:
            validated = generated

        structured = self._enforce_structure(validated, normalized_state)

        if include_google_places:
            await self._enrich_with_google_places(structured, normalized_state)

        structured = self._fit_response_size(structured)
        self._store_cache(normalized_state, structured)
        return structured

    def _normalize_state(self, state: str) -> str:
        clean = re.sub(r"\s+", " ", state or "").strip()
        if not clean:
            return "India"
        return clean.title()

    async def _generate_with_llm(self, state: str) -> Dict[str, Any]:
        user_prompt = (
            f"State: {state}. Generate destination intelligence in strict JSON with this shape: "
            f"{json.dumps(JSON_SCHEMA_HINT, ensure_ascii=False)}"
        )

        raw = await self._chat_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=2600,
            temperature=0.2,
        )

        if raw:
            return raw

        return self._fallback_from_dataset(state)

    async def _validate_with_llm(self, payload: Dict[str, Any], state: str) -> Optional[Dict[str, Any]]:
        user_prompt = (
            f"State: {state}. Validate and correct this JSON while preserving schema. "
            f"JSON: {json.dumps(payload, ensure_ascii=False)}"
        )

        return await self._chat_json(
            system_prompt=VALIDATION_PROMPT,
            user_prompt=user_prompt,
            max_tokens=2200,
            temperature=0.0,
        )

    async def _chat_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Optional[Dict[str, Any]]:
        if settings.GROQ_API_KEY:
            result = await self._call_groq(system_prompt, user_prompt, max_tokens, temperature)
            if result:
                return result

        if settings.OPENAI_API_KEY:
            result = await self._call_openai(system_prompt, user_prompt, max_tokens, temperature)
            if result:
                return result

        return None

    async def _call_groq(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Optional[Dict[str, Any]]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
            return self._extract_json(content)
        except Exception:
            return None

    async def _call_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Optional[Dict[str, Any]]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
            return self._extract_json(content)
        except Exception:
            return None

    def _extract_json(self, content: str) -> Optional[Dict[str, Any]]:
        if not content:
            return None

        text = content.strip().replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return data
            return None
        except Exception:
            pass

        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                data = json.loads(text[start : end + 1])
                if isinstance(data, dict):
                    return data
            except Exception:
                return None
        return None

    def _enforce_structure(self, data: Dict[str, Any], state: str) -> Dict[str, Any]:
        popular_places = data.get("popular_places") if isinstance(data, dict) else None
        if not isinstance(popular_places, list):
            return self._fallback_from_dataset(state)

        cleaned_places: List[Dict[str, Any]] = []
        for place in popular_places[:10]:
            if not isinstance(place, dict):
                continue

            name = self._trim_words(str(place.get("name") or ""), 8) or "Unknown Place"
            category = self._trim_words(str(place.get("category") or "General"), 6)
            summary = self._trim_words(str(place.get("summary") or ""), 55)
            history = self._trim_words(str(place.get("history") or ""), 55)
            architecture = self._trim_words(str(place.get("architecture") or ""), 50)
            cultural = self._trim_words(str(place.get("cultural_importance") or ""), 50)
            best_time = self._trim_words(str(place.get("best_time_to_visit") or "Oct to Mar"), 20)

            tips_raw = place.get("student_travel_tips")
            if not isinstance(tips_raw, list):
                tips_raw = []
            tips = [self._trim_words(str(t), 18) for t in tips_raw if str(t).strip()]
            if len(tips) < 3:
                tips.extend(
                    [
                        "Use student ID for discounts where available.",
                        "Prefer public transport and shared stays.",
                        "Visit major spots early to avoid peak crowds.",
                    ]
                )
            tips = tips[:3]

            cleaned_places.append(
                {
                    "name": name,
                    "category": category,
                    "summary": summary,
                    "history": history,
                    "architecture": architecture or "Primarily known for natural or cultural significance.",
                    "cultural_importance": cultural,
                    "best_time_to_visit": best_time,
                    "student_travel_tips": tips,
                }
            )

        if not cleaned_places:
            return self._fallback_from_dataset(state)

        overview = self._trim_words(str(data.get("overview") or f"{state} is a culturally rich Indian state."), 120)

        return {
            "state": state,
            "overview": overview,
            "popular_places": cleaned_places,
        }

    async def _enrich_with_google_places(self, payload: Dict[str, Any], state: str):
        api_key = (settings.GOOGLE_MAPS_API_KEY or "").strip()
        if not api_key:
            return

        places = payload.get("popular_places", [])
        if not places:
            return

        sem = asyncio.Semaphore(4)

        async def enrich_one(place: Dict[str, Any]):
            async with sem:
                enriched = await self._google_place_lookup(place.get("name", ""), state, api_key)
                if enriched:
                    place.update(enriched)

        await asyncio.gather(*(enrich_one(p) for p in places))

    async def _google_place_lookup(self, place_name: str, state: str, api_key: str) -> Optional[Dict[str, Any]]:
        if not place_name:
            return None

        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": f"{place_name}, {state}, India",
            "key": api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            results = data.get("results", [])
            if not results:
                return None

            best = results[0]
            geometry = best.get("geometry", {}).get("location", {})
            lat = geometry.get("lat")
            lng = geometry.get("lng")
            place_id = best.get("place_id")

            image_url = None
            photos = best.get("photos") or []
            if photos:
                photo_ref = photos[0].get("photo_reference")
                if photo_ref:
                    image_url = (
                        "https://maps.googleapis.com/maps/api/place/photo"
                        f"?maxwidth=1000&photo_reference={photo_ref}&key={api_key}"
                    )

            enriched = {
                "rating": float(best.get("rating", 0.0) or 0.0),
                "latitude": float(lat) if lat is not None else None,
                "longitude": float(lng) if lng is not None else None,
                "google_maps_url": f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else None,
            }
            if image_url:
                enriched["image"] = image_url
            return enriched
        except Exception:
            return None

    def _fit_response_size(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        def payload_size(data: Dict[str, Any]) -> int:
            return len(json.dumps(data, ensure_ascii=False).encode("utf-8"))

        data = payload
        while payload_size(data) > self.max_response_bytes and len(data.get("popular_places", [])) > 6:
            data["popular_places"] = data["popular_places"][:-1]

        if payload_size(data) > self.max_response_bytes:
            for place in data.get("popular_places", []):
                place["summary"] = self._trim_words(place.get("summary", ""), 35)
                place["history"] = self._trim_words(place.get("history", ""), 35)
                place["architecture"] = self._trim_words(place.get("architecture", ""), 30)
                place["cultural_importance"] = self._trim_words(place.get("cultural_importance", ""), 30)
                place["student_travel_tips"] = [self._trim_words(t, 12) for t in place.get("student_travel_tips", [])[:3]]

        return data

    def _get_cached_state(self, state: str) -> Optional[Dict[str, Any]]:
        try:
            rows = csv_manager.read(self.cache_table, use_cache=False)
        except Exception:
            return None

        if not rows:
            return None

        now = datetime.utcnow()
        cutoff = now - timedelta(hours=self.cache_ttl_hours)
        state_l = state.lower().strip()

        for row in reversed(rows):
            row_state = str(row.get("state") or "").lower().strip()
            if row_state != state_l:
                continue

            created_at_raw = row.get("created_at")
            try:
                created_at = datetime.fromisoformat(str(created_at_raw))
            except Exception:
                continue

            if created_at < cutoff:
                continue

            json_data = row.get("json_data")
            if isinstance(json_data, dict):
                return json_data
            if isinstance(json_data, str):
                try:
                    parsed = json.loads(json_data)
                    if isinstance(parsed, dict):
                        return parsed
                except Exception:
                    continue

        return None

    def _store_cache(self, state: str, payload: Dict[str, Any]):
        try:
            rows = csv_manager.read(self.cache_table, use_cache=False)
        except Exception:
            rows = []

        max_id = 0
        for row in rows:
            try:
                max_id = max(max_id, int(row.get("id") or 0))
            except Exception:
                continue

        record = {
            "id": max_id + 1,
            "state": state,
            "json_data": payload,
            "created_at": datetime.utcnow().isoformat(),
        }
        csv_manager.append(self.cache_table, [record])

    def _fallback_from_dataset(self, state: str) -> Dict[str, Any]:
        state_l = state.lower().strip()
        filtered = [item for item in INDIA_CITY_DATASET if item.state.lower() == state_l]

        if not filtered:
            filtered = [item for item in INDIA_CITY_DATASET if state_l in item.state.lower() or state_l in item.city.lower()]

        if not filtered:
            filtered = INDIA_CITY_DATASET[:8]

        places = []
        for item in filtered[:8]:
            places.append(
                {
                    "name": item.city,
                    "category": self._infer_category(item.city),
                    "summary": f"{item.city} in {item.state} is a prominent destination known for heritage, local experiences, and student-friendly travel opportunities.",
                    "history": f"{item.city} has evolved through multiple historical periods and reflects regional political, religious, and social developments in India.",
                    "architecture": "The destination includes regional architectural styles, from temple and fort traditions to colonial and modern urban forms where applicable.",
                    "cultural_importance": f"{item.city} plays a meaningful role in {item.state}'s identity through festivals, cuisine, language, arts, and community traditions.",
                    "best_time_to_visit": "October to March",
                    "student_travel_tips": [
                        "Use state buses/metro and student passes where available.",
                        "Book hostels or budget stays close to transit hubs.",
                        "Plan major sightseeing in morning hours to save time and cost.",
                    ],
                    "image": item.image,
                }
            )

        return {
            "state": state,
            "overview": f"{state} offers a diverse mix of heritage sites, natural landscapes, and living cultural traditions, making it suitable for educational and budget-conscious student travel.",
            "popular_places": places,
        }

    def _infer_category(self, name: str) -> str:
        lower = (name or "").lower()
        if any(k in lower for k in ["temple", "ghat", "palace", "fort", "cave"]):
            return "Historical/Religious"
        if any(k in lower for k in ["beach", "island", "backwater", "coast"]):
            return "Coastal/Nature"
        if any(k in lower for k in ["valley", "hill", "mount", "park", "forest"]):
            return "Nature/Adventure"
        return "Cultural/Historical"

    def _trim_words(self, text: str, max_words: int) -> str:
        clean = re.sub(r"\s+", " ", (text or "").strip())
        if not clean:
            return ""
        words = clean.split(" ")
        if len(words) <= max_words:
            return clean
        return " ".join(words[:max_words]).strip() + "..."


_destination_explore_service = DestinationExploreService()


def get_destination_explore_service() -> DestinationExploreService:
    return _destination_explore_service

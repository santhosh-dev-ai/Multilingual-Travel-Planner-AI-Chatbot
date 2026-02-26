from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.data_manager import csv_manager


router = APIRouter()


SYSTEM_PROMPT = """You are a professional Indian travel historian.

Return ONLY valid JSON.
Do NOT include markdown.
Do NOT include explanation.
Do NOT include headings.
Do NOT include triple backticks.
Do NOT include extra keys.

Generate:

1. State overview (max 150 words)
2. 6–8 major destinations in that state
3. For each destination:
   - summary (80 words max)
   - history (80 words max)
   - architecture (only if applicable)
   - cultural importance (60 words max)
   - best time to visit (short)
   - 3 concise student tips

Keep it:
- Accurate
- Concise
- Structured
- Non-repetitive"""


class DestinationExploreRequest(BaseModel):
    state: str = Field(..., min_length=2, max_length=80)


class PlaceItem(BaseModel):
    name: str
    category: str
    summary: str
    history: str
    architecture: str
    cultural_importance: str
    best_time_to_visit: str
    student_travel_tips: List[str]


class DestinationExploreResponse(BaseModel):
    state: str
    overview: str
    popular_places: List[PlaceItem]


def _normalize_state(value: str) -> str:
    return " ".join((value or "").strip().split()).title()


def _trim_words(text: Any, max_words: int) -> str:
    clean = " ".join(str(text or "").strip().split())
    if not clean:
        return ""
    words = clean.split(" ")
    if len(words) <= max_words:
        return clean
    return " ".join(words[:max_words]).strip() + "..."


def _safe_place_dict(place: Dict[str, Any]) -> Dict[str, Any]:
    tips = place.get("student_travel_tips")
    if not isinstance(tips, list):
        tips = []

    cleaned_tips = [_trim_words(t, 10) for t in tips if str(t).strip()][:3]
    while len(cleaned_tips) < 3:
        defaults = [
            "Use public transport and metro cards.",
            "Carry student ID for discounts.",
            "Visit early to avoid heavy crowds.",
        ]
        cleaned_tips.append(defaults[len(cleaned_tips)])

    return {
        "name": _trim_words(place.get("name"), 8) or "Unknown Place",
        "category": _trim_words(place.get("category"), 4) or "General",
        "summary": _trim_words(place.get("summary"), 32),
        "history": _trim_words(place.get("history"), 32),
        "architecture": _trim_words(place.get("architecture"), 28) or "Not architecture-focused.",
        "cultural_importance": _trim_words(place.get("cultural_importance"), 20),
        "best_time_to_visit": _trim_words(place.get("best_time_to_visit"), 8) or "Oct to Mar",
        "student_travel_tips": cleaned_tips,
    }


def _sanitize_payload(payload: Dict[str, Any], state: str) -> Dict[str, Any]:
    places = payload.get("popular_places")
    if not isinstance(places, list):
        places = []

    cleaned_places = [_safe_place_dict(p) for p in places if isinstance(p, dict)]

    if len(cleaned_places) < 6:
        # Fail safe: not enough valid places from model output
        raise HTTPException(status_code=500, detail="Invalid model output: insufficient destinations")

    # Keep strictly in 6-8 range
    cleaned_places = cleaned_places[:8]

    result = {
        "state": state,
        "overview": _trim_words(payload.get("overview"), 60),
        "popular_places": cleaned_places,
    }

    # Keep response under 8KB
    while len(json.dumps(result, ensure_ascii=False).encode("utf-8")) > 8192 and len(result["popular_places"]) > 6:
        result["popular_places"].pop()

    if len(json.dumps(result, ensure_ascii=False).encode("utf-8")) > 8192:
        for place in result["popular_places"]:
            place["summary"] = _trim_words(place["summary"], 22)
            place["history"] = _trim_words(place["history"], 22)
            place["architecture"] = _trim_words(place["architecture"], 16)
            place["cultural_importance"] = _trim_words(place["cultural_importance"], 14)
            place["student_travel_tips"] = [_trim_words(t, 8) for t in place["student_travel_tips"][:3]]

    if len(json.dumps(result, ensure_ascii=False).encode("utf-8")) > 8192:
        raise HTTPException(status_code=500, detail="Response too large")

    return result


def _read_cache(state: str) -> Optional[Dict[str, Any]]:
    rows = csv_manager.read("destination_cache", use_cache=False)
    if not rows:
        return None

    target = state.lower().strip()
    for row in reversed(rows):
        row_state = str(row.get("state") or "").lower().strip()
        if row_state != target:
            continue

        data = row.get("json_data")
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                continue

        if isinstance(data, dict):
            try:
                # Ensure cache still conforms exactly
                clean = _sanitize_payload(data, state)
                return clean
            except Exception:
                continue

    return None


def _write_cache(state: str, payload: Dict[str, Any]) -> None:
    rows = csv_manager.read("destination_cache", use_cache=False)
    next_id = 1
    for row in rows:
        try:
            next_id = max(next_id, int(row.get("id") or 0) + 1)
        except Exception:
            continue

    csv_manager.append(
        "destination_cache",
        [
            {
                "id": next_id,
                "state": state,
                "json_data": payload,
                "created_at": datetime.utcnow().isoformat(),
            }
        ],
    )


async def _call_llm_json(state: str) -> Dict[str, Any]:
    user_prompt = (
        "Generate destination intelligence for this Indian state: "
        f"{state}. Output valid JSON with keys: "
        "state, overview, popular_places, where popular_places is an array of objects having exactly: "
        "name, category, summary, history, architecture, cultural_importance, best_time_to_visit, student_travel_tips."
    )

    if not (settings.GROQ_API_KEY or settings.OPENAI_API_KEY):
        raise HTTPException(status_code=500, detail="LLM API key not configured")

    # 1) Groq first
    if settings.GROQ_API_KEY:
        try:
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 2200,
                "response_format": {"type": "json_object"},
            }
            headers = {
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            }
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            # Required: validate with json.loads()
            return json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid JSON from LLM")
        except HTTPException:
            raise
        except Exception:
            pass

    # 2) OpenAI fallback
    if settings.OPENAI_API_KEY:
        try:
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 2200,
                "response_format": {"type": "json_object"},
            }
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            }
            async with httpx.AsyncClient(timeout=45.0) as client:
                resp = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            # Required: validate with json.loads()
            return json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid JSON from LLM")
        except HTTPException:
            raise
        except Exception:
            pass

    raise HTTPException(status_code=500, detail="LLM generation failed")


@router.post("/destination/explore", response_model=DestinationExploreResponse)
async def explore_destination(payload: DestinationExploreRequest):
    state = _normalize_state(payload.state)
    if not state:
        raise HTTPException(status_code=400, detail="State is required")

    cached = _read_cache(state)
    if cached:
        return DestinationExploreResponse(**cached)

    # Required: try/except around LLM call
    try:
        llm_json = await _call_llm_json(state)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to generate destination data")

    # Required: never send raw LLM text, always validate first
    safe_response = _sanitize_payload(llm_json, state)

    _write_cache(state, safe_response)
    return DestinationExploreResponse(**safe_response)

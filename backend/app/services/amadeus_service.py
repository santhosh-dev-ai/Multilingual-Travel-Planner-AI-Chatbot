"""Amadeus flight search integration and student-focused ranking."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx


class AmadeusService:
    """Service for searching and ranking flight offers using Amadeus API."""

    LOCATION_ALIASES = {
        "bangalore": "bengaluru",
        "banglore": "bengaluru",
        "bombay": "mumbai",
        "calcutta": "kolkata",
        "madras": "chennai",
        "new delhi": "delhi",
    }

    def __init__(self) -> None:
        self.client_id = os.getenv("AMADEUS_CLIENT_ID", "")
        self.client_secret = os.getenv("AMADEUS_CLIENT_SECRET", "")
        self.base_url = os.getenv("AMADEUS_BASE_URL", "https://test.api.amadeus.com").rstrip("/")
        self.currency_code = os.getenv("AMADEUS_CURRENCY", "INR").upper()

    @property
    def token_url(self) -> str:
        return f"{self.base_url}/v1/security/oauth2/token"

    @property
    def search_url(self) -> str:
        return f"{self.base_url}/v2/shopping/flight-offers"

    @property
    def location_url(self) -> str:
        return f"{self.base_url}/v1/reference-data/locations"

    def is_configured(self) -> bool:
        """Check if Amadeus credentials are configured."""
        return bool(
            self.client_id
            and self.client_secret
            and self.client_id not in {"", "your_amadeus_client_id"}
            and self.client_secret not in {"", "your_amadeus_client_secret"}
        )

    async def _get_access_token(self) -> str:
        """Fetch OAuth2 access token from Amadeus."""
        if not self.is_configured():
            raise ValueError("Amadeus API credentials are not configured")

        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(self.token_url, data=data)
            response.raise_for_status()
            payload = response.json()
            token = payload.get("access_token")
            if not token:
                raise ValueError("Failed to acquire Amadeus access token")
            return token

    async def _fetch_flight_offers(
        self,
        *,
        origin_query: str,
        destination_query: str,
        departure_date: str,
        return_date: Optional[str],
        adults: int,
        cabin_class: Optional[str],
        non_stop: Optional[bool],
    ) -> Dict[str, Any]:
        """Fetch live flight offers from Amadeus."""
        token = await self._get_access_token()

        origin_code = await self._resolve_iata_code(origin_query, token)
        destination_code = await self._resolve_iata_code(destination_query, token)

        params: Dict[str, Any] = {
            "originLocationCode": origin_code,
            "destinationLocationCode": destination_code,
            "departureDate": departure_date,
            "adults": adults,
            "currencyCode": self.currency_code,
            "max": 50,
        }
        if return_date:
            params["returnDate"] = return_date
        if cabin_class:
            params["travelClass"] = cabin_class
        if non_stop is not None:
            params["nonStop"] = str(non_stop).lower()

        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.search_url, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
            return {
                "offers": payload.get("data", []),
                "origin_code": origin_code,
                "destination_code": destination_code,
            }

    async def _resolve_iata_code(self, location_query: str, token: str) -> str:
        """Resolve city/airport input to IATA code using Amadeus location API."""
        query = location_query.strip().upper()
        if len(query) == 3 and query.isalpha():
            return query

        keyword = location_query.strip().lower()
        candidates = [location_query.strip()]

        alias = self.LOCATION_ALIASES.get(keyword)
        if alias and alias not in candidates:
            candidates.append(alias)

        compact = " ".join(location_query.strip().split())
        if compact and compact not in candidates:
            candidates.append(compact)

        data: List[Dict[str, Any]] = []
        headers = {"Authorization": f"Bearer {token}"}
        for candidate in candidates:
            params = {
                "keyword": candidate,
                "subType": "CITY,AIRPORT",
                "view": "LIGHT",
                "page[limit]": 8,
            }

            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(self.location_url, params=params, headers=headers)
                response.raise_for_status()
                payload = response.json()

            data = payload.get("data", []) or []
            if data:
                break

        if not data:
            raise ValueError(f"Could not find airport/city for '{location_query}'")

        def _name_match_score(item: Dict[str, Any]) -> int:
            score = 0
            city_name = ((item.get("address") or {}).get("cityName") or "").lower()
            name = (item.get("name") or "").lower()
            iata = (item.get("iataCode") or "").lower()

            if keyword == iata:
                score += 100
            if keyword == city_name:
                score += 90
            if keyword == name:
                score += 80
            if keyword in city_name:
                score += 40
            if keyword in name:
                score += 30
            return score

        best = sorted(data, key=_name_match_score, reverse=True)[0]
        code = best.get("iataCode")
        if not code:
            raise ValueError(f"No IATA code found for '{location_query}'")
        return str(code).upper()

    @staticmethod
    def _duration_to_minutes(duration_iso: str) -> int:
        """Convert ISO-8601 duration (e.g. PT2H30M) to minutes."""
        if not duration_iso:
            return 0
        clean = duration_iso.replace("PT", "")
        hours = 0
        minutes = 0
        if "H" in clean:
            hours_part, clean = clean.split("H", 1)
            hours = int(hours_part or 0)
        if "M" in clean:
            minutes_part = clean.replace("M", "")
            minutes = int(minutes_part or 0)
        return hours * 60 + minutes

    @staticmethod
    def _has_included_baggage(offer: Dict[str, Any]) -> bool:
        """Check if offer includes checked baggage in any segment."""
        traveler_pricings = offer.get("travelerPricings", [])
        for traveler in traveler_pricings:
            fare_details = traveler.get("fareDetailsBySegment", [])
            for detail in fare_details:
                bags = detail.get("includedCheckedBags") or {}
                quantity = bags.get("quantity", 0)
                weight = bags.get("weight", 0)
                if quantity or weight:
                    return True
        return False

    def _transform_offer(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """Map raw Amadeus offer to response structure."""
        itineraries = offer.get("itineraries", [])
        outbound = itineraries[0] if itineraries else {}
        inbound = itineraries[1] if len(itineraries) > 1 else {}

        outbound_segments = outbound.get("segments", [])
        inbound_segments = inbound.get("segments", [])

        first_segment = outbound_segments[0] if outbound_segments else {}
        last_segment = inbound_segments[-1] if inbound_segments else (outbound_segments[-1] if outbound_segments else {})

        price_info = offer.get("price", {})
        total_price = float(price_info.get("grandTotal", 0.0))
        outbound_minutes = self._duration_to_minutes(outbound.get("duration", ""))
        inbound_minutes = self._duration_to_minutes(inbound.get("duration", ""))
        total_duration_minutes = outbound_minutes + inbound_minutes
        baggage_included = self._has_included_baggage(offer)

        return {
            "offer_id": offer.get("id"),
            "airline": (offer.get("validatingAirlineCodes") or [None])[0],
            "price": total_price,
            "currency": price_info.get("currency", "USD"),
            "total_duration_minutes": total_duration_minutes,
            "outbound_duration_minutes": outbound_minutes,
            "inbound_duration_minutes": inbound_minutes,
            "baggage_included": baggage_included,
            "outbound_departure": first_segment.get("departure", {}).get("at"),
            "outbound_arrival": (outbound_segments[-1].get("arrival", {}).get("at") if outbound_segments else None),
            "return_departure": (inbound_segments[0].get("departure", {}).get("at") if inbound_segments else None),
            "return_arrival": last_segment.get("arrival", {}).get("at"),
            "number_of_stops": max(len(outbound_segments) - 1, 0) + max(len(inbound_segments) - 1, 0),
        }

    @staticmethod
    def _normalized(value: float, low: float, high: float) -> float:
        if high <= low:
            return 0.0
        return (value - low) / (high - low)

    def _rank_offers(self, offers: List[Dict[str, Any]], ranking_preference: str) -> List[Dict[str, Any]]:
        """Student-focused ranking tuned to user preference."""
        if not offers:
            return []

        prices = [o["price"] for o in offers]
        durations = [o["total_duration_minutes"] for o in offers]
        p_min, p_max = min(prices), max(prices)
        d_min, d_max = min(durations), max(durations)

        preference_weights = {
            "cheapest": (0.75, 0.15, -0.10),
            "fastest": (0.30, 0.60, -0.10),
            "baggage": (0.45, 0.20, -0.25),
            "balanced": (0.60, 0.30, -0.15),
        }
        price_weight, duration_weight, baggage_bonus_val = preference_weights.get(
            ranking_preference, preference_weights["balanced"]
        )

        for offer in offers:
            price_score = self._normalized(offer["price"], p_min, p_max)
            duration_score = self._normalized(offer["total_duration_minutes"], d_min, d_max)
            baggage_bonus = baggage_bonus_val if offer["baggage_included"] else 0.0

            # Lower total score ranks higher.
            offer["ranking_score"] = (price_weight * price_score) + (duration_weight * duration_score) + baggage_bonus

        return sorted(offers, key=lambda x: x["ranking_score"])

    async def search_flights(
        self,
        *,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str],
        adults: int,
        budget: Optional[float],
        cabin_class: Optional[str],
        max_stops: Optional[int],
        baggage_required: bool,
        ranking_preference: str,
        non_stop: Optional[bool],
    ) -> Dict[str, Any]:
        """Search live flights and return top student-optimized offers."""
        search_result = await self._fetch_flight_offers(
            origin_query=origin,
            destination_query=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=adults,
            cabin_class=cabin_class,
            non_stop=non_stop,
        )
        raw_offers = search_result["offers"]
        provider_offers_count = len(raw_offers)

        transformed = [self._transform_offer(offer) for offer in raw_offers]
        before_filter_count = len(transformed)

        if budget is not None:
            transformed = [offer for offer in transformed if offer["price"] <= budget]

        if max_stops is not None:
            transformed = [offer for offer in transformed if offer["number_of_stops"] <= max_stops]

        if baggage_required:
            transformed = [offer for offer in transformed if offer["baggage_included"]]

        after_filter_count = len(transformed)

        ranked = self._rank_offers(transformed, ranking_preference=ranking_preference)
        top_five = ranked[:5]

        return {
            "flights": top_five,
            "origin_code": search_result["origin_code"],
            "destination_code": search_result["destination_code"],
            "provider_offers_count": provider_offers_count,
            "before_filter_count": before_filter_count,
            "after_filter_count": after_filter_count,
        }


amadeus_service = AmadeusService()

"""RapidAPI Railway train integration with student-focused recommendation logic."""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

import httpx


class TrainServiceError(Exception):
    pass


class TrainService:
    """Train service using RapidAPI Railway endpoints."""

    def __init__(self) -> None:
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY", "").strip()
        self.rapidapi_host = os.getenv("RAPIDAPI_HOST", "").strip()

    def is_configured(self) -> bool:
        return bool(self.rapidapi_key and self.rapidapi_host)

    def _build_base_url(self) -> str:
        if self.rapidapi_host.startswith("http://") or self.rapidapi_host.startswith("https://"):
            return self.rapidapi_host.rstrip("/")
        return f"https://{self.rapidapi_host.strip('/')}"

    def _headers(self) -> Dict[str, str]:
        return {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": self.rapidapi_host,
        }

    @staticmethod
    def _duration_to_minutes(value: Any) -> int:
        if value is None:
            return 10**9
        if isinstance(value, (int, float)):
            return int(value)
        text = str(value).strip().lower()
        if text.isdigit():
            return int(text)

        d_match = re.search(r"(\d+)\s*d", text)
        h_match = re.search(r"(\d+)\s*h", text)
        m_match = re.search(r"(\d+)\s*m", text)

        days = int(d_match.group(1)) if d_match else 0
        hours = int(h_match.group(1)) if h_match else 0
        minutes = int(m_match.group(1)) if m_match else 0

        if days == 0 and hours == 0 and minutes == 0:
            hm = re.match(r"^(\d{1,2}):(\d{2})$", text)
            if hm:
                return int(hm.group(1)) * 60 + int(hm.group(2))

        return (days * 24 * 60) + (hours * 60) + minutes

    @staticmethod
    def _extract_list(payload: Any) -> List[Dict[str, Any]]:
        if isinstance(payload, list):
            return [x for x in payload if isinstance(x, dict)]
        if isinstance(payload, dict):
            for key in ("data", "result", "results", "trains", "items"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [x for x in value if isinstance(x, dict)]
        return []

    @staticmethod
    def _nested(item: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
        for key in keys:
            if key in item and item[key] not in (None, ""):
                return item[key]
        return default

    async def _call_rapidapi(self, path: str, params: Dict[str, Any]) -> Any:
        if not self.is_configured():
            raise TrainServiceError("RapidAPI credentials are not configured")

        url = f"{self._build_base_url()}{path}"

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(url, headers=self._headers(), params=params)
            response.raise_for_status()
            return response.json() if response.content else {}
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text or "RapidAPI request failed"
            raise TrainServiceError(f"RapidAPI error ({exc.response.status_code}): {detail}") from exc
        except httpx.HTTPError as exc:
            raise TrainServiceError(f"RapidAPI network error: {str(exc)}") from exc

    async def get_trains_between_stations(self, from_station: str, to_station: str, date: str) -> List[Dict[str, Any]]:
        payload = await self._call_rapidapi(
            "/api/v3/trainBetweenStations",
            {
                "fromStationCode": from_station,
                "toStationCode": to_station,
                "dateOfJourney": date,
            },
        )
        return self._extract_list(payload)

    async def get_seat_availability(self, train_no: str, from_station: str, to_station: str, date: str, class_type: str) -> Dict[str, Any]:
        payload = await self._call_rapidapi(
            "/api/v1/checkSeatAvailability",
            {
                "trainNo": train_no,
                "fromStationCode": from_station,
                "toStationCode": to_station,
                "date": date,
                "classType": class_type,
                "quota": "GN",
            },
        )
        if isinstance(payload, dict):
            return payload
        return {}

    async def get_train_schedule(self, train_no: str) -> Dict[str, Any]:
        payload = await self._call_rapidapi(
            "/api/v1/getTrainSchedule",
            {
                "trainNo": train_no,
            },
        )
        if isinstance(payload, dict):
            return payload
        return {}

    @staticmethod
    def _extract_price(train: Dict[str, Any]) -> float:
        for key in ("fare", "price", "ticket_fare", "amount"):
            value = train.get(key)
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str) and value.replace(".", "", 1).isdigit():
                return float(value)
        return 0.0

    @staticmethod
    def _availability_score(availability_payload: Dict[str, Any]) -> int:
        text_parts: List[str] = []

        data = availability_payload.get("data") if isinstance(availability_payload, dict) else None
        if isinstance(data, list):
            for row in data:
                if isinstance(row, dict):
                    status = row.get("current_status") or row.get("status") or row.get("availability")
                    if status:
                        text_parts.append(str(status))
        elif isinstance(data, dict):
            status = data.get("current_status") or data.get("status") or data.get("availability")
            if status:
                text_parts.append(str(status))

        raw = " ".join(text_parts).upper()
        if not raw:
            return 0
        if "AVAILABLE" in raw or raw.startswith("AVL"):
            return 100
        if "RAC" in raw:
            return 70
        if "WL" in raw or "WAIT" in raw:
            return 30
        return 50

    def _apply_student_logic(
        self,
        *,
        trains: List[Dict[str, Any]],
        from_station: str,
        to_station: str,
        date: str,
        requested_class_type: str,
        budget: float,
    ) -> Dict[str, Any]:
        budget_low = budget <= 1500
        chosen_class = "SL" if budget_low else requested_class_type.upper()
        student_discount_applied = budget_low
        student_discount_rate = 0.10 if student_discount_applied else 0.0

        enriched: List[Dict[str, Any]] = []
        for train in trains:
            train_no = str(self._nested(train, ["train_number", "trainNo", "number", "train_no"], ""))
            train_name = str(self._nested(train, ["train_name", "name"], "Unknown Train"))
            duration_raw = self._nested(train, ["duration", "travel_time", "running_time"], "")
            duration_minutes = self._duration_to_minutes(duration_raw)
            base_fare = self._extract_price(train)
            discounted_fare = round(base_fare * (1 - student_discount_rate), 2)

            enriched.append(
                {
                    "train_number": train_no,
                    "train_name": train_name,
                    "from_station": from_station,
                    "to_station": to_station,
                    "date": date,
                    "class_type": chosen_class,
                    "duration": str(duration_raw) if duration_raw else None,
                    "duration_minutes": duration_minutes,
                    "base_fare": base_fare,
                    "student_discounted_fare": discounted_fare,
                    "student_discount_rate": student_discount_rate,
                    "availability_score": 0,
                    "availability": None,
                    "schedule": None,
                    "is_budget_fit": discounted_fare <= budget if discounted_fare > 0 else True,
                }
            )

        return {
            "chosen_class": chosen_class,
            "student_discount_applied": student_discount_applied,
            "trains": enriched,
        }

    async def search_trains_for_students(
        self,
        *,
        from_station: str,
        to_station: str,
        date: str,
        class_type: str,
        budget: float,
    ) -> Dict[str, Any]:
        if not self.is_configured():
            raise TrainServiceError("Missing RAPIDAPI_KEY or RAPIDAPI_HOST")

        trains = await self.get_trains_between_stations(from_station=from_station, to_station=to_station, date=date)
        logic_applied = self._apply_student_logic(
            trains=trains,
            from_station=from_station,
            to_station=to_station,
            date=date,
            requested_class_type=class_type,
            budget=budget,
        )

        enriched_trains: List[Dict[str, Any]] = logic_applied["trains"]
        chosen_class = logic_applied["chosen_class"]

        for train in enriched_trains[:10]:
            train_no = train.get("train_number")
            if not train_no:
                continue

            try:
                availability_payload = await self.get_seat_availability(
                    train_no=train_no,
                    from_station=from_station,
                    to_station=to_station,
                    date=date,
                    class_type=chosen_class,
                )
                train["availability_score"] = self._availability_score(availability_payload)
                train["availability"] = availability_payload.get("data", availability_payload)
            except TrainServiceError:
                train["availability_score"] = 0
                train["availability"] = None

            try:
                schedule_payload = await self.get_train_schedule(train_no=train_no)
                train["schedule"] = schedule_payload.get("data", schedule_payload)
            except TrainServiceError:
                train["schedule"] = None

        ranked = sorted(
            enriched_trains,
            key=lambda item: (
                item.get("duration_minutes", 10**9),
                -item.get("availability_score", 0),
                item.get("student_discounted_fare", item.get("base_fare", 0)),
            ),
        )

        return {
            "recommended_trains": ranked[:5],
            "student_discount_applied": logic_applied["student_discount_applied"],
        }


train_service = TrainService()

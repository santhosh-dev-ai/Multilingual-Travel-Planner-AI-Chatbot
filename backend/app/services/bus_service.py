"""Smart bus booking simulation engine with dynamic pricing and seat management."""

from __future__ import annotations

from datetime import date, datetime
from hashlib import md5
from typing import Any, Dict, List, Set
from uuid import uuid4


class BusServiceError(Exception):
    pass


class BusService:
    """In-memory bus simulation service."""

    def __init__(self) -> None:
        self.currency = "INR"
        self.student_discount_rate = 0.10

        self.routes: List[Dict[str, Any]] = [
            {
                "route_id": "R-CHN-BLR-01",
                "from_city": "Chennai",
                "to_city": "Bangalore",
                "operator": "SouthLine Travels",
                "duration_minutes": 360,
                "base_price": 820,
                "base_demand": 0.62,
            },
            {
                "route_id": "R-CHN-BLR-02",
                "from_city": "Chennai",
                "to_city": "Bangalore",
                "operator": "Campus Express",
                "duration_minutes": 410,
                "base_price": 680,
                "base_demand": 0.74,
            },
            {
                "route_id": "R-HYD-BLR-01",
                "from_city": "Hyderabad",
                "to_city": "Bangalore",
                "operator": "Deccan Wheels",
                "duration_minutes": 570,
                "base_price": 950,
                "base_demand": 0.58,
            },
            {
                "route_id": "R-MDU-CHN-01",
                "from_city": "Madurai",
                "to_city": "Chennai",
                "operator": "Tamil Connect",
                "duration_minutes": 500,
                "base_price": 760,
                "base_demand": 0.54,
            },
        ]

        self.booked_seats: Dict[str, Set[int]] = {}
        self.selected_seats: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _normalize_city(value: str) -> str:
        return value.strip().lower()

    @staticmethod
    def _validate_date(value: str) -> date:
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise BusServiceError("date must be in YYYY-MM-DD format") from exc

    @staticmethod
    def _seat_layout() -> List[Dict[str, Any]]:
        layout: List[Dict[str, Any]] = []
        for seat_no in range(1, 41):
            layout.append(
                {
                    "seat_number": seat_no,
                    "row": ((seat_no - 1) // 4) + 1,
                    "column": ((seat_no - 1) % 4) + 1,
                }
            )
        return layout

    @staticmethod
    def _trip_id(route_id: str, travel_date: str, bus_type: str, seat_type: str) -> str:
        return f"{route_id}:{travel_date}:{bus_type.upper()}:{seat_type.upper()}"

    def _demand_factor(self, route: Dict[str, Any], travel_date: date) -> float:
        days_to_travel = max((travel_date - date.today()).days, 0)
        urgency_boost = 0.18 if days_to_travel <= 3 else (0.10 if days_to_travel <= 7 else 0.03)

        seed = f"{route['route_id']}:{travel_date.isoformat()}"
        seeded_variation = (int(md5(seed.encode()).hexdigest()[:2], 16) / 255.0) * 0.15

        demand = route["base_demand"] + urgency_boost + seeded_variation
        return min(max(demand, 0.0), 0.98)

    @staticmethod
    def _bus_type_multiplier(bus_type: str) -> float:
        return 1.25 if bus_type.upper() == "AC" else 1.0

    @staticmethod
    def _seat_type_multiplier(seat_type: str) -> float:
        return 1.18 if seat_type.upper() == "SLEEPER" else 1.0

    def _occupancy(self, trip_id: str, demand_factor: float) -> float:
        booked_count = len(self.booked_seats.get(trip_id, set()))
        booked_ratio = booked_count / 40.0
        return min(max((demand_factor * 0.65) + (booked_ratio * 0.35), 0.0), 0.99)

    def _calculate_price(
        self,
        *,
        base_price: float,
        bus_type: str,
        seat_type: str,
        demand_factor: float,
        occupancy: float,
    ) -> Dict[str, float]:
        # Pricing logic:
        # 1) Start with route base fare
        # 2) Apply AC/Non-AC and Sleeper/Seater multipliers
        # 3) Add demand surge (up to +25%) based on current demand factor
        # 4) If occupancy > 70%, add additional occupancy surge (+15%)
        # 5) Apply student discount (-10%) on the final surged fare
        fare = base_price
        fare *= self._bus_type_multiplier(bus_type)
        fare *= self._seat_type_multiplier(seat_type)

        demand_surge = 1.0 + (0.25 * demand_factor)
        fare *= demand_surge

        occupancy_surge = 1.15 if occupancy > 0.70 else 1.0
        fare *= occupancy_surge

        fare_before_discount = round(fare, 2)
        final_fare = round(fare_before_discount * (1 - self.student_discount_rate), 2)

        return {
            "fare_before_discount": fare_before_discount,
            "final_fare": final_fare,
            "demand_factor": round(demand_factor, 3),
            "occupancy": round(occupancy, 3),
            "student_discount_applied": True,
        }

    def search(
        self,
        *,
        from_city: str,
        to_city: str,
        travel_date: str,
        bus_type: str,
        budget: float,
    ) -> Dict[str, Any]:
        if budget <= 0:
            raise BusServiceError("budget must be greater than 0")

        parsed_date = self._validate_date(travel_date)

        filtered_routes = [
            route
            for route in self.routes
            if self._normalize_city(route["from_city"]) == self._normalize_city(from_city)
            and self._normalize_city(route["to_city"]) == self._normalize_city(to_city)
        ]

        recommended: List[Dict[str, Any]] = []
        seat_layout = self._seat_layout()

        for route in filtered_routes:
            demand = self._demand_factor(route, parsed_date)

            for seat_type in ("SEATER", "SLEEPER"):
                trip_id = self._trip_id(route["route_id"], travel_date, bus_type, seat_type)
                occupancy = self._occupancy(trip_id, demand)
                pricing = self._calculate_price(
                    base_price=route["base_price"],
                    bus_type=bus_type,
                    seat_type=seat_type,
                    demand_factor=demand,
                    occupancy=occupancy,
                )

                if pricing["final_fare"] > budget:
                    continue

                booked = self.booked_seats.get(trip_id, set())
                available_seats = [seat for seat in seat_layout if seat["seat_number"] not in booked]

                recommended.append(
                    {
                        "trip_id": trip_id,
                        "route_id": route["route_id"],
                        "operator": route["operator"],
                        "from_city": route["from_city"],
                        "to_city": route["to_city"],
                        "date": travel_date,
                        "bus_type": bus_type.upper(),
                        "seat_type": seat_type,
                        "duration_minutes": route["duration_minutes"],
                        "price": pricing["final_fare"],
                        "fare_before_discount": pricing["fare_before_discount"],
                        "currency": self.currency,
                        "student_discount_applied": pricing["student_discount_applied"],
                        "demand_factor": pricing["demand_factor"],
                        "occupancy": pricing["occupancy"],
                        "available_seats_count": len(available_seats),
                        "seat_layout": available_seats,
                    }
                )

        ranked = sorted(recommended, key=lambda item: item["price"])
        return {
            "recommended_buses": ranked,
            "student_discount_applied": True,
        }

    def select_seat(self, *, trip_id: str, seat_number: int) -> Dict[str, Any]:
        if seat_number < 1 or seat_number > 40:
            raise BusServiceError("seat_number must be between 1 and 40")

        booked = self.booked_seats.get(trip_id, set())
        if seat_number in booked:
            raise BusServiceError("Seat is already booked")

        for selection in self.selected_seats.values():
            if selection["trip_id"] == trip_id and selection["seat_number"] == seat_number:
                raise BusServiceError("Seat is already selected by another user")

        selection_id = f"SEL-{uuid4().hex[:10].upper()}"
        self.selected_seats[selection_id] = {
            "trip_id": trip_id,
            "seat_number": seat_number,
            "selected_at": datetime.utcnow().isoformat(),
        }
        return {
            "selection_id": selection_id,
            "trip_id": trip_id,
            "seat_number": seat_number,
            "status": "selected",
        }

    def _get_option_by_trip_id(self, trip_id: str) -> Dict[str, Any]:
        try:
            route_id, travel_date, bus_type, seat_type = trip_id.split(":")
        except ValueError as exc:
            raise BusServiceError("Invalid trip_id format") from exc

        route = next((item for item in self.routes if item["route_id"] == route_id), None)
        if route is None:
            raise BusServiceError("Trip route not found")

        demand = self._demand_factor(route, self._validate_date(travel_date))
        occupancy = self._occupancy(trip_id, demand)
        pricing = self._calculate_price(
            base_price=route["base_price"],
            bus_type=bus_type,
            seat_type=seat_type,
            demand_factor=demand,
            occupancy=occupancy,
        )

        return {
            "route": route,
            "trip_id": trip_id,
            "bus_type": bus_type,
            "seat_type": seat_type,
            "final_fare": pricing["final_fare"],
        }

    def book(self, *, selection_id: str) -> Dict[str, Any]:
        selection = self.selected_seats.get(selection_id)
        if selection is None:
            raise BusServiceError("Invalid selection_id")

        trip_id = selection["trip_id"]
        seat_number = selection["seat_number"]

        booked = self.booked_seats.setdefault(trip_id, set())
        if seat_number in booked:
            raise BusServiceError("Seat was just booked by another user")

        option = self._get_option_by_trip_id(trip_id)
        booked.add(seat_number)
        del self.selected_seats[selection_id]

        return {
            "booking_id": f"BUS-{uuid4().hex[:12].upper()}",
            "seat_number": seat_number,
            "final_price": option["final_fare"],
            "status": "confirmed",
        }


bus_service = BusService()

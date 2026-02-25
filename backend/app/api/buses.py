"""Bus simulation API endpoints."""

from datetime import date
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.bus_service import BusServiceError, bus_service


router = APIRouter()


class BusSearchRequest(BaseModel):
    from_city: str = Field(..., min_length=2, max_length=80)
    to_city: str = Field(..., min_length=2, max_length=80)
    date: date
    bus_type: str = Field(default="AC", description="AC or Non-AC")
    budget: float = Field(..., gt=0)


class SeatSelectionRequest(BaseModel):
    trip_id: str = Field(..., min_length=5)
    seat_number: int = Field(..., ge=1, le=40)


class BookingRequest(BaseModel):
    selection_id: str = Field(..., min_length=5)


class BusSearchResponse(BaseModel):
    recommended_buses: List[Dict[str, Any]]
    student_discount_applied: bool


class BookingResponse(BaseModel):
    booking_id: str
    seat_number: int
    final_price: float
    status: str


@router.post("/bus/search", response_model=BusSearchResponse)
async def bus_search(payload: BusSearchRequest):
    bus_type_normalized = payload.bus_type.strip().upper()
    if bus_type_normalized not in {"AC", "NON-AC", "NONAC"}:
        raise HTTPException(status_code=400, detail="bus_type must be either 'AC' or 'Non-AC'")
    bus_type_value = "NON-AC" if bus_type_normalized in {"NON-AC", "NONAC"} else "AC"

    try:
        return bus_service.search(
            from_city=payload.from_city,
            to_city=payload.to_city,
            travel_date=str(payload.date),
            bus_type=bus_type_value,
            budget=payload.budget,
        )
    except BusServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Bus search failed: {str(exc)}")


@router.post("/bus/select-seat")
async def select_seat(payload: SeatSelectionRequest):
    try:
        return bus_service.select_seat(
            trip_id=payload.trip_id,
            seat_number=payload.seat_number,
        )
    except BusServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Seat selection failed: {str(exc)}")


@router.post("/bus/book", response_model=BookingResponse)
async def book_bus(payload: BookingRequest):
    try:
        return bus_service.book(selection_id=payload.selection_id)
    except BusServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Booking failed: {str(exc)}")


class LegacyBusSearchRequest(BaseModel):
    origin: str = Field(..., min_length=2, max_length=80)
    destination: str = Field(..., min_length=2, max_length=80)
    travel_date: date
    budget: float = Field(..., gt=0)


@router.post("/search/buses", response_model=BusSearchResponse)
async def search_buses_legacy(payload: LegacyBusSearchRequest):
    try:
        return bus_service.search(
            from_city=payload.origin,
            to_city=payload.destination,
            travel_date=str(payload.travel_date),
            bus_type="AC",
            budget=payload.budget,
        )
    except BusServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Bus search failed: {str(exc)}")

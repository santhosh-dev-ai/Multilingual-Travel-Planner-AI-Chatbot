"""Flight search API endpoints."""

from datetime import date
from typing import List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.services.amadeus_service import amadeus_service


router = APIRouter()


class FlightSearchRequest(BaseModel):
    origin: str = Field(..., min_length=2, max_length=100, description="Origin city or airport")
    destination: str = Field(..., min_length=2, max_length=100, description="Destination city or airport")
    departure_date: date
    return_date: date
    adults: int = Field(default=1, ge=1, le=9)
    budget: float = Field(..., gt=0)
    cabin_class: str = Field(default="ECONOMY", description="ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST")
    max_stops: int = Field(default=2, ge=0, le=4)
    baggage_required: bool = Field(default=False)
    ranking_preference: str = Field(default="balanced", description="cheapest, fastest, baggage, balanced")
    non_stop_only: bool = Field(default=False)

    @field_validator("origin", "destination")
    @classmethod
    def validate_location(cls, value: str) -> str:
        clean = value.strip()
        if len(clean) < 2:
            raise ValueError("Location must be at least 2 characters")
        return clean

    @field_validator("cabin_class")
    @classmethod
    def validate_cabin_class(cls, value: str) -> str:
        allowed = {"ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"}
        normalized = value.strip().upper()
        if normalized not in allowed:
            raise ValueError(f"cabin_class must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @field_validator("ranking_preference")
    @classmethod
    def validate_ranking_preference(cls, value: str) -> str:
        allowed = {"cheapest", "fastest", "baggage", "balanced"}
        normalized = value.strip().lower()
        if normalized not in allowed:
            raise ValueError(f"ranking_preference must be one of: {', '.join(sorted(allowed))}")
        return normalized


class FlightOfferResponse(BaseModel):
    offer_id: Optional[str]
    airline: Optional[str]
    price: float
    currency: str
    total_duration_minutes: int
    outbound_duration_minutes: int
    inbound_duration_minutes: int
    baggage_included: bool
    outbound_departure: Optional[str]
    outbound_arrival: Optional[str]
    return_departure: Optional[str]
    return_arrival: Optional[str]
    number_of_stops: int
    ranking_score: float


class FlightSearchResponse(BaseModel):
    success: bool
    data_source: str
    resolved_origin_iata: Optional[str]
    resolved_destination_iata: Optional[str]
    total_results: int
    filters_applied: dict
    flights: List[FlightOfferResponse]


@router.post("/search/flights", response_model=FlightSearchResponse)
async def search_flights(payload: FlightSearchRequest):
    """Search and rank flights using live Amadeus data for student-friendly options."""
    if payload.return_date and payload.return_date < payload.departure_date:
        raise HTTPException(status_code=400, detail="return_date must be on or after departure_date")

    if not amadeus_service.is_configured():
        raise HTTPException(
            status_code=500,
            detail="Amadeus credentials are missing. Set AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET in environment variables.",
        )

    try:
        result = await amadeus_service.search_flights(
            origin=payload.origin,
            destination=payload.destination,
            departure_date=str(payload.departure_date),
            return_date=str(payload.return_date),
            adults=payload.adults,
            budget=payload.budget,
            cabin_class=payload.cabin_class,
            max_stops=payload.max_stops,
            baggage_required=payload.baggage_required,
            ranking_preference=payload.ranking_preference,
            non_stop=payload.non_stop_only,
        )
        flights = result["flights"]
    except httpx.HTTPStatusError as exc:
        detail = "Amadeus API request failed"
        try:
            detail_payload = exc.response.json()
            if isinstance(detail_payload, dict):
                if isinstance(detail_payload.get("errors"), list) and detail_payload["errors"]:
                    detail = detail_payload["errors"][0].get("detail", detail)
                elif detail_payload.get("error_description"):
                    detail = detail_payload.get("error_description")
                elif detail_payload.get("detail"):
                    detail = detail_payload.get("detail")
        except Exception:
            detail = exc.response.text or detail
        raise HTTPException(status_code=502, detail=detail)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Flight search failed: {str(exc)}")

    return {
        "success": True,
        "data_source": amadeus_service.base_url,
        "resolved_origin_iata": result.get("origin_code"),
        "resolved_destination_iata": result.get("destination_code"),
        "total_results": len(flights),
        "filters_applied": {
            "origin": payload.origin,
            "destination": payload.destination,
            "departure_date": str(payload.departure_date),
            "return_date": str(payload.return_date),
            "adults": payload.adults,
            "budget": payload.budget,
            "currency": amadeus_service.currency_code,
            "cabin_class": payload.cabin_class,
            "max_stops": payload.max_stops,
            "baggage_required": payload.baggage_required,
            "non_stop_only": payload.non_stop_only,
            "ranking_preference": payload.ranking_preference,
            "provider_offers_count": result.get("provider_offers_count", 0),
            "offers_before_filters": result.get("before_filter_count", 0),
            "offers_after_filters": result.get("after_filter_count", 0),
            "ranking_strategy": ["user_preference_weighted", "student_optimized"],
        },
        "flights": flights,
    }

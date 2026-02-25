"""Train search API using RapidAPI Railway endpoints."""

from datetime import date
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.train_service import TrainServiceError, train_service


router = APIRouter()


class TrainStudentSearchRequest(BaseModel):
    from_station: str = Field(..., min_length=2, max_length=10)
    to_station: str = Field(..., min_length=2, max_length=10)
    date: date
    class_type: str = Field(default="3A", min_length=2, max_length=5)
    budget: float = Field(..., gt=0)


class TrainSearchResponse(BaseModel):
    recommended_trains: List[Dict[str, Any]]
    student_discount_applied: bool


class LegacyTrainSearchRequest(BaseModel):
    origin: str = Field(..., min_length=2, max_length=10)
    destination: str = Field(..., min_length=2, max_length=10)
    travel_date: date
    budget: float = Field(..., gt=0)
    ranking_preference: str = Field(default="balanced")
    max_transfers: int = Field(default=1, ge=0)
    passengers: int = Field(default=1, ge=1)


@router.get("/trains/health")
async def trains_health() -> Dict[str, Any]:
    configured = train_service.is_configured()
    return {
        "success": configured,
        "configured": configured,
        "provider": "RapidAPI Railway",
        "detail": None if configured else "Set RAPIDAPI_KEY and RAPIDAPI_HOST",
    }


@router.post("/trains/search", response_model=TrainSearchResponse)
async def search_trains(payload: TrainStudentSearchRequest):
    if not train_service.is_configured():
        raise HTTPException(
            status_code=500,
            detail="RapidAPI train integration is not configured. Set RAPIDAPI_KEY and RAPIDAPI_HOST.",
        )

    try:
        result = await train_service.search_trains_for_students(
            from_station=payload.from_station.strip().upper(),
            to_station=payload.to_station.strip().upper(),
            date=str(payload.date),
            class_type=payload.class_type.strip().upper(),
            budget=payload.budget,
        )
        return result
    except TrainServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Train search failed: {str(exc)}")


@router.post("/search/trains", response_model=TrainSearchResponse)
async def search_trains_legacy(payload: LegacyTrainSearchRequest):
    if not train_service.is_configured():
        raise HTTPException(
            status_code=500,
            detail="RapidAPI train integration is not configured. Set RAPIDAPI_KEY and RAPIDAPI_HOST.",
        )

    try:
        result = await train_service.search_trains_for_students(
            from_station=payload.origin.strip().upper(),
            to_station=payload.destination.strip().upper(),
            date=str(payload.travel_date),
            class_type="3A",
            budget=payload.budget,
        )
        return result
    except TrainServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Train search failed: {str(exc)}")

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List

from app.services.india_locations import get_popular_india_locations, search_india_locations


router = APIRouter()


class LocationItem(BaseModel):
    city: str
    state: str
    country: str
    popularity: int
    image: str


class LocationsResponse(BaseModel):
    locations: List[LocationItem]


@router.get("/locations/popular", response_model=LocationsResponse)
async def get_popular_locations(limit: int = Query(100, ge=1, le=500)):
    return {"locations": get_popular_india_locations(limit=limit)}


@router.get("/locations/search", response_model=LocationsResponse)
async def search_locations(q: str = Query("", min_length=1), limit: int = Query(10, ge=1, le=10)):
    locations = await search_india_locations(query=q, limit=limit)
    return {"locations": locations}

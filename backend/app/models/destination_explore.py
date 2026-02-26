from pydantic import BaseModel, Field
from typing import List, Optional


class DestinationExploreRequest(BaseModel):
    state: str = Field(..., min_length=2, max_length=80, description="Indian state name")
    include_google_places: bool = Field(
        False,
        description="Optionally enrich places with Google rating/location/image",
    )
    force_refresh: bool = Field(
        False,
        description="Bypass cache and regenerate destination intelligence",
    )


class PopularPlace(BaseModel):
    name: str
    category: str
    summary: str
    history: str
    architecture: str
    cultural_importance: str
    best_time_to_visit: str
    student_travel_tips: List[str]
    rating: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    google_maps_url: Optional[str] = None
    image: Optional[str] = None


class DestinationExploreResponse(BaseModel):
    state: str
    overview: str
    popular_places: List[PopularPlace]

"""
Enhanced Pydantic Models for Production System
Comprehensive data models with validation
"""

from .user import User, UserProfile, UserPreferences, UserCreate, UserUpdate
from .destination import (
    Destination, 
    DestinationDetail, 
    DestinationCreate, 
    DestinationMetrics
)
from .itinerary import (
    Itinerary, 
    ItineraryDay, 
    ItineraryActivity,
    ItineraryRequest,
    ItineraryResponse
)
from .analytics import (
    UserBehavior,
    SearchQuery,
    DestinationTrend,
    RecommendationScore
)
from .responses import (
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse
)
from .ranking import (
    Place,
    PlaceType,
    PriceRange,
    RankingRequest,
    RankedPlace,
    RankingResponse,
    ScoreBreakdown,
    Coordinates
)

__all__ = [
    # User models
    "User",
    "UserProfile",
    "UserPreferences",
    "UserCreate",
    "UserUpdate",
    # Destination models
    "Destination",
    "DestinationDetail",
    "DestinationCreate",
    "DestinationMetrics",
    # Itinerary models
    "Itinerary",
    "ItineraryDay",
    "ItineraryActivity",
    "ItineraryRequest",
    "ItineraryResponse",
    # Analytics models
    "UserBehavior",
    "SearchQuery",
    "DestinationTrend",
    "RecommendationScore",
    # Response models
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
    # Ranking models
    "Place",
    "PlaceType",
    "PriceRange",
    "RankingRequest",
    "RankedPlace",
    "RankingResponse",
    "ScoreBreakdown",
    "Coordinates",
]

"""
Analytics Models - User behavior and trend tracking
For ML-based recommendation and intelligence features
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class EventType(str, Enum):
    """User event types for tracking"""
    VIEW_DESTINATION = "view_destination"
    SEARCH = "search"
    ADD_WISHLIST = "add_wishlist"
    REMOVE_WISHLIST = "remove_wishlist"
    CREATE_ITINERARY = "create_itinerary"
    CHAT_INTERACTION = "chat_interaction"
    FILTER_APPLIED = "filter_applied"
    SHARE = "share"
    BOOKING_INTENT = "booking_intent"


class UserBehavior(BaseModel):
    """User behavior tracking for ML personalization"""
    user_id: str = Field(..., description="User identifier")
    event_type: EventType
    destination_id: Optional[int] = None
    search_query: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    duration_seconds: Optional[int] = Field(None, ge=0, description="Time spent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "event_type": "view_destination",
                "destination_id": 5,
                "session_id": "session_abc123",
                "duration_seconds": 45,
                "timestamp": "2026-02-18T12:00:00"
            }
        }


class SearchQuery(BaseModel):
    """Search query tracking for trend analysis"""
    query: str = Field(..., min_length=1, max_length=200)
    user_id: Optional[str] = None
    results_count: int = Field(default=0, ge=0)
    clicked_results: List[int] = Field(default_factory=list, description="Clicked destination IDs")
    filters_applied: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    

class DestinationTrend(BaseModel):
    """Destination popularity trends over time"""
    destination_id: int
    destination_name: str
    time_period: str = Field(..., description="Period (day, week, month)")
    views: int = Field(default=0, ge=0)
    searches: int = Field(default=0, ge=0)
    wishlists_added: int = Field(default=0, ge=0)
    itineraries_created: int = Field(default=0, ge=0)
    popularity_change: float = Field(default=0.0, description="% change from previous period")
    trending_score: float = Field(default=0.0, ge=0, le=100)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class RecommendationScore(BaseModel):
    """ML-based recommendation score"""
    destination_id: int
    user_id: str
    score: float = Field(..., ge=0, le=100, description="Recommendation confidence (0-100)")
    reasons: List[str] = Field(default_factory=list, description="Why recommended")
    factors: Dict[str, float] = Field(
        default_factory=dict,
        description="Factor weights (preference_match, price_fit, etc.)"
    )
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "destination_id": 10,
                "user_id": "user_123",
                "score": 87.5,
                "reasons": [
                    "Matches your interest in culture",
                    "Within your budget range",
                    "Popular in your age group"
                ],
                "factors": {
                    "preference_match": 0.35,
                    "price_fit": 0.25,
                    "popularity": 0.20,
                    "seasonal": 0.20
                }
            }
        }


class PriceOptimization(BaseModel):
    """Price optimization suggestions"""
    destination_id: int
    current_price: float
    optimal_price: float
    potential_demand_increase: float = Field(..., ge=0, description="% demand increase")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level (0-1)")
    factors: Dict[str, Any] = Field(default_factory=dict)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class UserSegment(BaseModel):
    """User segmentation for targeted marketing"""
    segment_id: str
    name: str = Field(..., description="Segment name (e.g., 'Budget Backpackers')")
    description: str
    characteristics: Dict[str, Any] = Field(default_factory=dict)
    user_count: int = Field(default=0, ge=0)
    average_budget: float = Field(default=0.0, ge=0)
    top_destinations: List[int] = Field(default_factory=list)
    top_interests: List[str] = Field(default_factory=list)


class SystemMetrics(BaseModel):
    """Overall system performance metrics"""
    total_users: int = Field(default=0, ge=0)
    active_users_today: int = Field(default=0, ge=0)
    total_destinations: int = Field(default=0, ge=0)
    total_searches: int = Field(default=0, ge=0)
    total_itineraries: int = Field(default=0, ge=0)
    total_wishlists: int = Field(default=0, ge=0)
    average_session_duration: float = Field(default=0.0, ge=0)
    top_destinations: List[Dict[str, Any]] = Field(default_factory=list)
    top_searches: List[Dict[str, Any]] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class ABTestResult(BaseModel):
    """A/B testing results"""
    test_id: str
    variant_a: str
    variant_b: str
    metric: str = Field(..., description="Measured metric")
    variant_a_value: float
    variant_b_value: float
    improvement_percentage: float
    sample_size_a: int = Field(..., ge=0)
    sample_size_b: int = Field(..., ge=0)
    confidence_level: float = Field(..., ge=0, le=1)
    is_significant: bool

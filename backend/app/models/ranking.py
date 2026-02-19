"""
Ranking Models - Multi-criteria place ranking system
For hotels, cafes, and restaurants with weighted scoring
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class PlaceType(str, Enum):
    """Types of places that can be ranked"""
    HOTEL = "hotel"
    CAFE = "cafe"
    RESTAURANT = "restaurant"


class PriceRange(str, Enum):
    """Price range categories"""
    BUDGET = "budget"           # $
    MODERATE = "moderate"       # $$
    EXPENSIVE = "expensive"     # $$$
    LUXURY = "luxury"          # $$$$


class Place(BaseModel):
    """
    Place entity with all attributes needed for ranking
    """
    id: str = Field(..., description="Unique place identifier")
    name: str = Field(..., min_length=1, max_length=200)
    place_type: PlaceType
    
    # Ranking criteria
    rating: float = Field(..., ge=0.0, le=5.0, description="User rating (0-5)")
    price_range: PriceRange = Field(..., description="Price category")
    average_price: float = Field(..., ge=0, description="Average price per person/night")
    
    # Location
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str = Field(default="", max_length=500)
    city: str = Field(..., max_length=100)
    
    # Popularity metrics
    review_count: int = Field(default=0, ge=0, description="Total number of reviews")
    popularity_score: float = Field(default=0.0, ge=0.0, le=100.0, description="Normalized popularity (0-100)")
    
    # Student-friendly indicators
    student_discount: bool = Field(default=False, description="Offers student discount")
    wifi_available: bool = Field(default=False, description="Free WiFi available")
    study_friendly: bool = Field(default=False, description="Good for studying/working")
    wallet_friendly: bool = Field(default=False, description="Budget-friendly options")
    
    # Additional metadata
    cuisine_type: Optional[str] = Field(None, max_length=100, description="For restaurants/cafes")
    amenities: List[str] = Field(default_factory=list, description="Available amenities")
    opening_hours: Optional[str] = Field(None, max_length=200)
    image_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "cafe_001",
                "name": "The Study Corner Cafe",
                "place_type": "cafe",
                "rating": 4.5,
                "price_range": "moderate",
                "average_price": 12.50,
                "latitude": 40.7128,
                "longitude": -74.0060,
                "address": "123 Student St",
                "city": "New York",
                "review_count": 250,
                "popularity_score": 75.5,
                "student_discount": True,
                "wifi_available": True,
                "study_friendly": True,
                "wallet_friendly": True,
                "cuisine_type": "Coffee & Pastries",
                "amenities": ["WiFi", "Power Outlets", "Quiet Space"]
            }
        }


class Coordinates(BaseModel):
    """User's current location or search location"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class RankingRequest(BaseModel):
    """
    Request for ranked place recommendations
    """
    # User context
    user_budget: float = Field(..., gt=0, description="Maximum budget per person/night")
    user_location: Coordinates = Field(..., description="User's current location or search center")
    
    # Filters
    place_types: List[PlaceType] = Field(
        default_factory=lambda: [PlaceType.HOTEL, PlaceType.CAFE, PlaceType.RESTAURANT],
        description="Types of places to include in ranking"
    )
    max_distance_km: Optional[float] = Field(
        default=10.0,
        gt=0,
        le=100,
        description="Maximum distance from user location (km)"
    )
    min_rating: Optional[float] = Field(
        default=0.0,
        ge=0.0,
        le=5.0,
        description="Minimum rating filter"
    )
    student_friendly_only: bool = Field(
        default=False,
        description="Filter for student-friendly places only"
    )
    
    # Pagination
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results to return"
    )
    
    # Optional parameters
    preferred_cuisine: Optional[str] = Field(None, max_length=100)
    required_amenities: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_budget": 50.0,
                "user_location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                "place_types": ["cafe", "restaurant"],
                "max_distance_km": 5.0,
                "min_rating": 3.5,
                "student_friendly_only": True,
                "limit": 10
            }
        }


class ScoreBreakdown(BaseModel):
    """
    Detailed breakdown of how the final score was calculated
    """
    rating_score: float = Field(..., ge=0.0, le=1.0, description="Rating component (0-1)")
    budget_match_score: float = Field(..., ge=0.0, le=1.0, description="Budget match component (0-1)")
    distance_score: float = Field(..., ge=0.0, le=1.0, description="Distance component (0-1)")
    popularity_score: float = Field(..., ge=0.0, le=1.0, description="Popularity component (0-1)")
    student_friendly_score: float = Field(..., ge=0.0, le=1.0, description="Student-friendly component (0-1)")
    
    # Weighted components
    weighted_rating: float = Field(..., description="0.4 × rating_score")
    weighted_budget: float = Field(..., description="0.25 × budget_match_score")
    weighted_distance: float = Field(..., description="0.2 × distance_score")
    weighted_popularity: float = Field(..., description="0.1 × popularity_score")
    weighted_student: float = Field(..., description="0.05 × student_friendly_score")
    
    total_score: float = Field(..., ge=0.0, le=1.0, description="Final weighted score (0-1)")


class RankedPlace(BaseModel):
    """
    Place with ranking score and explanation
    """
    place: Place = Field(..., description="The place details")
    score: float = Field(..., ge=0.0, le=100.0, description="Final ranking score (0-100)")
    rank: int = Field(..., ge=1, description="Rank position (1 = best)")
    distance_km: float = Field(..., ge=0.0, description="Distance from user location (km)")
    
    score_breakdown: ScoreBreakdown = Field(..., description="Detailed score components")
    
    # Explanations
    match_reasons: List[str] = Field(
        default_factory=list,
        description="Reasons why this place matches user preferences"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Potential concerns (e.g., over budget, far distance)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "rank": 1,
                "score": 85.5,
                "distance_km": 1.2,
                "match_reasons": [
                    "Excellent rating (4.5/5)",
                    "Within budget ($12.50 vs $50.00)",
                    "Student discount available",
                    "Very close (1.2 km)"
                ],
                "warnings": []
            }
        }


class RankingResponse(BaseModel):
    """
    Response with ranked places
    """
    places: List[RankedPlace] = Field(..., description="Ranked list of places")
    total_candidates: int = Field(..., ge=0, description="Total places evaluated before filtering")
    filters_applied: Dict[str, Any] = Field(..., description="Summary of filters applied")
    search_location: Coordinates = Field(..., description="Center point of search")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "places": [],  # List of RankedPlace objects
                "total_candidates": 45,
                "filters_applied": {
                    "place_types": ["cafe", "restaurant"],
                    "max_distance_km": 5.0,
                    "min_rating": 3.5,
                    "user_budget": 50.0
                },
                "search_location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                "timestamp": "2026-02-18T12:00:00"
            }
        }

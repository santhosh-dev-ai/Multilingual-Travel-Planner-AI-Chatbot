"""
Content-Based Recommendation Models
Pydantic models for destination recommendation API
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class TravelType(str, Enum):
    """Travel type preferences"""
    ADVENTURE = "adventure"
    BEACH = "beach"
    CULTURAL = "cultural"
    FOODIE = "foodie"
    SHOPPING = "shopping"
    NATURE = "nature"
    LUXURY = "luxury"
    URBAN = "urban"
    RELAXATION = "relaxation"


class Mood(str, Enum):
    """User mood/travel style"""
    RELAXED = "relaxed"
    ENERGETIC = "energetic"
    ROMANTIC = "romantic"
    FAMILY = "family"
    SOLO = "solo"


class BudgetCategory(str, Enum):
    """Budget categories"""
    BUDGET = "budget"
    MODERATE = "moderate"
    LUXURY = "luxury"


class RecommendationRequest(BaseModel):
    """Request model for destination recommendations"""
    
    budget: Optional[BudgetCategory] = Field(
        None,
        description="Budget category: budget (<$2000), moderate ($2000-$3500), luxury (>$3500)"
    )
    max_budget: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum budget in USD (overrides budget category)"
    )
    duration: Optional[int] = Field(
        None,
        ge=1,
        le=365,
        description="Trip duration in days"
    )
    travel_type: TravelType = Field(
        TravelType.CULTURAL,
        description="Type of travel experience desired"
    )
    mood: Mood = Field(
        Mood.RELAXED,
        description="Travel mood/style"
    )
    top_n: int = Field(
        5,
        ge=1,
        le=20,
        description="Number of recommendations to return"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "budget": "moderate",
                "duration": 7,
                "travel_type": "beach",
                "mood": "relaxed",
                "top_n": 5
            }
        }


class RecommendedDestination(BaseModel):
    """Single recommended destination with similarity score"""
    
    id: int = Field(..., description="Destination ID")
    name: str = Field(..., description="Destination name")
    country: str = Field(..., description="Country")
    region: str = Field(..., description="Geographic region")
    description: str = Field(..., description="Destination description")
    estimated_budget: int = Field(..., description="Estimated budget in USD")
    best_time_to_visit: str = Field(..., description="Best time to visit")
    popular_activities: List[str] = Field(..., description="Popular activities")
    climate: str = Field(..., description="Climate type")
    rating: float = Field(..., ge=0, le=5, description="User rating (0-5)")
    image_url: str = Field(..., description="Destination image URL")
    
    # Explainability fields
    similarity_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Cosine similarity score (0-1)"
    )
    similarity_percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Similarity as percentage (0-100%)"
    )
    match_reason: str = Field(
        ...,
        description="Human-readable explanation of why this destination matches"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 3,
                "name": "Bali",
                "country": "Indonesia",
                "region": "asia",
                "description": "Tropical paradise with stunning beaches",
                "estimated_budget": 1500,
                "best_time_to_visit": "April-October",
                "popular_activities": ["Beaches", "Surfing", "Temples", "Yoga"],
                "climate": "tropical",
                "rating": 4.9,
                "image_url": "https://example.com/bali.jpg",
                "similarity_score": 0.78,
                "similarity_percentage": 78.0,
                "match_reason": "This destination matches your beach interest, suits relaxed mood, highly rated (4.9/5)."
            }
        }


class RecommendationResponse(BaseModel):
    """Response model for destination recommendations"""
    
    success: bool = Field(True, description="Request success status")
    message: str = Field("Recommendations generated successfully")
    query_summary: dict = Field(
        ...,
        description="Summary of user query parameters"
    )
    recommendations: List[RecommendedDestination] = Field(
        ...,
        description="List of recommended destinations"
    )
    total_found: int = Field(
        ...,
        ge=0,
        description="Total number of matching destinations"
    )
    algorithm: str = Field(
        "TF-IDF + Cosine Similarity",
        description="Recommendation algorithm used"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Recommendations generated successfully",
                "query_summary": {
                    "travel_type": "beach",
                    "mood": "relaxed",
                    "budget": "moderate",
                    "duration": 7
                },
                "recommendations": [
                    {
                        "id": 3,
                        "name": "Bali",
                        "country": "Indonesia",
                        "similarity_score": 0.78,
                        "similarity_percentage": 78.0
                    }
                ],
                "total_found": 5,
                "algorithm": "TF-IDF + Cosine Similarity"
            }
        }

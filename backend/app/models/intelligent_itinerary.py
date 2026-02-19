"""
Intelligent Itinerary Models
Request/Response models for comprehensive itinerary generation
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class TravelType(str, Enum):
    """Travel type preferences"""
    ADVENTURE = "adventure"
    BEACH = "beach"
    CULTURAL = "cultural"
    NATURE = "nature"
    URBAN = "urban"
    HISTORICAL = "historical"
    FOOD = "food"
    RELAXATION = "relaxation"


class Mood(str, Enum):
    """Traveler mood preferences"""
    RELAXED = "relaxed"
    ENERGETIC = "energetic"
    ROMANTIC = "romantic"
    ADVENTUROUS = "adventurous"
    CURIOUS = "curious"
    CONTEMPLATIVE = "contemplative"


# ============================================================================
# REQUEST MODELS
# ============================================================================

class IntelligentItineraryRequest(BaseModel):
    """
    Request for intelligent itinerary generation
    Integrates all AI systems: ranking, recommendations, budget, enrichment, routing
    """
    
    # Location
    location: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Destination name (city or region)",
        example="Paris"
    )
    
    latitude: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="Latitude for route optimization",
        example=48.8566
    )
    
    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="Longitude for route optimization",
        example=2.3522
    )
    
    # Budget & Group
    budget: float = Field(
        ...,
        gt=0,
        le=100000,
        description="Total budget in USD",
        example=1500
    )
    
    duration: int = Field(
        ...,
        ge=1,
        le=365,
        description="Trip duration in days",
        example=7
    )
    
    group_size: int = Field(
        ...,
        ge=1,
        le=50,
        description="Number of travelers",
        example=2
    )
    
    # Preferences
    mood: Mood = Field(
        default=Mood.RELAXED,
        description="Traveler mood/energy level"
    )
    
    travel_type: TravelType = Field(
        default=TravelType.CULTURAL,
        description="Primary travel interest"
    )
    
    # Optional filters
    include_hotels: bool = Field(
        default=True,
        description="Include hotel recommendations"
    )
    
    include_restaurants: bool = Field(
        default=True,
        description="Include restaurant recommendations"
    )
    
    include_enrichment: bool = Field(
        default=True,
        description="Include educational enrichment"
    )
    
    max_distance_km: float = Field(
        default=50.0,
        ge=1,
        le=500,
        description="Maximum distance for POIs (km)"
    )
    
    student_friendly: bool = Field(
        default=False,
        description="Prioritize student-friendly options"
    )
    
    custom_budget_allocation: Optional[Dict[str, float]] = Field(
        None,
        description="Custom budget allocation percentages"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "location": "Paris",
                "latitude": 48.8566,
                "longitude": 2.3522,
                "budget": 1500,
                "duration": 7,
                "group_size": 2,
                "mood": "cultural",
                "travel_type": "cultural",
                "include_hotels": True,
                "include_restaurants": True,
                "include_enrichment": True,
                "student_friendly": True
            }
        }


# ============================================================================
# RESPONSE SUB-MODELS
# ============================================================================

class RankedPlace(BaseModel):
    """Ranked place (hotel/restaurant/attraction)"""
    name: str
    place_type: str
    rating: float
    score: float
    rank: int
    distance_km: float
    price_level: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    student_friendly: bool = False
    why_recommended: Optional[str] = None


class RouteOptimization(BaseModel):
    """Optimized route for visiting places"""
    ordered_places: List[str] = Field(
        description="Place names in optimal visit order"
    )
    total_distance_km: float = Field(
        description="Total travel distance"
    )
    estimated_travel_time_hours: float = Field(
        description="Estimated travel time"
    )
    optimization_method: str = Field(
        description="Algorithm used (greedy, nearest_neighbor, etc.)"
    )


class BudgetBreakdown(BaseModel):
    """Detailed budget allocation"""
    total_budget: float
    duration_days: int
    group_size: int
    budget_tier: str
    per_person_per_day: float
    
    # Allocations
    stay_budget: float
    food_budget: float
    travel_budget: float
    activity_budget: float
    
    # Percentages
    allocation_percentages: Dict[str, float]
    
    # Per person
    per_person: Dict[str, float]
    
    # Per day
    per_day: Dict[str, float]
    
    # Suggestions
    suggestions: List[Dict[str, Any]]
    
    # Discounts
    group_discount_factor: float
    effective_stay_budget: float


class EducationalEnrichment(BaseModel):
    """Educational content and context"""
    destination: str
    country: str
    region: str
    
    historical_summary: str = Field(
        description="Brief historical overview"
    )
    
    cultural_insights: List[str] = Field(
        description="Cultural knowledge and etiquette"
    )
    
    travel_tips: List[str] = Field(
        description="Practical travel advice"
    )
    
    why_books_matter: str = Field(
        description="How reading enhances the experience"
    )


class BookRecommendation(BaseModel):
    """Recommended book about destination"""
    title: str
    author: str
    genre: str
    rating: float
    year_published: int
    pages: int
    description: str
    isbn: str
    student_friendly: bool
    educational_value: str
    why_recommended: Optional[str] = None


class DayItinerary(BaseModel):
    """Single day in itinerary"""
    day: int
    title: str
    morning_activity: Optional[str] = None
    afternoon_activity: Optional[str] = None
    evening_activity: Optional[str] = None
    recommended_restaurant: Optional[str] = None
    budget_estimate: Optional[float] = None
    notes: Optional[str] = None


# ============================================================================
# MAIN RESPONSE MODEL
# ============================================================================

class IntelligentItineraryResponse(BaseModel):
    """
    Comprehensive intelligent itinerary response
    Integrates all subsystems
    """
    
    success: bool = Field(
        default=True,
        description="Operation success status"
    )
    
    message: str = Field(
        default="Intelligent itinerary generated successfully",
        description="Status message"
    )
    
    # Basic Info
    location: str
    duration_days: int
    group_size: int
    
    # Optimized Itinerary
    optimized_itinerary: List[DayItinerary] = Field(
        description="Day-by-day itinerary with activities"
    )
    
    # Rankings
    ranked_hotels: List[RankedPlace] = Field(
        default=[],
        description="Top recommended hotels"
    )
    
    ranked_restaurants: List[RankedPlace] = Field(
        default=[],
        description="Top recommended restaurants"
    )
    
    ranked_attractions: List[RankedPlace] = Field(
        default=[],
        description="Top attractions to visit"
    )
    
    # Route Optimization
    route_order: RouteOptimization = Field(
        description="Optimal route through places"
    )
    
    # Budget
    budget_breakdown: BudgetBreakdown = Field(
        description="Detailed budget allocation"
    )
    
    # Educational Content
    educational_enrichment: Optional[EducationalEnrichment] = Field(
        None,
        description="Historical and cultural context"
    )
    
    recommended_books: List[BookRecommendation] = Field(
        default=[],
        description="Books about the destination"
    )
    
    # Recommendations
    alternative_destinations: List[Dict[str, Any]] = Field(
        default=[],
        description="Similar destinations to consider"
    )
    
    # Metadata
    generation_time_seconds: float = Field(
        description="Time taken to generate itinerary"
    )
    
    included_features: List[str] = Field(
        description="Features included in this response"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Intelligent itinerary generated successfully",
                "location": "Paris",
                "duration_days": 7,
                "group_size": 2,
                "optimized_itinerary": [
                    {
                        "day": 1,
                        "title": "Iconic Landmarks",
                        "morning_activity": "Eiffel Tower",
                        "afternoon_activity": "Louvre Museum",
                        "evening_activity": "Seine River Cruise",
                        "recommended_restaurant": "Le Comptoir du Relais",
                        "budget_estimate": 120,
                        "notes": "Book Louvre tickets online"
                    }
                ],
                "ranked_hotels": [
                    {
                        "name": "Hotel Le Marais",
                        "place_type": "hotel",
                        "rating": 4.5,
                        "score": 0.92,
                        "rank": 1,
                        "distance_km": 2.3,
                        "student_friendly": True
                    }
                ],
                "budget_breakdown": {
                    "total_budget": 1500,
                    "budget_tier": "moderate",
                    "stay_budget": 600,
                    "food_budget": 450
                },
                "generation_time_seconds": 2.45
            }
        }

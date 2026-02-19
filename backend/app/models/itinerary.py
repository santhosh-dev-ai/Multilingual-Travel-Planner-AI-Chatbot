"""
Itinerary Models - Enhanced trip planning structures
Production-ready with validation and optimization features
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, time
from pydantic import BaseModel, Field, validator
from enum import Enum


class TravelPace(str, Enum):
    """Travel pace/style"""
    RELAXED = "relaxed"
    BALANCED = "balanced"
    PACKED = "packed"


class BudgetLevel(str, Enum):
    """Budget categories"""
    BUDGET = "budget"
    MODERATE = "moderate"
    LUXURY = "luxury"


class ActivityCategory(str, Enum):
    """Activity types"""
    SIGHTSEEING = "sightseeing"
    ADVENTURE = "adventure"
    FOOD = "food"
    CULTURE = "culture"
    RELAXATION = "relaxation"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    NATURE = "nature"


class ItineraryActivity(BaseModel):
    """Single activity in itinerary"""
    time: str = Field(..., description="Activity time (e.g., '09:00 AM')")
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=1000)
    location: str = Field(..., description="Specific location/address")
    duration: str = Field(..., description="Duration (e.g., '2 hours')")
    category: Optional[ActivityCategory] = None
    cost: Optional[str] = Field(None, description="Cost estimate")
    cost_value: Optional[float] = Field(None, ge=0, description="Numeric cost")
    tips: Optional[str] = Field(None, description="Insider tips")
    booking_required: bool = False
    booking_url: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "time": "09:00 AM",
                "title": "Eiffel Tower Visit",
                "description": "Visit the iconic Eiffel Tower and enjoy panoramic views",
                "location": "Champ de Mars, Paris",
                "duration": "2 hours",
                "category": "sightseeing",
                "cost": "$28",
                "cost_value": 28.0,
                "tips": "Book tickets online to skip queues"
            }
        }


class ItineraryDay(BaseModel):
    """Single day in itinerary"""
    day: int = Field(..., ge=1, description="Day number")
    date: Optional[str] = Field(None, description="Actual date if known")
    title: str = Field(..., description="Day theme/title")
    activities: List[ItineraryActivity] = Field(..., min_items=1)
    meals: Optional[Dict[str, str]] = Field(
        None,
        description="Meal recommendations (breakfast, lunch, dinner)"
    )
    accommodation: Optional[str] = None
    notes: Optional[str] = Field(None, description="Special notes for the day")
    total_cost: Optional[float] = Field(None, ge=0, description="Total day cost")
    weather_note: Optional[str] = None
    
    @validator('meals')
    def validate_meals(cls, v):
        if v:
            valid_keys = {'breakfast', 'lunch', 'dinner', 'snacks'}
            invalid = set(v.keys()) - valid_keys
            if invalid:
                raise ValueError(f"Invalid meal keys: {invalid}")
        return v


class ItineraryRequest(BaseModel):
    """Request to generate an itinerary"""
    destination: str = Field(..., min_length=2, max_length=100)
    duration: int = Field(..., ge=1, le=30, description="Trip duration in days")
    interests: List[str] = Field(..., min_items=1, max_items=10, description="User interests")
    budget: BudgetLevel = BudgetLevel.MODERATE
    travel_style: TravelPace = TravelPace.BALANCED
    start_date: Optional[str] = Field(None, description="Trip start date (YYYY-MM-DD)")
    group_size: int = Field(default=1, ge=1, le=50, description="Number of travelers")
    accessibility_needs: List[str] = Field(default_factory=list)
    include_meals: bool = True
    include_accommodation: bool = True
    language: str = Field(default="en-US", description="Response language")
    user_id: Optional[str] = None
    
    @validator('interests')
    def validate_interests(cls, v):
        valid_interests = [
            'culture', 'adventure', 'food', 'beach', 'nature', 'history',
            'shopping', 'nightlife', 'relaxation', 'photography', 'sports',
            'art', 'music', 'architecture', 'wildlife', 'spiritual'
        ]
        invalid = [i for i in v if i.lower() not in valid_interests]
        if invalid:
            raise ValueError(f"Invalid interests: {invalid}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "destination": "Paris",
                "duration": 5,
                "interests": ["culture", "food", "history"],
                "budget": "moderate",
                "travel_style": "balanced",
                "group_size": 2,
                "language": "en-US"
            }
        }


class ItineraryBase(BaseModel):
    """Base itinerary fields"""
    destination: str = Field(..., description="Destination name")
    destination_country: Optional[str] = None
    duration: int = Field(..., ge=1)
    summary: str = Field(..., description="Trip summary")
    travel_style: TravelPace
    budget: BudgetLevel


class Itinerary(ItineraryBase):
    """Complete itinerary response"""
    id: Optional[str] = None
    user_id: Optional[str] = None
    days: List[ItineraryDay] = Field(..., min_items=1)
    budget_estimate: str = Field(..., description="Total budget breakdown")
    packing_tips: List[str] = Field(default_factory=list)
    local_phrases: List[Dict[str, str]] = Field(default_factory=list)
    important_contacts: Optional[Dict[str, str]] = None
    emergency_info: Optional[Dict[str, Any]] = None
    total_estimated_cost: Optional[float] = Field(None, ge=0)
    optimization_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="How well optimized (0-100)"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "destination": "Paris",
                "duration": 3,
                "summary": "A perfect 3-day cultural journey through Paris",
                "travel_style": "balanced",
                "budget": "moderate",
                "days": [],
                "budget_estimate": "Total: $900-$1200",
                "packing_tips": ["Comfortable walking shoes", "Light jacket"],
                "total_estimated_cost": 1050.0
            }
        }


class ItineraryResponse(BaseModel):
    """API response with itinerary"""
    success: bool = True
    message: str = "Itinerary generated successfully"
    itinerary: Itinerary
    alternatives: Optional[List[Itinerary]] = Field(
        None,
        description="Alternative itinerary suggestions"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ItineraryOptimization(BaseModel):
    """Itinerary optimization suggestions"""
    original_cost: float
    optimized_cost: float
    savings: float = Field(..., ge=0)
    savings_percentage: float = Field(..., ge=0)
    suggestions: List[str] = Field(..., description="Optimization suggestions")
    alternative_activities: List[Dict[str, Any]] = Field(default_factory=list)
    better_timing: Optional[Dict[int, str]] = Field(
        None,
        description="Better times for activities (day -> suggestion)"
    )

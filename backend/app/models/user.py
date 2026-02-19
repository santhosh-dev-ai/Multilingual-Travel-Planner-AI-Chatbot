"""
User Models - Production-grade user management
Includes profiles, preferences, and authentication
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum


class TravelStyle(str, Enum):
    """User travel style preferences"""
    BUDGET = "budget"
    MODERATE = "moderate"
    LUXURY = "luxury"
    BACKPACKER = "backpacker"
    BUSINESS = "business"


class UserRole(str, Enum):
    """User role types"""
    STUDENT = "student"
    PROFESSIONAL = "professional"
    FAMILY = "family"
    SOLO = "solo"
    GROUP = "group"


class UserPreferences(BaseModel):
    """User travel preferences for ML personalization"""
    favorite_regions: List[str] = Field(default_factory=list, description="Preferred regions")
    favorite_climates: List[str] = Field(default_factory=list, description="Preferred climates")
    interests: List[str] = Field(default_factory=list, description="Travel interests (culture, adventure, etc.)")
    budget_range: Dict[str, int] = Field(default_factory=dict, description="Min/max budget per trip")
    travel_style: TravelStyle = TravelStyle.MODERATE
    preferred_duration: int = Field(default=7, ge=1, le=365, description="Preferred trip duration in days")
    language_preference: str = Field(default="en-US", description="Preferred language")
    accessibility_needs: List[str] = Field(default_factory=list, description="Accessibility requirements")
    
    class Config:
        json_schema_extra = {
            "example": {
                "favorite_regions": ["europe", "asia"],
                "favorite_climates": ["mediterranean", "tropical"],
                "interests": ["culture", "food", "adventure"],
                "budget_range": {"min": 500, "max": 2000},
                "travel_style": "moderate",
                "preferred_duration": 7
            }
        }


class UserProfile(BaseModel):
    """Extended user profile with behavioral data"""
    user_id: str = Field(..., description="Unique user identifier")
    age_range: Optional[str] = Field(None, description="Age range (18-24, 25-34, etc.)")
    occupation: Optional[str] = None
    role: UserRole = UserRole.STUDENT
    home_country: Optional[str] = None
    currencies_used: List[str] = Field(default_factory=lambda: ["USD"])
    total_trips: int = Field(default=0, ge=0, description="Total trips planned")
    total_destinations: int = Field(default=0, ge=0, description="Total destinations explored")
    wishlist_count: int = Field(default=0, ge=0)
    average_budget: float = Field(default=0.0, ge=0, description="Average trip budget")
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('age_range')
    def validate_age_range(cls, v):
        valid_ranges = ["13-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
        if v and v not in valid_ranges:
            raise ValueError(f"Age range must be one of {valid_ranges}")
        return v


class User(BaseModel):
    """Core user model"""
    id: str = Field(..., description="Unique user ID")
    email: Optional[EmailStr] = None
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    profile: Optional[UserProfile] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_123",
                "email": "student@example.com",
                "username": "travel_student",
                "full_name": "John Doe",
                "is_active": True
            }
        }


class UserCreate(BaseModel):
    """User creation request"""
    email: Optional[EmailStr] = None
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    role: UserRole = UserRole.STUDENT
    preferences: Optional[UserPreferences] = None


class UserUpdate(BaseModel):
    """User update request (all fields optional)"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    preferences: Optional[UserPreferences] = None


class UserStats(BaseModel):
    """User statistics for dashboard"""
    total_trips: int = 0
    total_destinations: int = 0
    countries_visited: int = 0
    total_budget_spent: float = 0.0
    favorite_destination: Optional[str] = None
    most_visited_region: Optional[str] = None
    average_trip_duration: float = 0.0
    wishlist_count: int = 0

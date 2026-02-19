"""
Destination Models - Enhanced destination data structures
Includes metrics, popularity scores, and seasonal data
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator, HttpUrl
from enum import Enum


class Region(str, Enum):
    """Geographic regions"""
    EUROPE = "europe"
    ASIA = "asia"
    AMERICAS = "americas"
    AFRICA = "africa"
    OCEANIA = "oceania"
    MIDDLE_EAST = "middle_east"


class Climate(str, Enum):
    """Climate types"""
    TROPICAL = "tropical"
    MEDITERRANEAN = "mediterranean"
    CONTINENTAL = "continental"
    DESERT = "desert"
    ALPINE = "alpine"
    TEMPERATE = "temperate"
    SUBARCTIC = "subarctic"
    SAVANNA = "savanna"


class DestinationStatus(str, Enum):
    """Destination availability status"""
    ACTIVE = "active"
    SEASONAL = "seasonal"
    RESTRICTED = "restricted"
    COMING_SOON = "coming_soon"


class Coordinates(BaseModel):
    """Geographic coordinates"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")


class DestinationMetrics(BaseModel):
    """Real-time destination metrics for ranking"""
    popularity_score: float = Field(default=0.0, ge=0, le=100, description="Popularity (0-100)")
    search_count: int = Field(default=0, ge=0, description="Times searched")
    view_count: int = Field(default=0, ge=0, description="Profile views")
    wishlist_count: int = Field(default=0, ge=0, description="Times added to wishlist")
    booking_count: int = Field(default=0, ge=0, description="Itineraries created")
    rating: float = Field(default=4.5, ge=0, le=5, description="Average rating")
    reviews: int = Field(default=0, ge=0, description="Number of reviews")
    trending_rank: Optional[int] = Field(None, description="Current trending position")
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class SeasonalPricing(BaseModel):
    """Seasonal price variations"""
    season: str = Field(..., description="Season name (spring, summer, etc.)")
    months: List[str] = Field(..., description="Applicable months")
    price_multiplier: float = Field(default=1.0, ge=0.5, le=3.0, description="Price adjustment")
    description: str = Field(..., description="Season description")


class DestinationBase(BaseModel):
    """Base destination fields"""
    name: str = Field(..., min_length=2, max_length=100)
    country: str = Field(..., min_length=2, max_length=100)
    region: Region
    description: str = Field(..., min_length=10, max_length=500, description="Short description")
    full_description: str = Field(..., min_length=50, max_length=2000, description="Detailed description")


class Destination(DestinationBase):
    """Complete destination model"""
    id: int = Field(..., description="Unique destination ID")
    image: HttpUrl = Field(..., description="Main destination image URL")
    image_gallery: List[HttpUrl] = Field(default_factory=list, description="Additional images")
    
    # Pricing
    price: str = Field(..., description="Display price (e.g., '$1,200')")
    price_value: int = Field(..., ge=0, description="Numeric price for calculations")
    price_currency: str = Field(default="USD")
    student_discount: Optional[float] = Field(None, ge=0, le=100, description="Student discount %")
    
    # Travel info
    duration: str = Field(..., description="Recommended duration (e.g., '5-7 days')")
    best_time_to_visit: str = Field(..., description="Best months to visit")
    climate: Climate
    coordinates: Optional[Coordinates] = None
    
    # Features
    highlights: List[str] = Field(..., min_items=1, max_items=10, description="Key attractions")
    tags: List[str] = Field(..., min_items=1, max_items=8, description="Category tags")
    activities: List[str] = Field(default_factory=list, description="Available activities")
    accommodation_types: List[str] = Field(default_factory=list, description="Housing options")
    
    # Badges & status
    badge: Optional[str] = None
    status: DestinationStatus = DestinationStatus.ACTIVE
    is_featured: bool = False
    is_budget_friendly: bool = False
    
    # Metrics
    metrics: DestinationMetrics = Field(default_factory=DestinationMetrics)
    
    # Seasonal data
    seasonal_pricing: List[SeasonalPricing] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Santorini",
                "country": "Greece",
                "region": "europe",
                "description": "Beautiful Greek island with stunning sunsets",
                "full_description": "Santorini is one of the most beautiful islands...",
                "image": "https://example.com/santorini.jpg",
                "price": "$1,200",
                "price_value": 1200,
                "duration": "5-7 days",
                "best_time_to_visit": "Apr - Oct",
                "climate": "mediterranean",
                "highlights": ["Oia sunset", "White villages", "Wine tasting"],
                "tags": ["romantic", "beach", "culture"]
            }
        }


class DestinationDetail(Destination):
    """Extended destination with additional details"""
    local_language: Optional[str] = None
    currency_info: Optional[Dict[str, Any]] = None
    visa_requirements: Optional[Dict[str, str]] = None
    safety_rating: Optional[float] = Field(None, ge=0, le=10)
    accessibility_score: Optional[float] = Field(None, ge=0, le=10)
    
    # Transportation
    flight_info: Optional[Dict[str, Any]] = None
    local_transport: List[str] = Field(default_factory=list)
    
    # Cost breakdown
    average_costs: Optional[Dict[str, float]] = Field(
        None,
        description="Average costs (accommodation, food, activities, transport)"
    )
    
    # Similar destinations
    similar_destinations: List[int] = Field(default_factory=list, description="Similar destination IDs")


class DestinationCreate(DestinationBase):
    """Destination creation request"""
    image: HttpUrl
    price_value: int = Field(..., ge=0)
    duration: str
    best_time_to_visit: str
    climate: Climate
    highlights: List[str] = Field(..., min_items=1)
    tags: List[str] = Field(..., min_items=1)
    coordinates: Optional[Coordinates] = None
    student_discount: Optional[float] = Field(None, ge=0, le=100)


class DestinationUpdate(BaseModel):
    """Destination update request (all fields optional)"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    full_description: Optional[str] = None
    price_value: Optional[int] = Field(None, ge=0)
    highlights: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[DestinationStatus] = None
    is_featured: Optional[bool] = None


class DestinationFilter(BaseModel):
    """Destination filtering options"""
    region: Optional[Region] = None
    climate: Optional[Climate] = None
    min_price: Optional[int] = Field(None, ge=0)
    max_price: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    budget_friendly: Optional[bool] = None
    featured: Optional[bool] = None
    sort_by: str = Field(default="popularity", description="Sort field")
    sort_order: str = Field(default="desc", description="asc or desc")
    
    @validator('sort_by')
    def validate_sort_field(cls, v):
        valid_fields = ["popularity", "price", "rating", "trending", "name"]
        if v not in valid_fields:
            raise ValueError(f"sort_by must be one of {valid_fields}")
        return v

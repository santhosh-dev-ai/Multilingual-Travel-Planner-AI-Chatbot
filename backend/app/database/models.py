"""Pydantic models for database entities."""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


# ============== Wishlist Models ==============

class WishlistItemCreate(BaseModel):
    """Model for creating a new wishlist item."""
    user_id: str = Field(..., description="User identifier")
    destination_id: int = Field(..., description="Destination ID")
    destination_name: str = Field(..., description="Name of the destination")
    destination_country: str = Field(..., description="Country of the destination")
    destination_image: Optional[str] = Field(None, description="Image URL")
    destination_price: Optional[str] = Field(None, description="Price range")
    destination_rating: Optional[float] = Field(None, description="Rating")


class WishlistItem(WishlistItemCreate):
    """Model for wishlist item from database."""
    id: str = Field(..., description="Unique wishlist item ID")
    created_at: datetime = Field(..., description="When the item was added")


class WishlistResponse(BaseModel):
    """Response model for wishlist operations."""
    success: bool
    message: str
    data: Optional[List[WishlistItem]] = None


# ============== Itinerary Models ==============

class ItineraryActivity(BaseModel):
    """Model for a single activity in an itinerary day."""
    time: str
    title: str
    location: str
    description: str
    cost: Optional[str] = None
    tips: Optional[str] = None
    duration: Optional[str] = None


class ItineraryDay(BaseModel):
    """Model for a single day in an itinerary."""
    day: int
    title: str
    activities: List[ItineraryActivity]
    meals: Optional[dict] = None
    notes: Optional[str] = None


class ItineraryCreate(BaseModel):
    """Model for creating a new itinerary."""
    user_id: str = Field(..., description="User identifier")
    destination: str = Field(..., description="Destination name")
    destination_country: Optional[str] = Field(None, description="Country")
    duration: int = Field(..., description="Number of days")
    travel_style: str = Field(default="balanced", description="relaxed, balanced, or packed")
    budget: str = Field(default="moderate", description="budget, moderate, or luxury")
    summary: Optional[str] = Field(None, description="Itinerary summary")
    days: List[ItineraryDay] = Field(..., description="Daily itinerary")
    budget_estimate: Optional[str] = Field(None, description="Estimated budget")
    packing_tips: Optional[List[str]] = Field(None, description="Packing recommendations")
    local_phrases: Optional[List[dict]] = Field(None, description="Useful local phrases")


class Itinerary(BaseModel):
    """Model for itinerary from database."""
    id: str = Field(..., description="Unique itinerary ID")
    user_id: str
    destination: str
    destination_country: Optional[str] = None
    duration: int
    travel_style: str
    budget: str
    summary: Optional[str] = None
    days: List[dict]  # Store as JSON
    budget_estimate: Optional[str] = None
    packing_tips: Optional[List[str]] = None
    local_phrases: Optional[List[dict]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ItineraryResponse(BaseModel):
    """Response model for itinerary operations."""
    success: bool
    message: str
    data: Optional[Any] = None

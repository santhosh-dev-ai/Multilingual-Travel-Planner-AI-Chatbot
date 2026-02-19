"""
Budget Allocation Models
Pydantic models for budget optimization API
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class BudgetRequest(BaseModel):
    """Request model for budget allocation"""
    
    total_budget: float = Field(
        ...,
        gt=0,
        description="Total budget in USD"
    )
    duration: int = Field(
        ...,
        ge=1,
        le=365,
        description="Trip duration in days"
    )
    group_size: int = Field(
        ...,
        ge=1,
        le=50,
        description="Number of people in the group"
    )
    custom_allocation: Optional[Dict[str, float]] = Field(
        None,
        description="Optional custom allocation percentages (must sum to 1.0)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_budget": 1500,
                "duration": 7,
                "group_size": 2,
                "custom_allocation": None
            }
        }


class BudgetSuggestion(BaseModel):
    """Single budget optimization suggestion"""
    
    category: str = Field(..., description="Suggestion category")
    priority: str = Field(..., description="Priority level: critical, high, medium, low")
    tip: str = Field(..., description="Suggestion text")
    savings_potential: str = Field(..., description="Savings potential: high, medium, low, n/a")
    alternatives: Optional[List[str]] = Field(None, description="Alternative options")
    free_activities: Optional[List[str]] = Field(None, description="Free activity suggestions")
    recommendation: Optional[str] = Field(None, description="Additional recommendation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "stay",
                "priority": "high",
                "tip": "Target hostels at $25/night per person",
                "savings_potential": "high",
                "alternatives": ["Hostels", "Couchsurfing", "Airbnb shared rooms"]
            }
        }


class PerPersonBreakdown(BaseModel):
    """Per-person budget breakdown"""
    
    stay: float = Field(..., description="Stay budget per person")
    food: float = Field(..., description="Food budget per person")
    travel: float = Field(..., description="Travel budget per person")
    activities: float = Field(..., description="Activities budget per person")


class DailyBreakdown(BaseModel):
    """Daily budget breakdown"""
    
    stay_per_night: float = Field(..., description="Stay budget per night")
    food_per_day: float = Field(..., description="Food budget per day")
    stay_per_person_per_night: float = Field(..., description="Stay budget per person per night")
    food_per_person_per_day: float = Field(..., description="Food budget per person per day")


class AllocationPercentages(BaseModel):
    """Budget allocation percentages"""
    
    stay: float = Field(..., ge=0, le=100, description="Stay allocation percentage")
    food: float = Field(..., ge=0, le=100, description="Food allocation percentage")
    travel: float = Field(..., ge=0, le=100, description="Travel allocation percentage")
    activities: float = Field(..., ge=0, le=100, description="Activities allocation percentage")


class BudgetResponse(BaseModel):
    """Response model for budget allocation"""
    
    success: bool = Field(True, description="Request success status")
    message: str = Field("Budget optimized successfully")
    
    # Overview
    total_budget: float = Field(..., description="Total budget in USD")
    duration_days: int = Field(..., description="Trip duration in days")
    group_size: int = Field(..., description="Number of people")
    budget_tier: str = Field(
        ...,
        description="Budget tier: ultra_low, low, moderate, comfortable, high"
    )
    per_person_total: float = Field(..., description="Total budget per person")
    per_person_per_day: float = Field(..., description="Budget per person per day")
    
    # Category allocations
    stay_budget: float = Field(..., description="Total budget for accommodations")
    food_budget: float = Field(..., description="Total budget for food")
    travel_budget: float = Field(..., description="Total budget for transportation")
    activity_budget: float = Field(..., description="Total budget for activities")
    
    # Percentages
    allocation_percentages: AllocationPercentages = Field(
        ...,
        description="Allocation percentages by category"
    )
    
    # Breakdowns
    per_person: PerPersonBreakdown = Field(..., description="Per-person breakdown")
    per_day: DailyBreakdown = Field(..., description="Daily breakdown")
    
    # Group factors
    group_discount_factor: float = Field(..., description="Group discount factor applied")
    effective_stay_budget: float = Field(
        ...,
        description="Effective stay budget after group discount"
    )
    
    # Suggestions
    suggestions: List[BudgetSuggestion] = Field(
        ...,
        description="Budget optimization suggestions"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Budget optimized successfully",
                "total_budget": 1500,
                "duration_days": 7,
                "group_size": 2,
                "budget_tier": "moderate",
                "per_person_total": 750,
                "per_person_per_day": 107.14,
                "stay_budget": 600,
                "food_budget": 450,
                "travel_budget": 300,
                "activity_budget": 150,
                "allocation_percentages": {
                    "stay": 40,
                    "food": 30,
                    "travel": 20,
                    "activities": 10
                },
                "per_person": {
                    "stay": 300,
                    "food": 225,
                    "travel": 150,
                    "activities": 75
                },
                "per_day": {
                    "stay_per_night": 85.71,
                    "food_per_day": 64.29,
                    "stay_per_person_per_night": 42.86,
                    "food_per_person_per_day": 32.14
                },
                "group_discount_factor": 0.95,
                "effective_stay_budget": 631.58,
                "suggestions": [
                    {
                        "category": "stay",
                        "priority": "medium",
                        "tip": "$42.86/night allows private rooms in mid-range hotels",
                        "savings_potential": "medium"
                    }
                ]
            }
        }

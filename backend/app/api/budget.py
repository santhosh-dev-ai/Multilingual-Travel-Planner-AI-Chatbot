"""
Budget Optimization API
FastAPI endpoint for student-focused budget allocation
"""

from fastapi import APIRouter, HTTPException, status, Body
import logging

from app.models.budget import (
    BudgetRequest,
    BudgetResponse,
    BudgetSuggestion,
    PerPersonBreakdown,
    DailyBreakdown,
    AllocationPercentages
)
from app.services.budget import optimize_budget

# Initialize router
router = APIRouter(tags=["Budget Optimization"])

# Logging
logger = logging.getLogger(__name__)


# ============================================================================
# BUDGET OPTIMIZATION ENDPOINT
# ============================================================================

@router.post(
    "/budget",
    response_model=BudgetResponse,
    status_code=status.HTTP_200_OK,
    summary="Optimize budget allocation for student travel",
    description="""
    Student-focused budget allocation engine with dynamic optimization.
    
    **Features**:
    - Smart budget allocation by category (Stay: 40%, Food: 30%, Travel: 20%, Activities: 10%)
    - Budget tier detection (ultra_low, low, moderate, comfortable, high)
    - Per-person and per-day breakdowns
    - Group discount calculations (up to 25% for large groups)
    - Free/low-cost suggestions for tight budgets
    - Dynamic allocation adjustment based on budget level
    
    **Budget Tiers** (per person per day):
    - Ultra Low: < $30/day (hostels, street food, free attractions)
    - Low: $30-60/day (budget accommodations, self-catering)
    - Moderate: $60-100/day (mid-range hotels, restaurants)
    - Comfortable: $100-150/day (quality accommodations, experiences)
    - High: > $150/day (premium options, full flexibility)
    
    **Use Case**: Call when user plans a trip to get budget breakdown and optimization tips.
    """,
    responses={
        200: {
            "description": "Budget optimized successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Budget optimized successfully",
                        "total_budget": 1500,
                        "duration_days": 7,
                        "group_size": 2,
                        "budget_tier": "moderate",
                        "per_person_per_day": 107.14,
                        "stay_budget": 600,
                        "food_budget": 450,
                        "travel_budget": 300,
                        "activity_budget": 150,
                        "suggestions": [
                            {
                                "category": "general",
                                "priority": "high",
                                "tip": "Group of 2: Save 5% by sharing accommodations"
                            }
                        ]
                    }
                }
            }
        },
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"}
    }
)
async def optimize_budget_allocation(
    request: BudgetRequest = Body(
        ...,
        examples={
            "default": {
                "summary": "Sample budget optimization request",
                "value": {
                    "total_budget": 1500,
                    "duration": 7,
                    "group_size": 2
                }
            }
        }
    )
):
    """
    Optimize budget allocation for student travel
    
    Args:
        request: BudgetRequest with total_budget, duration, group_size
        
    Returns:
        BudgetResponse with complete breakdown and suggestions
        
    Example:
        ```python
        POST /api/optimize/budget
        {
            "total_budget": 1500,
            "duration": 7,
            "group_size": 2
        }
        ```
    """
    try:
        logger.info(
            f"[Budget API] Request received - "
            f"budget=${request.total_budget}, duration={request.duration} days, "
            f"group_size={request.group_size}"
        )
        
        # Validate inputs
        if request.total_budget <= 0:
            raise ValueError("Total budget must be greater than 0")
        
        if request.duration <= 0:
            raise ValueError("Duration must be at least 1 day")
        
        if request.group_size <= 0:
            raise ValueError("Group size must be at least 1 person")
        
        # Calculate per-person-per-day for logging
        per_person_per_day = request.total_budget / (request.duration * request.group_size)
        
        # Optimize budget
        result = optimize_budget(
            total_budget=request.total_budget,
            duration=request.duration,
            group_size=request.group_size,
            custom_allocation=request.custom_allocation
        )
        
        logger.info(
            f"[Budget API] Optimized budget - tier={result['budget_tier']}, "
            f"${per_person_per_day:.2f}/person/day, {len(result['suggestions'])} suggestions"
        )
        
        # Build response
        response = BudgetResponse(
            success=True,
            message="Budget optimized successfully",
            total_budget=result["total_budget"],
            duration_days=result["duration_days"],
            group_size=result["group_size"],
            budget_tier=result["budget_tier"],
            per_person_total=result["per_person_total"],
            per_person_per_day=result["per_person_per_day"],
            stay_budget=result["stay_budget"],
            food_budget=result["food_budget"],
            travel_budget=result["travel_budget"],
            activity_budget=result["activity_budget"],
            allocation_percentages=AllocationPercentages(**result["allocation_percentages"]),
            per_person=PerPersonBreakdown(**result["per_person"]),
            per_day=DailyBreakdown(**result["per_day"]),
            group_discount_factor=result["group_discount_factor"],
            effective_stay_budget=result["effective_stay_budget"],
            suggestions=[BudgetSuggestion(**sug) for sug in result["suggestions"]]
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"[Budget API] Invalid request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request parameters: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[Budget API] Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to optimize budget. Please try again later."
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get(
    "/budget/tiers",
    status_code=status.HTTP_200_OK,
    summary="Get budget tier information",
    description="Returns budget tier classifications and thresholds",
    response_model=dict
)
async def get_budget_tiers():
    """Get budget tier information"""
    return {
        "success": True,
        "tiers": {
            "ultra_low": {
                "threshold": "< $30/person/day",
                "description": "Very tight budget - hostels, street food, free attractions",
                "accommodation": "Hostel dorms, couchsurfing",
                "food": "Self-cooking, street food, markets",
                "activities": "Free walking tours, parks, beaches",
                "suitable_for": "Backpackers, budget travelers"
            },
            "low": {
                "threshold": "$30-60/person/day",
                "description": "Budget travel - basic accommodations, budget meals",
                "accommodation": "Budget hostels, shared rooms",
                "food": "Mix of cooking and cheap restaurants",
                "activities": "Mix of free and paid attractions",
                "suitable_for": "Students, budget-conscious travelers"
            },
            "moderate": {
                "threshold": "$60-100/person/day",
                "description": "Comfortable budget - mid-range hotels, restaurants",
                "accommodation": "Mid-range hotels, private Airbnb",
                "food": "Regular restaurants, occasional splurges",
                "activities": "Most paid attractions accessible",
                "suitable_for": "Most travelers, balanced experience"
            },
            "comfortable": {
                "threshold": "$100-150/person/day",
                "description": "Comfortable travel - quality accommodations, experiences",
                "accommodation": "Quality hotels, nice Airbnbs",
                "food": "Good restaurants, no budget concerns",
                "activities": "Premium experiences accessible",
                "suitable_for": "Comfort-focused travelers"
            },
            "high": {
                "threshold": "> $150/person/day",
                "description": "Premium travel - luxury options, full flexibility",
                "accommodation": "High-end hotels, boutique stays",
                "food": "Fine dining, no restrictions",
                "activities": "All experiences accessible",
                "suitable_for": "Luxury travelers, premium experiences"
            }
        },
        "note": "Tiers based on per-person-per-day spending"
    }


@router.get(
    "/budget/allocation-defaults",
    status_code=status.HTTP_200_OK,
    summary="Get default allocation percentages",
    description="Returns default budget allocation percentages by tier",
    response_model=dict
)
async def get_allocation_defaults():
    """Get default allocation percentages"""
    return {
        "success": True,
        "default": {
            "stay": 40,
            "food": 30,
            "travel": 20,
            "activities": 10
        },
        "by_tier": {
            "ultra_low": {
                "stay": 35,
                "food": 35,
                "travel": 20,
                "activities": 10,
                "rationale": "Lower stay % (cheap hostels), higher food % (self-cooking costs)"
            },
            "low": {
                "stay": 38,
                "food": 32,
                "travel": 20,
                "activities": 10,
                "rationale": "Slightly adjusted for budget accommodations"
            },
            "moderate": {
                "stay": 40,
                "food": 30,
                "travel": 20,
                "activities": 10,
                "rationale": "Balanced allocation for comfortable travel"
            },
            "comfortable": {
                "stay": 40,
                "food": 28,
                "travel": 18,
                "activities": 14,
                "rationale": "More activities budget, less food concern"
            },
            "high": {
                "stay": 42,
                "food": 25,
                "travel": 18,
                "activities": 15,
                "rationale": "Premium stays, flexible activities"
            }
        },
        "note": "Allocations automatically adjust based on budget tier"
    }


@router.post(
    "/budget/calculate-per-person",
    status_code=status.HTTP_200_OK,
    summary="Calculate per-person costs",
    description="Quick calculator for per-person and per-day costs",
    response_model=dict
)
async def calculate_per_person_costs(
    total_budget: float = Body(..., gt=0),
    duration: int = Body(..., ge=1),
    group_size: int = Body(..., ge=1)
):
    """Calculate per-person costs"""
    try:
        per_person_total = total_budget / group_size
        per_person_per_day = total_budget / (duration * group_size)
        total_per_day = total_budget / duration
        
        # Determine tier
        if per_person_per_day < 30:
            tier = "ultra_low"
        elif per_person_per_day < 60:
            tier = "low"
        elif per_person_per_day < 100:
            tier = "moderate"
        elif per_person_per_day < 150:
            tier = "comfortable"
        else:
            tier = "high"
        
        return {
            "success": True,
            "total_budget": total_budget,
            "duration_days": duration,
            "group_size": group_size,
            "per_person_total": round(per_person_total, 2),
            "per_person_per_day": round(per_person_per_day, 2),
            "total_per_day": round(total_per_day, 2),
            "budget_tier": tier
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get(
    "/budget/health",
    status_code=status.HTTP_200_OK,
    summary="Health check for budget service",
    response_model=dict
)
async def health_check():
    """Check if budget service is operational"""
    try:
        from app.services.budget import get_budget_allocator
        allocator = get_budget_allocator()
        
        return {
            "success": True,
            "status": "healthy",
            "service": "Budget Allocation Engine",
            "version": "1.0.0",
            "features": {
                "dynamic_allocation": True,
                "budget_tiers": 5,
                "group_discounts": True,
                "smart_suggestions": True,
                "custom_allocation": True
            },
            "tiers_available": ["ultra_low", "low", "moderate", "comfortable", "high"]
        }
    except Exception as e:
        logger.error(f"[Health Check] Service unhealthy: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Budget service unavailable: {str(e)}"
        )

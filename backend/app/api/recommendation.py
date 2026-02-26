"""
Content-Based Recommendation API
FastAPI endpoint for destination recommendations using TF-IDF and cosine similarity
"""

from fastapi import APIRouter, HTTPException, status, Body
from typing import Optional
import logging
import time

from app.models.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendedDestination,
    TravelType,
    Mood,
    BudgetCategory
)
from app.services.recommendation import get_recommendations

# Initialize router
router = APIRouter(tags=["Recommendations"])

# Logging
logger = logging.getLogger(__name__)


# ============================================================================
# RECOMMENDATION ENDPOINT
# ============================================================================

@router.post(
    "/destination",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get personalized destination recommendations",
    description="""
    Content-based recommendation system using TF-IDF and cosine similarity.
    
    **Algorithm**: 
    - TF-IDF vectorization of destination features (description, activities, climate, region)
    - Cosine similarity matching between user query and destinations
    - Budget filtering for performance optimization
    
    **Features**:
    - Explainable recommendations with similarity scores
    - Budget and duration filtering
    - Travel type and mood matching
    - Performance optimized with caching
    
    **Travel Types**: adventure, beach, cultural, foodie, shopping, nature, luxury, urban, relaxation
    
    **Moods**: relaxed, energetic, romantic, family, solo
    
    **Budget Categories**:
    - budget: < $2000
    - moderate: $2000 - $3500
    - luxury: > $3500
    """,
    responses={
        200: {
            "description": "Recommendations generated successfully",
            "content": {
                "application/json": {
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
                                "region": "asia",
                                "description": "Tropical paradise with stunning beaches",
                                "estimated_budget": 1500,
                                "best_time_to_visit": "April-October",
                                "popular_activities": ["Beaches", "Surfing", "Temples"],
                                "climate": "tropical",
                                "rating": 4.9,
                                "image_url": "https://example.com/bali.jpg",
                                "similarity_score": 0.78,
                                "similarity_percentage": 78.0,
                                "match_reason": "This destination matches your beach interest, suits relaxed mood."
                            }
                        ],
                        "total_found": 5,
                        "algorithm": "TF-IDF + Cosine Similarity"
                    }
                }
            }
        },
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"}
    }
)
async def recommend_destinations(
    request: RecommendationRequest = Body(
        ...,
        examples={
            "default": {
                "summary": "Sample destination recommendation request",
                "value": {
                    "budget": "moderate",
                    "duration": 7,
                    "travel_type": "beach",
                    "mood": "relaxed",
                    "top_n": 5
                }
            }
        }
    )
):
    """
    Get personalized destination recommendations based on user preferences
    
    Args:
        request: RecommendationRequest with user preferences
        
    Returns:
        RecommendationResponse with top N recommended destinations
        
    Example:
        ```python
        POST /api/recommend/destination
        {
            "budget": "moderate",
            "duration": 7,
            "travel_type": "beach",
            "mood": "relaxed",
            "top_n": 5
        }
        ```
    """
    try:
        start_time = time.time()
        
        logger.info(
            f"[Recommendation API] Request received - "
            f"travel_type={request.travel_type}, mood={request.mood}, "
            f"budget={request.budget}, duration={request.duration}"
        )
        
        # Get recommendations from service
        recommendations = get_recommendations(
            budget=request.budget.value if request.budget else None,
            duration=request.duration,
            travel_type=request.travel_type.value,
            mood=request.mood.value,
            max_budget=request.max_budget,
            top_n=request.top_n
        )
        
        # Calculate processing time
        processing_time = round((time.time() - start_time) * 1000, 2)  # ms
        
        logger.info(
            f"[Recommendation API] Generated {len(recommendations)} recommendations "
            f"in {processing_time}ms"
        )
        
        # Build response
        response = RecommendationResponse(
            success=True,
            message=f"Generated {len(recommendations)} personalized recommendations",
            query_summary={
                "travel_type": request.travel_type.value,
                "mood": request.mood.value,
                "budget": request.budget.value if request.budget else None,
                "max_budget": request.max_budget,
                "duration": request.duration,
                "top_n": request.top_n
            },
            recommendations=[
                RecommendedDestination(**rec) for rec in recommendations
            ],
            total_found=len(recommendations),
            algorithm="TF-IDF + Cosine Similarity"
        )
        
        return response
        
    except FileNotFoundError as e:
        logger.error(f"[Recommendation API] Dataset not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Destination dataset not found. Please ensure locations.csv exists."
        )
    except ValueError as e:
        logger.error(f"[Recommendation API] Invalid request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request parameters: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[Recommendation API] Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations. Please try again later."
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get(
    "/travel-types",
    status_code=status.HTTP_200_OK,
    summary="Get available travel types",
    description="Returns list of supported travel types for recommendations",
    response_model=dict
)
async def get_travel_types():
    """Get list of available travel types"""
    return {
        "success": True,
        "travel_types": [t.value for t in TravelType],
        "descriptions": {
            "adventure": "Hiking, trekking, outdoor sports, mountains",
            "beach": "Ocean, coast, tropical, swimming, surfing",
            "cultural": "History, museums, temples, architecture, art",
            "foodie": "Cuisine, restaurants, markets, culinary experiences",
            "shopping": "Markets, malls, luxury brands, local crafts",
            "nature": "Wildlife, parks, gardens, hiking, scenic outdoors",
            "luxury": "Upscale, premium, high-end, exclusive experiences",
            "urban": "City life, modern, nightlife, entertainment",
            "relaxation": "Spa, wellness, yoga, meditation, peaceful"
        }
    }


@router.get(
    "/moods",
    status_code=status.HTTP_200_OK,
    summary="Get available mood options",
    description="Returns list of supported mood/travel styles",
    response_model=dict
)
async def get_moods():
    """Get list of available moods"""
    return {
        "success": True,
        "moods": [m.value for m in Mood],
        "descriptions": {
            "relaxed": "Peaceful, tranquil, calm, serene, quiet",
            "energetic": "Vibrant, bustling, lively, active, exciting",
            "romantic": "Couples, sunset, intimate, charming, beautiful",
            "family": "Kids, children, activities, safe, friendly",
            "solo": "Backpacker, hostels, affordable, social"
        }
    }


@router.get(
    "/budget-categories",
    status_code=status.HTTP_200_OK,
    summary="Get budget category information",
    description="Returns budget categories and their ranges",
    response_model=dict
)
async def get_budget_categories():
    """Get budget category information"""
    return {
        "success": True,
        "categories": [b.value for b in BudgetCategory],
        "ranges": {
            "budget": {"min": 0, "max": 2000, "description": "Budget-friendly, < $2000"},
            "moderate": {"min": 2000, "max": 3500, "description": "Mid-range, $2000-$3500"},
            "luxury": {"min": 3500, "max": None, "description": "Luxury, > $3500"}
        },
        "note": "You can also specify max_budget in USD to override category"
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check for recommendation service",
    response_model=dict
)
async def health_check():
    """Check if recommendation service is operational"""
    try:
        # Try to initialize recommender to verify dataset exists
        from app.services.recommendation import get_recommender
        recommender = get_recommender()
        
        return {
            "success": True,
            "status": "healthy",
            "service": "Content-Based Recommendation",
            "algorithm": "TF-IDF + Cosine Similarity",
            "total_destinations": len(recommender.df),
            "features": {
                "tfidf_features": recommender.tfidf_matrix.shape[1] if recommender.tfidf_matrix is not None else 0,
                "ngram_range": "(1, 2)",
                "max_features": 500
            }
        }
    except Exception as e:
        logger.error(f"[Health Check] Service unhealthy: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Recommendation service unavailable: {str(e)}"
        )

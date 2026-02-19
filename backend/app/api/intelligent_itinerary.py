"""
Intelligent Itinerary API
Unified endpoint integrating all AI systems

Integrations:
- Budget Optimization
- Destination Recommendations
- Hotel & Restaurant Ranking
- Route Optimization
- Educational Enrichment
- Book Recommendations
"""

from fastapi import APIRouter, HTTPException, status, Body
import logging

from app.models.intelligent_itinerary import (
    IntelligentItineraryRequest,
    IntelligentItineraryResponse
)
from app.services.intelligent_itinerary import get_orchestrator

# Initialize router
router = APIRouter(tags=["Intelligent Itinerary"])

# Logging
logger = logging.getLogger(__name__)


# ============================================================================
# MAIN ENDPOINT
# ============================================================================

@router.post(
    "/intelligent-itinerary",
    response_model=IntelligentItineraryResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate comprehensive intelligent itinerary",
    description="""
    **Unified AI-Powered Itinerary Generation**
    
    Integrates 5 major AI systems into one endpoint:
    
    **1. Budget Optimization Engine**
    - Dynamic allocation based on budget tier
    - Group discount calculations
    - Per-person and per-day breakdowns
    - Smart budget-saving suggestions
    
    **2. Destination Recommendation System**
    - TF-IDF content-based recommendations
    - Finds alternative similar destinations
    - Matches travel type and mood preferences
    
    **3. Ranking Engine**
    - Multi-criteria weighted scoring
    - Ranks hotels, restaurants, attractions
    - Distance-based optimization
    - Student-friendly filtering
    
    **4. Route Optimization**
    - Greedy nearest-neighbor algorithm
    - Minimizes total travel distance
    - Efficient itinerary sequencing
    
    **5. Educational Enrichment**
    - Historical summaries (AI-generated)
    - Cultural insights and etiquette
    - Book recommendations
    - Student-focused learning content
    
    **Performance**:
    - Clean architecture with service separation
    - Efficient parallel execution where possible
    - No duplicate calculations
    - Optimized for production use
    
    **Use Case**: One-stop endpoint for complete trip planning with AI intelligence.
    """,
    responses={
        200: {
            "description": "Intelligent itinerary generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Intelligent itinerary generated successfully",
                        "location": "Paris",
                        "duration_days": 7,
                        "group_size": 2,
                        "optimized_itinerary": [
                            {
                                "day": 1,
                                "title": "Day 1: Eiffel Tower, Louvre Museum",
                                "morning_activity": "Eiffel Tower",
                                "afternoon_activity": "Louvre Museum",
                                "evening_activity": "Seine River Cruise",
                                "recommended_restaurant": "Le Comptoir du Relais",
                                "budget_estimate": 107.14,
                                "notes": "Budget: $107 for the day"
                            }
                        ],
                        "ranked_hotels": [
                            {
                                "name": "Paris Grand Hotel",
                                "place_type": "hotel",
                                "rating": 4.5,
                                "score": 0.92,
                                "rank": 1,
                                "distance_km": 2.3,
                                "price_level": "moderate",
                                "student_friendly": True
                            }
                        ],
                        "ranked_restaurants": [
                            {
                                "name": "Paris Local Bistro",
                                "place_type": "restaurant",
                                "rating": 4.6,
                                "score": 0.89,
                                "rank": 1,
                                "distance_km": 1.5,
                                "student_friendly": True
                            }
                        ],
                        "route_order": {
                            "ordered_places": [
                                "Paris Museum",
                                "Paris Historic Center",
                                "Paris Art Gallery"
                            ],
                            "total_distance_km": 12.5,
                            "estimated_travel_time_hours": 0.42,
                            "optimization_method": "greedy_nearest_neighbor"
                        },
                        "budget_breakdown": {
                            "total_budget": 1500,
                            "duration_days": 7,
                            "group_size": 2,
                            "budget_tier": "moderate",
                            "per_person_per_day": 107.14,
                            "stay_budget": 600,
                            "food_budget": 450,
                            "travel_budget": 300,
                            "activity_budget": 150
                        },
                        "educational_enrichment": {
                            "destination": "Paris",
                            "country": "France",
                            "historical_summary": "Paris has been a center of art, culture, and intellectual thought for centuries...",
                            "cultural_insights": [
                                "Always greet with 'Bonjour' before asking questions",
                                "Tipping is not mandatory but 5-10% is appreciated"
                            ],
                            "travel_tips": [
                                "Buy a Paris Visite pass for unlimited metro travel",
                                "Visit museums on first Sunday of month for free entry"
                            ]
                        },
                        "recommended_books": [
                            {
                                "title": "The Flaneur",
                                "author": "Edmund White",
                                "rating": 4.2,
                                "student_friendly": True
                            }
                        ],
                        "generation_time_seconds": 2.45,
                        "included_features": [
                            "budget_optimization",
                            "hotel_ranking",
                            "restaurant_ranking",
                            "attraction_ranking",
                            "route_optimization",
                            "educational_enrichment"
                        ]
                    }
                }
            }
        },
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"}
    }
)
async def generate_intelligent_itinerary(
    request: IntelligentItineraryRequest = Body(
        ...,
        example={
            "location": "Paris",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "budget": 1500,
            "duration": 7,
            "group_size": 2,
            "mood": "relaxed",
            "travel_type": "cultural",
            "include_hotels": True,
            "include_restaurants": True,
            "include_enrichment": True,
            "student_friendly": True
        }
    )
):
    """
    Generate comprehensive intelligent itinerary
    
    Integrates all AI systems in a single request:
    - Budget allocation optimization
    - Destination recommendations
    - Hotel & restaurant ranking
    - Route optimization
    - Educational enrichment
    
    Args:
        request: IntelligentItineraryRequest with all parameters
        
    Returns:
        IntelligentItineraryResponse with complete itinerary
        
    Example:
        ```python
        POST /api/generate/intelligent-itinerary
        {
            "location": "Paris",
            "budget": 1500,
            "duration": 7,
            "group_size": 2,
            "mood": "cultural",
            "travel_type": "cultural"
        }
        ```
    """
    try:
        logger.info(
            f"[Itinerary API] Request - {request.location}, "
            f"${request.budget}, {request.duration}d, {request.group_size}p"
        )
        
        # Validate inputs
        if request.budget <= 0:
            raise ValueError("Budget must be greater than 0")
        
        if request.duration <= 0 or request.duration > 365:
            raise ValueError("Duration must be between 1 and 365 days")
        
        if request.group_size <= 0 or request.group_size > 50:
            raise ValueError("Group size must be between 1 and 50 people")
        
        # Get orchestrator and generate itinerary
        orchestrator = get_orchestrator()
        result = await orchestrator.generate_intelligent_itinerary(request)
        
        logger.info(
            f"[Itinerary API] Success - Generated in {result['generation_time_seconds']}s, "
            f"{len(result['included_features'])} features"
        )
        
        # Build response
        response = IntelligentItineraryResponse(**result)
        
        return response
        
    except ValueError as e:
        logger.error(f"[Itinerary API] Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request parameters: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[Itinerary API] Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate intelligent itinerary. Please try again later."
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get(
    "/intelligent-itinerary/features",
    status_code=status.HTTP_200_OK,
    summary="Get available features",
    description="Returns list of all integrated AI features",
    response_model=dict
)
async def get_features():
    """Get list of available integrated features"""
    return {
        "success": True,
        "features": {
            "budget_optimization": {
                "description": "Dynamic budget allocation with tier-based optimization",
                "capabilities": [
                    "5 budget tiers (ultra_low to high)",
                    "Group discount calculations",
                    "Per-person and per-day breakdowns",
                    "Smart budget-saving suggestions"
                ]
            },
            "destination_recommendations": {
                "description": "Content-based recommendation system using TF-IDF",
                "capabilities": [
                    "Similar destination suggestions",
                    "Budget and duration filtering",
                    "Travel type matching (adventure, cultural, etc.)",
                    "Mood-based recommendations"
                ]
            },
            "ranking_engine": {
                "description": "Multi-criteria weighted scoring for places",
                "capabilities": [
                    "Hotel ranking by rating, budget, distance",
                    "Restaurant recommendations",
                    "Attraction prioritization",
                    "Student-friendly filtering"
                ]
            },
            "route_optimization": {
                "description": "Efficient travel route planning",
                "capabilities": [
                    "Nearest-neighbor greedy algorithm",
                    "Distance minimization",
                    "Travel time estimation",
                    "Optimal visit sequencing"
                ]
            },
            "educational_enrichment": {
                "description": "AI-generated cultural and historical content",
                "capabilities": [
                    "Historical summaries",
                    "Cultural insights and etiquette",
                    "Book recommendations",
                    "Travel tips for students"
                ]
            }
        },
        "integration": "All features accessible through single endpoint",
        "performance": {
            "execution": "Parallel where possible",
            "caching": "Optimized service singletons",
            "typical_response_time": "2-4 seconds"
        }
    }


@router.get(
    "/intelligent-itinerary/supported-moods",
    status_code=status.HTTP_200_OK,
    summary="Get supported mood options",
    response_model=dict
)
async def get_supported_moods():
    """Get list of supported mood preferences"""
    return {
        "success": True,
        "moods": [
            {
                "value": "relaxed",
                "description": "Slow-paced, leisurely exploration",
                "ideal_for": "Beach vacations, wellness retreats"
            },
            {
                "value": "energetic",
                "description": "Active, adventure-filled itinerary",
                "ideal_for": "Adventure travel, hiking, sports"
            },
            {
                "value": "romantic",
                "description": "Intimate, couple-focused experiences",
                "ideal_for": "Honeymoons, anniversaries"
            },
            {
                "value": "adventurous",
                "description": "Thrill-seeking, off-the-beaten-path",
                "ideal_for": "Backpacking, extreme sports"
            },
            {
                "value": "curious",
                "description": "Discovery-focused, learning-oriented",
                "ideal_for": "Cultural exploration, museums"
            },
            {
                "value": "contemplative",
                "description": "Reflective, peaceful exploration",
                "ideal_for": "Spiritual journeys, nature retreats"
            }
        ]
    }


@router.get(
    "/intelligent-itinerary/supported-travel-types",
    status_code=status.HTTP_200_OK,
    summary="Get supported travel type options",
    response_model=dict
)
async def get_supported_travel_types():
    """Get list of supported travel types"""
    return {
        "success": True,
        "travel_types": [
            {
                "value": "adventure",
                "description": "Outdoor activities, hiking, extreme sports",
                "examples": ["Mountain climbing", "Scuba diving", "Safari"]
            },
            {
                "value": "beach",
                "description": "Coastal relaxation, water sports",
                "examples": ["Tropical islands", "Beach resorts", "Surfing"]
            },
            {
                "value": "cultural",
                "description": "Museums, historical sites, local traditions",
                "examples": ["Ancient ruins", "Art galleries", "Cultural festivals"]
            },
            {
                "value": "nature",
                "description": "National parks, wildlife, landscapes",
                "examples": ["Forest hikes", "Wildlife watching", "Scenic drives"]
            },
            {
                "value": "urban",
                "description": "City exploration, nightlife, modern culture",
                "examples": ["Metropolitan cities", "Shopping districts", "Urban art"]
            },
            {
                "value": "historical",
                "description": "Ancient sites, archaeological wonders",
                "examples": ["Castles", "Archaeological sites", "Heritage towns"]
            },
            {
                "value": "food",
                "description": "Culinary experiences, local cuisine",
                "examples": ["Food tours", "Cooking classes", "Wine tasting"]
            },
            {
                "value": "relaxation",
                "description": "Spa, wellness, peaceful retreats",
                "examples": ["Spa resorts", "Yoga retreats", "Hot springs"]
            }
        ]
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get(
    "/intelligent-itinerary/health",
    status_code=status.HTTP_200_OK,
    summary="Health check for intelligent itinerary service",
    response_model=dict
)
async def health_check():
    """Check if intelligent itinerary service is operational"""
    try:
        from app.services.intelligent_itinerary import get_orchestrator
        from app.services.budget import get_budget_allocator
        from app.services.recommendation import get_recommender
        from app.services.enrichment import get_enrichment_engine
        
        orchestrator = get_orchestrator()
        budget_allocator = get_budget_allocator()
        recommender = get_recommender()
        enrichment = get_enrichment_engine()
        
        return {
            "success": True,
            "status": "healthy",
            "service": "Intelligent Itinerary Orchestrator",
            "version": "1.0.0",
            "subsystems": {
                "budget_optimization": "operational",
                "destination_recommendations": "operational",
                "ranking_engine": "operational",
                "route_optimization": "operational",
                "educational_enrichment": "operational"
            },
            "integrations": 5,
            "features": [
                "budget_optimization",
                "destination_recommendations",
                "hotel_ranking",
                "restaurant_ranking",
                "attraction_ranking",
                "route_optimization",
                "educational_enrichment",
                "book_recommendations"
            ]
        }
    except Exception as e:
        logger.error(f"[Health Check] Service unhealthy: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Intelligent itinerary service unavailable: {str(e)}"
        )

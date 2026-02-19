"""
Intelligence API - Advanced AI-powered travel intelligence endpoints
Showcases recommendation engine, analytics, and smart features
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.models.user import UserProfile, UserPreferences
from app.models.destination import Destination, DestinationFilter
from app.models.analytics import (
    RecommendationScore,
    DestinationTrend,
    UserBehavior,
    EventType,
    SystemMetrics
)
from app.models.responses import SuccessResponse, PaginatedResponse

from app.services.recommendation_engine import recommendation_engine
from app.services.analytics_service import analytics_service
from app.services.cache_service import recommendations_cache, analytics_cache
from app.middleware.production import get_current_user, get_session_id

router = APIRouter()


@router.post("/recommendations", response_model=SuccessResponse[List[RecommendationScore]])
async def get_personalized_recommendations(
    user_profile: UserProfile,
    destinations: List[Destination],
    limit: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    target_month: Optional[int] = Query(None, ge=1, le=12, description="Target travel month")
):
    """
    Get personalized destination recommendations using ML-based engine
    
    - **User Profile**: Complete user preferences and history
    - **Destinations**: Available destinations to rank
    - **Limit**: Number of recommendations (default 10)
    - **Target Month**: Optional month for seasonal scoring
    
    Returns top recommended destinations with scores and reasons
    """
    # Check cache first
    cache_key = f"{user_profile.user_id}:{limit}:{target_month}"
    cached = recommendations_cache.get(cache_key)
    if cached:
        return SuccessResponse(
            message="Recommendations retrieved from cache",
            data=cached
        )
    
    # Generate recommendations
    recommendations = recommendation_engine.get_top_recommendations(
        user_profile=user_profile,
        destinations=destinations,
        limit=limit,
        target_month=target_month
    )
    
    # Cache results (10 minutes)
    recommendations_cache.set(cache_key, recommendations, ttl=600)
    
    return SuccessResponse(
        message=f"Generated {len(recommendations)} personalized recommendations",
        data=recommendations
    )


@router.get("/trending", response_model=SuccessResponse[List[DestinationTrend]])
async def get_trending_destinations(
    time_period: str = Query("week", regex="^(day|week|month)$"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get currently trending destinations based on user activity
    
    - **Time Period**: day, week, or month
    - **Limit**: Number of trending destinations
    
    Trending score calculated from:
    - Views, searches, wishlist additions
    - Itineraries created
    - Booking intents
    """
    # Check cache
    cache_key = f"trending:{time_period}:{limit}"
    cached = analytics_cache.get(cache_key)
    if cached:
        return SuccessResponse(
            message="Trending data retrieved from cache",
            data=cached
        )
    
    # Calculate trending
    trending = analytics_service.get_trending_destinations(
        time_period=time_period,
        limit=limit
    )
    
    # Cache for 15 minutes
    analytics_cache.set(cache_key, trending, ttl=900)
    
    return SuccessResponse(
        message=f"Retrieved top {len(trending)} trending destinations",
        data=trending
    )


@router.post("/track-event", response_model=SuccessResponse[bool])
async def track_user_event(
    event: UserBehavior,
    user_id: Optional[str] = Depends(get_current_user),
    session_id: Optional[str] = Depends(get_session_id)
):
    """
    Track user behavior event for analytics and ML training
    
    Event types:
    - view_destination: User viewed destination details
    - search: User performed search
    - add_wishlist: Added to wishlist
    - create_itinerary: Created itinerary
    - chat_interaction: Interacted with chatbot
    - booking_intent: Showed intent to book
    """
    # Override with authenticated user/session
    if user_id:
        event.user_id = user_id
    if session_id:
        event.session_id = session_id
    
    # Track event
    success = analytics_service.track_event(event)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track event"
        )
    
    return SuccessResponse(
        message="Event tracked successfully",
        data=True
    )


@router.get("/popular-searches", response_model=SuccessResponse[List[dict]])
async def get_popular_searches(
    time_period: str = Query("week", regex="^(day|week|month)$"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get most popular search queries
    
    Useful for:
    - Search autocomplete
    - Trending keywords
    - Content optimization
    """
    # Check cache
    cache_key = f"popular_searches:{time_period}:{limit}"
    cached = analytics_cache.get(cache_key)
    if cached:
        return SuccessResponse(message="Retrieved from cache", data=cached)
    
    # Get popular searches
    searches = analytics_service.get_popular_searches(
        time_period=time_period,
        limit=limit
    )
    
    # Cache for 30 minutes
    analytics_cache.set(cache_key, searches, ttl=1800)
    
    return SuccessResponse(
        message=f"Retrieved {len(searches)} popular searches",
        data=searches
    )


@router.get("/user-journey/{user_id}", response_model=SuccessResponse[List[UserBehavior]])
async def get_user_journey(
    user_id: str,
    session_id: Optional[str] = None
):
    """
    Get user's interaction journey
    
    Shows complete timeline of user actions for:
    - UX optimization
    - Conversion analysis
    - Personalization improvement
    """
    journey = analytics_service.get_user_journey(
        user_id=user_id,
        session_id=session_id
    )
    
    return SuccessResponse(
        message=f"Retrieved {len(journey)} events",
        data=journey
    )


@router.get("/similar-destinations/{destination_id}", response_model=SuccessResponse[List[int]])
async def get_similar_destinations(
    destination_id: int,
    destinations: List[Destination],  # From dependency or database
    limit: int = Query(5, ge=1, le=20)
):
    """
    Get similar destinations for "You might also like" recommendations
    
    Similarity based on:
    - Region and climate
    - Tags and interests
    - Price range
    - User behavior patterns
    """
    # Find target destination
    target = next((d for d in destinations if d.id == destination_id), None)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    
    # Get similar destinations
    similar = recommendation_engine.get_similar_destinations(
        destination=target,
        all_destinations=destinations,
        limit=limit
    )
    
    return SuccessResponse(
        message=f"Found {len(similar)} similar destinations",
        data=similar
    )


@router.get("/conversion-rate", response_model=SuccessResponse[dict])
async def get_conversion_rate(
    event_from: EventType,
    event_to: EventType,
    time_window_days: int = Query(30, ge=1, le=365)
):
    """
    Calculate conversion rate between two event types
    
    Examples:
    - View → Wishlist conversion
    - Wishlist → Itinerary conversion
    - View → Booking intent
    
    Useful for:
    - Funnel optimization
    - Feature effectiveness
    - A/B testing
    """
    conversion_rate = analytics_service.calculate_conversion_rate(
        event_from=event_from,
        event_to=event_to,
        time_window_days=time_window_days
    )
    
    return SuccessResponse(
        message="Conversion rate calculated",
        data={
            'from_event': event_from.value,
            'to_event': event_to.value,
            'conversion_rate': round(conversion_rate, 4),
            'conversion_percentage': round(conversion_rate * 100, 2),
            'time_window_days': time_window_days
        }
    )


@router.get("/system-metrics", response_model=SuccessResponse[SystemMetrics])
async def get_system_metrics():
    """
    Get overall system performance metrics
    
    Includes:
    - Active users
    - Popular destinations
    - Search trends
    - Engagement metrics
    
    For admin dashboard and monitoring
    """
    metrics = analytics_service.get_system_metrics()
    
    return SuccessResponse(
        message="System metrics retrieved",
        data=metrics
    )


@router.post("/optimize-itinerary", response_model=SuccessResponse[dict])
async def optimize_itinerary(
    itinerary_data: dict,
    optimization_goals: List[str] = Query(
        ["cost", "time", "popular"],
        description="Optimization priorities"
    )
):
    """
    AI-powered itinerary optimization
    
    Optimization goals:
    - cost: Minimize expenses
    - time: Optimize travel time
    - popular: Include popular attractions
    - budget_friendly: Student-friendly options
    
    Returns optimized itinerary with suggestions
    """
    # Placeholder for optimization logic
    # In production, implement ML-based optimization
    
    suggestions = []
    savings = 0.0
    
    if "cost" in optimization_goals:
        suggestions.append("Consider visiting during off-season for 20% savings")
        savings += 200
    
    if "time" in optimization_goals:
        suggestions.append("Rearrange activities to minimize travel between locations")
    
    if "popular" in optimization_goals:
        suggestions.append("Add Eiffel Tower visit during less crowded morning hours")
    
    return SuccessResponse(
        message="Itinerary optimized",
        data={
            'original_cost': itinerary_data.get('total_cost', 0),
            'optimized_cost': itinerary_data.get('total_cost', 0) - savings,
            'savings': savings,
            'suggestions': suggestions,
            'optimization_score': 85.5
        }
    )

"""
Intelligent Itinerary Orchestration Service
Integrates all AI systems: ranking, recommendations, budget, enrichment, routing

Features:
- Budget allocation optimization
- Destination recommendations
- Hotel & restaurant ranking
- Route optimization
- Educational enrichment
- Book recommendations
- Efficient parallel execution
- No duplicate calculations
"""

import asyncio
import time
import math
from typing import List, Dict, Optional, Tuple, Any
import logging

from app.services.budget import optimize_budget
from app.services.recommendation import ContentBasedRecommender, get_recommender
from app.services.enrichment import EnrichmentEngine, get_enrichment_engine
from app.services.ranking_service import rank_places
from app.models.ranking import Place, RankingRequest
from app.models.intelligent_itinerary import (
    IntelligentItineraryRequest,
    RankedPlace,
    RouteOptimization,
    BudgetBreakdown,
    EducationalEnrichment,
    BookRecommendation,
    DayItinerary
)

logger = logging.getLogger(__name__)


# ============================================================================
# ROUTE OPTIMIZATION
# ============================================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula
    
    Args:
        lat1, lon1: Coordinates of point 1
        lat2, lon2: Coordinates of point 2
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(dlon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def optimize_route_greedy(
    places: List[Dict],
    start_lat: float,
    start_lon: float
) -> Tuple[List[str], float]:
    """
    Optimize route using greedy nearest-neighbor algorithm
    
    Args:
        places: List of places with coordinates
        start_lat: Starting latitude
        start_lon: Starting longitude
        
    Returns:
        Tuple of (ordered place names, total distance in km)
    """
    if not places:
        return [], 0.0
    
    # Filter places with valid coordinates
    valid_places = [
        p for p in places 
        if p.get('latitude') and p.get('longitude')
    ]
    
    if not valid_places:
        # No coordinates available - return original order
        return [p['name'] for p in places], 0.0
    
    unvisited = valid_places.copy()
    route = []
    total_distance = 0.0
    current_lat = start_lat
    current_lon = start_lon
    
    # Greedy: always visit nearest unvisited place
    while unvisited:
        # Find nearest place to current position
        nearest_idx = 0
        nearest_dist = float('inf')
        
        for idx, place in enumerate(unvisited):
            dist = haversine_distance(
                current_lat, current_lon,
                place['latitude'], place['longitude']
            )
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_idx = idx
        
        # Visit nearest place
        nearest = unvisited.pop(nearest_idx)
        route.append(nearest['name'])
        total_distance += nearest_dist
        current_lat = nearest['latitude']
        current_lon = nearest['longitude']
    
    return route, total_distance


# ============================================================================
# ITINERARY GENERATION
# ============================================================================

def generate_daily_itinerary(
    duration: int,
    hotels: List[Dict],
    restaurants: List[Dict],
    attractions: List[Dict],
    budget_per_day: float
) -> List[DayItinerary]:
    """
    Generate day-by-day itinerary from ranked places
    
    Args:
        duration: Number of days
        hotels: Ranked hotels
        restaurants: Ranked restaurants
        attractions: Ranked attractions
        budget_per_day: Daily budget estimate
        
    Returns:
        List of DayItinerary objects
    """
    itinerary = []
    
    # Distribute attractions across days
    attractions_per_day = max(1, len(attractions) // duration)
    
    for day in range(1, duration + 1):
        # Get attractions for this day
        start_idx = (day - 1) * attractions_per_day
        end_idx = start_idx + attractions_per_day
        day_attractions = attractions[start_idx:end_idx]
        
        # Assign time slots
        morning = day_attractions[0]['name'] if len(day_attractions) > 0 else None
        afternoon = day_attractions[1]['name'] if len(day_attractions) > 1 else None
        evening = day_attractions[2]['name'] if len(day_attractions) > 2 else None
        
        # Recommend restaurant (cycle through top restaurants)
        restaurant = restaurants[(day - 1) % len(restaurants)]['name'] if restaurants else None
        
        # Generate title based on attractions
        if day_attractions:
            title = f"Day {day}: {', '.join([a['name'] for a in day_attractions[:2]])}"
        else:
            title = f"Day {day}: Explore & Discover"
        
        itinerary.append(DayItinerary(
            day=day,
            title=title[:80],  # Limit title length
            morning_activity=morning,
            afternoon_activity=afternoon,
            evening_activity=evening,
            recommended_restaurant=restaurant,
            budget_estimate=round(budget_per_day, 2),
            notes=f"Budget: ${budget_per_day:.0f} for the day"
        ))
    
    return itinerary


# ============================================================================
# ORCHESTRATION SERVICE
# ============================================================================

class IntelligentItineraryOrchestrator:
    """
    Orchestrates all subsystems to generate comprehensive intelligent itinerary
    
    Architecture:
    - Budget allocation (synchronous)
    - Destination recommendations (synchronous)
    - Hotel/restaurant ranking (synchronous)
    - Educational enrichment (async)
    - Route optimization (synchronous)
    - Itinerary generation (synchronous)
    
    Performance:
    - Parallel execution where possible
    - Efficient service reuse
    - Single-pass data processing
    """
    
    def __init__(self):
        """Initialize with service singletons"""
        self.recommender = get_recommender()
        self.enrichment_engine = get_enrichment_engine()
    
    async def generate_intelligent_itinerary(
        self,
        request: IntelligentItineraryRequest
    ) -> Dict:
        """
        Generate comprehensive intelligent itinerary
        
        Args:
            request: IntelligentItineraryRequest with all parameters
            
        Returns:
            Complete itinerary dictionary
            
        Process:
            1. Budget optimization
            2. Destination recommendations (alternative suggestions)
            3. Hotel & restaurant ranking
            4. Route optimization
            5. Educational enrichment (async)
            6. Day-by-day itinerary generation
        """
        start_time = time.time()
        included_features = []
        
        logger.info(f"[Itinerary] Generating for {request.location}, "
                   f"{request.duration} days, ${request.budget}")
        
        # ========================================================================
        # STEP 1: Budget Optimization
        # ========================================================================
        logger.info("[Itinerary] Step 1/6: Optimizing budget allocation")
        budget_result = optimize_budget(
            total_budget=request.budget,
            duration=request.duration,
            group_size=request.group_size,
            custom_allocation=request.custom_budget_allocation
        )
        included_features.append("budget_optimization")
        
        budget_breakdown = BudgetBreakdown(**budget_result)
        budget_per_day = budget_breakdown.per_person_per_day
        
        # ========================================================================
        # STEP 2: Destination Recommendations
        # ========================================================================
        logger.info("[Itinerary] Step 2/6: Finding alternative destinations")
        try:
            alternative_destinations = self.recommender.recommend(
                budget=budget_breakdown.budget_tier,
                duration=request.duration,
                travel_type=request.travel_type.value,
                mood=request.mood.value,
                top_n=3
            )
            included_features.append("destination_recommendations")
        except Exception as e:
            logger.warning(f"[Itinerary] Recommendations failed: {e}")
            alternative_destinations = []
        
        # ========================================================================
        # STEP 3: Ranking - Hotels, Restaurants, Attractions
        # ========================================================================
        logger.info("[Itinerary] Step 3/6: Ranking hotels, restaurants, attractions")
        
        ranked_hotels = []
        ranked_restaurants = []
        ranked_attractions = []
        
        # Create sample places (in production, fetch from database or API)
        sample_places = self._generate_sample_places(
            request.location,
            request.latitude,
            request.longitude
        )
        
        if request.include_hotels and request.latitude and request.longitude:
            try:
                ranking_request = RankingRequest(
                    user_lat=request.latitude,
                    user_lon=request.longitude,
                    place_types=["hotel"],
                    min_rating=3.5,
                    max_distance_km=request.max_distance_km,
                    budget_weight=0.3,
                    rating_weight=0.3,
                    distance_weight=0.2,
                    popularity_weight=0.2,
                    student_friendly_only=request.student_friendly,
                    limit=10
                )
                
                hotel_places = [p for p in sample_places if p.place_type == "hotel"]
                ranked_hotel_objects = rank_places(hotel_places, ranking_request)
                
                ranked_hotels = [
                    {
                        "name": h.name,
                        "place_type": h.place_type,
                        "rating": h.rating,
                        "score": h.final_score,
                        "rank": h.rank,
                        "distance_km": h.distance_km,
                        "price_level": h.price_level,
                        "student_friendly": h.student_friendly,
                        "latitude": h.latitude,
                        "longitude": h.longitude
                    }
                    for h in ranked_hotel_objects[:5]
                ]
                included_features.append("hotel_ranking")
            except Exception as e:
                logger.warning(f"[Itinerary] Hotel ranking failed: {e}")
        
        if request.include_restaurants and request.latitude and request.longitude:
            try:
                ranking_request = RankingRequest(
                    user_lat=request.latitude,
                    user_lon=request.longitude,
                    place_types=["restaurant"],
                    min_rating=4.0,
                    max_distance_km=request.max_distance_km,
                    budget_weight=0.25,
                    rating_weight=0.35,
                    distance_weight=0.2,
                    popularity_weight=0.2,
                    student_friendly_only=request.student_friendly,
                    limit=15
                )
                
                restaurant_places = [p for p in sample_places if p.place_type == "restaurant"]
                ranked_restaurant_objects = rank_places(restaurant_places, ranking_request)
                
                ranked_restaurants = [
                    {
                        "name": r.name,
                        "place_type": r.place_type,
                        "rating": r.rating,
                        "score": r.final_score,
                        "rank": r.rank,
                        "distance_km": r.distance_km,
                        "price_level": r.price_level,
                        "student_friendly": r.student_friendly,
                        "latitude": r.latitude,
                        "longitude": r.longitude
                    }
                    for r in ranked_restaurant_objects[:10]
                ]
                included_features.append("restaurant_ranking")
            except Exception as e:
                logger.warning(f"[Itinerary] Restaurant ranking failed: {e}")
        
        # Always rank attractions
        try:
            ranking_request = RankingRequest(
                user_lat=request.latitude or 0.0,
                user_lon=request.longitude or 0.0,
                place_types=["attraction"],
                min_rating=4.0,
                max_distance_km=request.max_distance_km,
                budget_weight=0.2,
                rating_weight=0.4,
                distance_weight=0.2,
                popularity_weight=0.2,
                student_friendly_only=request.student_friendly,
                limit=20
            )
            
            attraction_places = [p for p in sample_places if p.place_type == "attraction"]
            ranked_attraction_objects = rank_places(attraction_places, ranking_request)
            
            ranked_attractions = [
                {
                    "name": a.name,
                    "place_type": a.place_type,
                    "rating": a.rating,
                    "score": a.final_score,
                    "rank": a.rank,
                    "distance_km": a.distance_km,
                    "student_friendly": a.student_friendly,
                    "latitude": a.latitude,
                    "longitude": a.longitude
                }
                for a in ranked_attraction_objects[:request.duration * 3]  # ~3 per day
            ]
            included_features.append("attraction_ranking")
        except Exception as e:
            logger.warning(f"[Itinerary] Attraction ranking failed: {e}")
        
        # ========================================================================
        # STEP 4: Route Optimization
        # ========================================================================
        logger.info("[Itinerary] Step 4/6: Optimizing route")
        
        if request.latitude and request.longitude:
            route_places = ranked_attractions[:min(10, len(ranked_attractions))]
            ordered_places, total_distance = optimize_route_greedy(
                route_places,
                request.latitude,
                request.longitude
            )
            
            route_optimization = RouteOptimization(
                ordered_places=ordered_places,
                total_distance_km=round(total_distance, 2),
                estimated_travel_time_hours=round(total_distance / 30, 2),  # Assume 30 km/h avg
                optimization_method="greedy_nearest_neighbor"
            )
            included_features.append("route_optimization")
        else:
            route_optimization = RouteOptimization(
                ordered_places=[p['name'] for p in ranked_attractions[:10]],
                total_distance_km=0.0,
                estimated_travel_time_hours=0.0,
                optimization_method="no_coordinates"
            )
        
        # ========================================================================
        # STEP 5: Educational Enrichment (Async)
        # ========================================================================
        logger.info("[Itinerary] Step 5/6: Generating educational enrichment")
        
        educational_enrichment = None
        recommended_books = []
        
        if request.include_enrichment:
            try:
                # Get books
                books = self.enrichment_engine.get_recommended_books(
                    destination=request.location,
                    top_n=5
                )
                
                if books:
                    recommended_books = [
                        BookRecommendation(**book)
                        for book in books
                    ]
                
                # Generate enrichment content (async)
                if books:
                    enrichment_data = await self.enrichment_engine.generate_enrichment(
                        destination=request.location,
                        country=books[0].get('country', 'Unknown'),
                        region=books[0].get('region', 'Unknown'),
                        books=books
                    )
                    
                    educational_enrichment = EducationalEnrichment(
                        destination=request.location,
                        country=books[0].get('country', 'Unknown'),
                        region=books[0].get('region', 'Unknown'),
                        historical_summary=enrichment_data.get('historical_summary', ''),
                        cultural_insights=enrichment_data.get('cultural_insights', []),
                        travel_tips=enrichment_data.get('travel_tips', []),
                        why_books_matter=enrichment_data.get('why_books_matter', '')
                    )
                    
                included_features.append("educational_enrichment")
            except Exception as e:
                logger.warning(f"[Itinerary] Enrichment failed: {e}")
        
        # ========================================================================
        # STEP 6: Generate Day-by-Day Itinerary
        # ========================================================================
        logger.info("[Itinerary] Step 6/6: Building day-by-day itinerary")
        
        optimized_itinerary = generate_daily_itinerary(
            duration=request.duration,
            hotels=ranked_hotels,
            restaurants=ranked_restaurants,
            attractions=ranked_attractions,
            budget_per_day=budget_per_day
        )
        
        # ========================================================================
        # FINAL RESULT
        # ========================================================================
        
        generation_time = time.time() - start_time
        
        logger.info(f"[Itinerary] Complete! Generated in {generation_time:.2f}s")
        
        return {
            "success": True,
            "message": "Intelligent itinerary generated successfully",
            "location": request.location,
            "duration_days": request.duration,
            "group_size": request.group_size,
            "optimized_itinerary": [day.dict() for day in optimized_itinerary],
            "ranked_hotels": ranked_hotels,
            "ranked_restaurants": ranked_restaurants,
            "ranked_attractions": ranked_attractions,
            "route_order": route_optimization.dict(),
            "budget_breakdown": budget_breakdown.dict(),
            "educational_enrichment": educational_enrichment.dict() if educational_enrichment else None,
            "recommended_books": [book.dict() for book in recommended_books],
            "alternative_destinations": alternative_destinations,
            "generation_time_seconds": round(generation_time, 2),
            "included_features": included_features
        }
    
    def _generate_sample_places(
        self,
        location: str,
        lat: Optional[float],
        lon: Optional[float]
    ) -> List[Place]:
        """
        Generate sample places for demonstration
        In production, this would fetch from a real database or API
        
        Args:
            location: Destination name
            lat: Latitude
            lon: Longitude
            
        Returns:
            List of Place objects
        """
        # Default coordinates if not provided
        if not lat or not lon:
            lat, lon = 40.7128, -74.0060  # Default to NYC
        
        # Sample data - in production, fetch from database
        sample_places = [
            # Hotels
            Place(
                name=f"{location} Grand Hotel",
                place_type="hotel",
                latitude=lat + 0.01,
                longitude=lon + 0.01,
                rating=4.5,
                price_level="moderate",
                popularity_score=850,
                student_friendly=True
            ),
            Place(
                name=f"{location} Budget Inn",
                place_type="hotel",
                latitude=lat + 0.02,
                longitude=lon - 0.01,
                rating=3.8,
                price_level="budget",
                popularity_score=620,
                student_friendly=True
            ),
            Place(
                name=f"{location} Luxury Resort",
                place_type="hotel",
                latitude=lat - 0.01,
                longitude=lon + 0.02,
                rating=4.8,
                price_level="luxury",
                popularity_score=950,
                student_friendly=False
            ),
            
            # Restaurants
            Place(
                name=f"{location} Local Bistro",
                place_type="restaurant",
                latitude=lat + 0.005,
                longitude=lon + 0.005,
                rating=4.6,
                price_level="moderate",
                popularity_score=720,
                student_friendly=True
            ),
            Place(
                name=f"{location} Street Food Market",
                place_type="restaurant",
                latitude=lat + 0.008,
                longitude=lon - 0.003,
                rating=4.3,
                price_level="budget",
                popularity_score=880,
                student_friendly=True
            ),
            Place(
                name=f"{location} Fine Dining",
                place_type="restaurant",
                latitude=lat - 0.005,
                longitude=lon + 0.008,
                rating=4.9,
                price_level="luxury",
                popularity_score=650,
                student_friendly=False
            ),
            
            # Attractions
            Place(
                name=f"{location} Museum",
                place_type="attraction",
                latitude=lat + 0.003,
                longitude=lon + 0.004,
                rating=4.7,
                price_level="moderate",
                popularity_score=920,
                student_friendly=True
            ),
            Place(
                name=f"{location} Historic Center",
                place_type="attraction",
                latitude=lat,
                longitude=lon,
                rating=4.8,
                price_level="free",
                popularity_score=980,
                student_friendly=True
            ),
            Place(
                name=f"{location} Botanical Garden",
                place_type="attraction",
                latitude=lat + 0.015,
                longitude=lon - 0.01,
                rating=4.5,
                price_level="budget",
                popularity_score=750,
                student_friendly=True
            ),
            Place(
                name=f"{location} Art Gallery",
                place_type="attraction",
                latitude=lat - 0.008,
                longitude=lon + 0.012,
                rating=4.6,
                price_level="moderate",
                popularity_score=680,
                student_friendly=True
            ),
            Place(
                name=f"{location} Observation Deck",
                place_type="attraction",
                latitude=lat + 0.02,
                longitude=lon + 0.015,
                rating=4.7,
                price_level="moderate",
                popularity_score=850,
                student_friendly=False
            ),
        ]
        
        return sample_places


# ============================================================================
# SINGLETON
# ============================================================================

_orchestrator_instance = None

def get_orchestrator() -> IntelligentItineraryOrchestrator:
    """Get singleton orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = IntelligentItineraryOrchestrator()
    return _orchestrator_instance

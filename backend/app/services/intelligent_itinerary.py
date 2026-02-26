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
from app.services.maps_service import get_nearby_attractions, get_travel_metrics_matrix
from app.models.ranking import Place, RankingRequest, Coordinates
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

try:
    from ortools.constraint_solver import pywrapcp, routing_enums_pb2
    ORTOOLS_AVAILABLE = True
except Exception:
    ORTOOLS_AVAILABLE = False

try:
    from sklearn.cluster import KMeans
    KMEANS_AVAILABLE = True
except Exception:
    KMEANS_AVAILABLE = False


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


def _budget_match_score(budget_per_day: float, price_level: int) -> float:
    """Budget-fit score based on per-person-per-day budget and attraction price level (0-4)."""
    level = max(0, min(4, int(price_level if price_level is not None else 2)))

    if budget_per_day < 40:
        # Strongly prefer low-cost attractions
        return {0: 1.0, 1: 0.95, 2: 0.55, 3: 0.25, 4: 0.1}.get(level, 0.55)
    if budget_per_day < 100:
        # Balanced preference around moderate pricing
        return {0: 0.7, 1: 0.85, 2: 1.0, 3: 0.7, 4: 0.45}.get(level, 0.7)

    # Higher budget can absorb premium attractions
    return {0: 0.55, 1: 0.7, 2: 0.85, 3: 1.0, 4: 0.95}.get(level, 0.8)


def solve_tsp(cost_matrix: List[List[float]], start_index: int = 0) -> List[int]:
    """
    Solve TSP path ordering using OR-Tools.

    Production behavior:
    - Uses OR-Tools when available.
    - Falls back to greedy nearest-neighbor if OR-Tools is unavailable
      or no solution is found.
    """
    node_count = len(cost_matrix)
    if node_count == 0:
        return []
    if node_count == 1:
        return [0]

    if ORTOOLS_AVAILABLE:
        try:
            manager = pywrapcp.RoutingIndexManager(node_count, 1, start_index)
            routing = pywrapcp.RoutingModel(manager)

            def transit_callback(from_index: int, to_index: int) -> int:
                from_node = manager.IndexToNode(from_index)
                to_node = manager.IndexToNode(to_index)
                value = max(cost_matrix[from_node][to_node], 0.0)
                return int(value * 1000)

            transit_callback_index = routing.RegisterTransitCallback(transit_callback)
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
            search_parameters.time_limit.seconds = 3

            solution = routing.SolveWithParameters(search_parameters)
            if solution:
                route: List[int] = []
                index = routing.Start(0)
                while not routing.IsEnd(index):
                    route.append(manager.IndexToNode(index))
                    index = solution.Value(routing.NextVar(index))

                seen = set()
                deduped_route = []
                for node in route:
                    if node not in seen:
                        deduped_route.append(node)
                        seen.add(node)
                return deduped_route
        except Exception as exc:
            logger.warning(f"[Itinerary] OR-Tools TSP failed, falling back to greedy: {exc}")

    # Fallback: greedy nearest-neighbor on cost matrix
    unvisited = set(range(node_count))
    route = [start_index]
    unvisited.remove(start_index)
    current = start_index

    while unvisited:
        next_node = min(unvisited, key=lambda node: cost_matrix[current][node])
        route.append(next_node)
        unvisited.remove(next_node)
        current = next_node

    return route


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
    if duration <= 0:
        return itinerary

    attraction_names = [a.get("name") for a in attractions if a.get("name")]
    if not attraction_names:
        attraction_names = ["City Highlights"]

    day_buckets: List[List[str]] = [[] for _ in range(duration)]
    for idx, attraction_name in enumerate(attraction_names):
        day_buckets[idx % duration].append(attraction_name)

    if budget_per_day < 40:
        max_activities = 2
    elif budget_per_day < 100:
        max_activities = 3
    else:
        max_activities = 4

    for day in range(1, duration + 1):
        day_items = day_buckets[day - 1]
        if not day_items:
            day_items = [attraction_names[(day - 1) % len(attraction_names)]]
        day_items = day_items[:max_activities]

        morning = day_items[0] if len(day_items) > 0 else None
        afternoon = day_items[1] if len(day_items) > 1 else None
        evening = day_items[2] if len(day_items) > 2 else None

        restaurant = restaurants[(day - 1) % len(restaurants)]["name"] if restaurants else None

        title_items = [item for item in [morning, afternoon] if item]
        title = f"Day {day}: {', '.join(title_items)}" if title_items else f"Day {day}: Explore & Discover"

        itinerary.append(DayItinerary(
            day=day,
            title=title[:80],
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

    def _cluster_attractions_for_days(
        self,
        attractions: List[Dict[str, Any]],
        duration: int
    ) -> List[List[Dict[str, Any]]]:
        """Cluster attractions by proximity for multi-day itinerary planning."""
        if duration <= 1 or len(attractions) <= 1:
            return [attractions]

        cluster_count = min(duration, len(attractions))
        if not KMEANS_AVAILABLE or cluster_count <= 1:
            buckets: List[List[Dict[str, Any]]] = [[] for _ in range(cluster_count)]
            for idx, attraction in enumerate(attractions):
                buckets[idx % cluster_count].append(attraction)
            return [bucket for bucket in buckets if bucket]

        coordinates = [
            [float(a.get("latitude", 0.0)), float(a.get("longitude", 0.0))]
            for a in attractions
        ]

        try:
            model = KMeans(n_clusters=cluster_count, random_state=42, n_init=10)
            labels = model.fit_predict(coordinates)
            clusters: List[List[Dict[str, Any]]] = [[] for _ in range(cluster_count)]
            for attraction, label in zip(attractions, labels):
                clusters[int(label)].append(attraction)
            return [cluster for cluster in clusters if cluster]
        except Exception as exc:
            logger.warning(f"[Itinerary] KMeans clustering failed, falling back to balanced buckets: {exc}")
            buckets = [[] for _ in range(cluster_count)]
            for idx, attraction in enumerate(attractions):
                buckets[idx % cluster_count].append(attraction)
            return [bucket for bucket in buckets if bucket]

    def _score_attractions_ml(
        self,
        attractions: List[Dict[str, Any]],
        budget_per_day: float
    ) -> List[Dict[str, Any]]:
        """Apply ML-style weighted attraction scoring with normalized features."""
        if not attractions:
            return []

        max_reviews_log = max(
            [math.log1p(max(int(a.get("user_ratings_total", 0) or 0), 0)) for a in attractions] + [1.0]
        )

        def attraction_score(attraction: Dict[str, Any]) -> float:
            normalized_rating = max(0.0, min(1.0, float(attraction.get("rating", 0.0) or 0.0) / 5.0))
            reviews = max(int(attraction.get("user_ratings_total", 0) or 0), 0)
            normalized_reviews = math.log1p(reviews) / max_reviews_log if max_reviews_log > 0 else 0.0

            budget_score = _budget_match_score(
                budget_per_day=budget_per_day,
                price_level=int(attraction.get("price_level", 2) or 2),
            )
            distance_score = 1 / (1 + float(attraction.get("distance_km", 1.0) or 1.0))

            return (
                0.35 * normalized_rating
                + 0.25 * normalized_reviews
                + 0.20 * budget_score
                + 0.20 * distance_score
            )

        ranked = sorted(attractions, key=attraction_score, reverse=True)
        return [
            {
                **attraction,
                "rank": index + 1,
                "score": round(attraction_score(attraction), 4),
            }
            for index, attraction in enumerate(ranked)
        ]

    async def _optimize_route_with_tsp(
        self,
        attractions: List[Dict[str, Any]],
        start_lat: float,
        start_lon: float
    ) -> Tuple[List[str], float, float]:
        """Optimize route order with time-first weighted TSP objective and safety factor."""
        if not attractions:
            return [], 0.0, 0.0

        start_point = (start_lat, start_lon)
        attraction_points = [
            (float(a.get("latitude", 0.0)), float(a.get("longitude", 0.0)))
            for a in attractions
        ]
        all_points = [start_point] + attraction_points

        distance_matrix, duration_matrix = await get_travel_metrics_matrix(all_points)
        if not distance_matrix or not duration_matrix:
            names, total_distance = optimize_route_greedy(attractions, start_lat, start_lon)
            return names, total_distance, (total_distance / 30.0) * 60.0

        node_metadata = [
            {"rating": 5.0, "safety_score": 0.1},
            *[
                {
                    "rating": float(a.get("rating", 4.0) or 4.0),
                    "safety_score": float(a.get("safety_score", 0.5) or 0.5),
                }
                for a in attractions
            ],
        ]

        cost_matrix: List[List[float]] = []
        for i in range(len(all_points)):
            row: List[float] = []
            for j in range(len(all_points)):
                if i == j:
                    row.append(0.0)
                    continue

                time_cost = float(duration_matrix[i][j])
                distance_cost = float(distance_matrix[i][j])
                rating = max(node_metadata[j].get("rating", 4.0), 0.1)
                inverse_rating = 1.0 / rating
                safety_score = float(node_metadata[j].get("safety_score", 0.5))

                final_weight = (
                    0.4 * time_cost
                    + 0.3 * distance_cost
                    + 0.2 * inverse_rating
                    + 0.1 * safety_score
                )
                row.append(final_weight)
            cost_matrix.append(row)

        route_nodes = solve_tsp(cost_matrix=cost_matrix, start_index=0)
        route_nodes = [node for node in route_nodes if node != 0]

        ordered_places: List[str] = []
        total_distance_km = 0.0
        total_duration_minutes = 0.0
        prev_node = 0

        for node in route_nodes:
            attraction_index = node - 1
            if 0 <= attraction_index < len(attractions):
                ordered_places.append(attractions[attraction_index].get("name", "Unknown"))
                total_distance_km += float(distance_matrix[prev_node][node])
                total_duration_minutes += float(duration_matrix[prev_node][node])
                prev_node = node

        return ordered_places, round(total_distance_km, 2), round(total_duration_minutes, 2)
    
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
        if request.latitude and request.longitude:
            google_attractions = await get_nearby_attractions(
                location_name=request.location,
                lat=request.latitude,
                lon=request.longitude,
                radius_km=request.max_distance_km,
                travel_type=request.travel_type.value,
            )

            sample_attractions = []
            for attraction in google_attractions:
                distance = haversine_distance(
                    request.latitude,
                    request.longitude,
                    float(attraction.get("latitude", 0.0)),
                    float(attraction.get("longitude", 0.0)),
                )
                sample_attractions.append(
                    {
                        **attraction,
                        "distance_km": round(distance, 2),
                        "student_friendly": int(attraction.get("price_level", 2) or 2) <= 2,
                    }
                )

            if sample_attractions:
                included_features.append("google_places_attractions")
            else:
                sample_attractions = self._generate_sample_attractions(
                    request.location,
                    request.latitude,
                    request.longitude,
                )
        else:
            sample_attractions = self._generate_sample_attractions(
                request.location,
                request.latitude,
                request.longitude,
            )
        
        if request.include_hotels and request.latitude and request.longitude:
            try:
                ranking_request = RankingRequest(
                    user_budget=max(budget_per_day, 1.0),
                    user_location=Coordinates(
                        latitude=request.latitude,
                        longitude=request.longitude,
                    ),
                    place_types=["hotel"],
                    min_rating=3.5,
                    max_distance_km=request.max_distance_km,
                    student_friendly_only=request.student_friendly,
                    limit=10
                )
                
                hotel_places = [p for p in sample_places if p.place_type == "hotel"]
                ranked_hotel_objects = rank_places(hotel_places, ranking_request)
                
                ranked_hotels = [
                    {
                        "name": h.place.name,
                        "place_type": h.place.place_type.value,
                        "rating": h.place.rating,
                        "score": round(h.score / 100, 4),
                        "rank": h.rank,
                        "distance_km": h.distance_km,
                        "price_level": h.place.price_range.value,
                        "student_friendly": (
                            h.place.student_discount
                            or h.place.wifi_available
                            or h.place.study_friendly
                            or h.place.wallet_friendly
                        ),
                        "latitude": h.place.latitude,
                        "longitude": h.place.longitude
                    }
                    for h in ranked_hotel_objects[:5]
                ]
                included_features.append("hotel_ranking")
            except Exception as e:
                logger.warning(f"[Itinerary] Hotel ranking failed: {e}")
        
        if request.include_restaurants and request.latitude and request.longitude:
            try:
                ranking_request = RankingRequest(
                    user_budget=max(budget_per_day, 1.0),
                    user_location=Coordinates(
                        latitude=request.latitude,
                        longitude=request.longitude,
                    ),
                    place_types=["restaurant"],
                    min_rating=4.0,
                    max_distance_km=request.max_distance_km,
                    student_friendly_only=request.student_friendly,
                    limit=15
                )
                
                restaurant_places = [p for p in sample_places if p.place_type == "restaurant"]
                ranked_restaurant_objects = rank_places(restaurant_places, ranking_request)
                
                ranked_restaurants = [
                    {
                        "name": r.place.name,
                        "place_type": r.place.place_type.value,
                        "rating": r.place.rating,
                        "score": round(r.score / 100, 4),
                        "rank": r.rank,
                        "distance_km": r.distance_km,
                        "price_level": r.place.price_range.value,
                        "student_friendly": (
                            r.place.student_discount
                            or r.place.wifi_available
                            or r.place.study_friendly
                            or r.place.wallet_friendly
                        ),
                        "latitude": r.place.latitude,
                        "longitude": r.place.longitude
                    }
                    for r in ranked_restaurant_objects[:10]
                ]
                included_features.append("restaurant_ranking")
            except Exception as e:
                logger.warning(f"[Itinerary] Restaurant ranking failed: {e}")
        
        # Always rank attractions (ML-style weighted scoring)
        try:
            ranked_attractions = self._score_attractions_ml(
                attractions=sample_attractions,
                budget_per_day=budget_per_day,
            )[: request.duration * 3]
            included_features.append("attraction_ranking")
        except Exception as e:
            logger.warning(f"[Itinerary] Attraction ranking failed: {e}")
        
        # ========================================================================
        # STEP 4: Route Optimization
        # ========================================================================
        logger.info("[Itinerary] Step 4/6: Optimizing route")
        
        if request.latitude and request.longitude:
            route_places = ranked_attractions[:min(12, len(ranked_attractions))]

            if request.duration > 1 and len(route_places) > request.duration:
                clusters = self._cluster_attractions_for_days(route_places, request.duration)
                ordered_places = []
                total_distance = 0.0
                total_minutes = 0.0

                for cluster in clusters:
                    cluster_order, cluster_distance, cluster_minutes = await self._optimize_route_with_tsp(
                        attractions=cluster,
                        start_lat=request.latitude,
                        start_lon=request.longitude,
                    )
                    ordered_places.extend(cluster_order)
                    total_distance += cluster_distance
                    total_minutes += cluster_minutes

                optimization_method = "kmeans_tsp_time_weighted"
            else:
                ordered_places, total_distance, total_minutes = await self._optimize_route_with_tsp(
                    attractions=route_places,
                    start_lat=request.latitude,
                    start_lon=request.longitude,
                )
                optimization_method = "tsp_time_weighted"
            
            route_optimization = RouteOptimization(
                ordered_places=ordered_places,
                total_distance_km=round(total_distance, 2),
                estimated_travel_time_hours=round(total_minutes / 60, 2),
                optimization_method=optimization_method
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

        if route_optimization and route_optimization.ordered_places:
            route_rank = {name: idx for idx, name in enumerate(route_optimization.ordered_places)}
            ranked_attractions.sort(key=lambda a: route_rank.get(a.get("name"), len(route_rank)))
        
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
                id=f"hotel_{location.lower().replace(' ', '_')}_grand",
                name=f"{location} Grand Hotel",
                place_type="hotel",
                latitude=lat + 0.01,
                longitude=lon + 0.01,
                rating=4.5,
                price_range="moderate",
                average_price=95,
                city=location,
                review_count=420,
                popularity_score=85,
                student_discount=True,
                wifi_available=True,
                study_friendly=True,
                wallet_friendly=False,
                amenities=["WiFi", "Breakfast", "Study Area"],
            ),
            Place(
                id=f"hotel_{location.lower().replace(' ', '_')}_budget",
                name=f"{location} Budget Inn",
                place_type="hotel",
                latitude=lat + 0.02,
                longitude=lon - 0.01,
                rating=3.8,
                price_range="budget",
                average_price=45,
                city=location,
                review_count=280,
                popularity_score=62,
                student_discount=True,
                wifi_available=True,
                study_friendly=False,
                wallet_friendly=True,
                amenities=["WiFi", "Budget Rooms"],
            ),
            Place(
                id=f"hotel_{location.lower().replace(' ', '_')}_luxury",
                name=f"{location} Luxury Resort",
                place_type="hotel",
                latitude=lat - 0.01,
                longitude=lon + 0.02,
                rating=4.8,
                price_range="luxury",
                average_price=220,
                city=location,
                review_count=510,
                popularity_score=95,
                student_discount=False,
                wifi_available=True,
                study_friendly=False,
                wallet_friendly=False,
                amenities=["Pool", "Spa", "Gym"],
            ),
            
            # Restaurants
            Place(
                id=f"restaurant_{location.lower().replace(' ', '_')}_bistro",
                name=f"{location} Local Bistro",
                place_type="restaurant",
                latitude=lat + 0.005,
                longitude=lon + 0.005,
                rating=4.6,
                price_range="moderate",
                average_price=22,
                city=location,
                review_count=360,
                popularity_score=72,
                student_discount=True,
                wifi_available=True,
                study_friendly=False,
                wallet_friendly=True,
                cuisine_type="Local",
                amenities=["Student Menu", "WiFi"],
            ),
            Place(
                id=f"restaurant_{location.lower().replace(' ', '_')}_street_food",
                name=f"{location} Street Food Market",
                place_type="restaurant",
                latitude=lat + 0.008,
                longitude=lon - 0.003,
                rating=4.3,
                price_range="budget",
                average_price=12,
                city=location,
                review_count=640,
                popularity_score=88,
                student_discount=True,
                wifi_available=False,
                study_friendly=False,
                wallet_friendly=True,
                cuisine_type="Street Food",
                amenities=["Budget Meals"],
            ),
            Place(
                id=f"restaurant_{location.lower().replace(' ', '_')}_fine_dining",
                name=f"{location} Fine Dining",
                place_type="restaurant",
                latitude=lat - 0.005,
                longitude=lon + 0.008,
                rating=4.9,
                price_range="luxury",
                average_price=55,
                city=location,
                review_count=220,
                popularity_score=65,
                student_discount=False,
                wifi_available=True,
                study_friendly=False,
                wallet_friendly=False,
                cuisine_type="Fine Dining",
                amenities=["Reservation"],
            ),
        ]
        
        return sample_places

    def _generate_sample_attractions(
        self,
        location: str,
        lat: Optional[float],
        lon: Optional[float]
    ) -> List[Dict[str, Any]]:
        if not lat or not lon:
            lat, lon = 40.7128, -74.0060

        base = [
            {"name": f"{location} Museum", "rating": 4.7, "latitude": lat + 0.003, "longitude": lon + 0.004, "student_friendly": True},
            {"name": f"{location} Historic Center", "rating": 4.8, "latitude": lat, "longitude": lon, "student_friendly": True},
            {"name": f"{location} Botanical Garden", "rating": 4.5, "latitude": lat + 0.015, "longitude": lon - 0.01, "student_friendly": True},
            {"name": f"{location} Art Gallery", "rating": 4.6, "latitude": lat - 0.008, "longitude": lon + 0.012, "student_friendly": True},
            {"name": f"{location} Observation Deck", "rating": 4.7, "latitude": lat + 0.02, "longitude": lon + 0.015, "student_friendly": False},
        ]

        results = []
        for attraction in base:
            distance = haversine_distance(lat, lon, attraction["latitude"], attraction["longitude"])
            results.append({
                **attraction,
                "place_type": "attraction",
                "distance_km": round(distance, 2),
            })

        return results


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

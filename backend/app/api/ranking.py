"""
Ranking API - Multi-criteria place ranking endpoint
Production-ready endpoint for ranking hotels, cafes, and restaurants
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.models.ranking import (
    Place,
    RankedPlace,
    RankingRequest,
    RankingResponse,
    PlaceType,
    PriceRange,
    Coordinates
)
from app.models.responses import SuccessResponse
from app.services.ranking_service import ranking_service
from app.services.cache_service import CacheService

# Initialize router
router = APIRouter()

# Cache for ranking results (5 minutes TTL)
ranking_cache = CacheService(max_size=500, default_ttl=300)


# ============================================================================
# SAMPLE DATA GENERATOR (For testing without external database)
# ============================================================================

def generate_sample_places(city: str = "New York") -> List[Place]:
    """
    Generate sample places for demonstration
    In production, this would query from database
    """
    return [
        # Hotels
        Place(
            id="hotel_001",
            name="Student Inn Downtown",
            place_type=PlaceType.HOTEL,
            rating=4.3,
            price_range=PriceRange.BUDGET,
            average_price=45.0,
            latitude=40.7128,
            longitude=-74.0060,
            address="123 Student St",
            city=city,
            review_count=234,
            popularity_score=72.5,
            student_discount=True,
            wifi_available=True,
            study_friendly=False,
            wallet_friendly=True,
            amenities=["WiFi", "Breakfast", "24/7 Reception"],
            opening_hours="24/7"
        ),
        Place(
            id="hotel_002",
            name="Luxury Grand Hotel",
            place_type=PlaceType.HOTEL,
            rating=4.8,
            price_range=PriceRange.LUXURY,
            average_price=250.0,
            latitude=40.7589,
            longitude=-73.9851,
            address="456 Luxury Ave",
            city=city,
            review_count=892,
            popularity_score=95.2,
            student_discount=False,
            wifi_available=True,
            study_friendly=False,
            wallet_friendly=False,
            amenities=["WiFi", "Spa", "Pool", "Gym", "Restaurant", "Concierge"],
            opening_hours="24/7"
        ),
        Place(
            id="hotel_003",
            name="Midtown Comfort Stay",
            place_type=PlaceType.HOTEL,
            rating=4.1,
            price_range=PriceRange.MODERATE,
            average_price=85.0,
            latitude=40.7549,
            longitude=-73.9840,
            address="789 Midtown Blvd",
            city=city,
            review_count=456,
            popularity_score=68.0,
            student_discount=False,
            wifi_available=True,
            study_friendly=False,
            wallet_friendly=True,
            amenities=["WiFi", "Parking", "Breakfast"],
            opening_hours="24/7"
        ),
        
        # Cafes
        Place(
            id="cafe_001",
            name="The Study Corner Cafe",
            place_type=PlaceType.CAFE,
            rating=4.6,
            price_range=PriceRange.BUDGET,
            average_price=8.5,
            latitude=40.7282,
            longitude=-73.9942,
            address="321 Coffee Lane",
            city=city,
            review_count=567,
            popularity_score=85.3,
            student_discount=True,
            wifi_available=True,
            study_friendly=True,
            wallet_friendly=True,
            cuisine_type="Coffee & Pastries",
            amenities=["WiFi", "Power Outlets", "Quiet Space", "Books"],
            opening_hours="6:00 AM - 11:00 PM"
        ),
        Place(
            id="cafe_002",
            name="Artisan Roasters",
            place_type=PlaceType.CAFE,
            rating=4.7,
            price_range=PriceRange.MODERATE,
            average_price=12.0,
            latitude=40.7410,
            longitude=-73.9896,
            address="555 Artisan Way",
            city=city,
            review_count=823,
            popularity_score=91.7,
            student_discount=False,
            wifi_available=True,
            study_friendly=False,
            wallet_friendly=False,
            cuisine_type="Specialty Coffee",
            amenities=["WiFi", "Outdoor Seating", "Pastries"],
            opening_hours="7:00 AM - 8:00 PM"
        ),
        Place(
            id="cafe_003",
            name="Campus Brew",
            place_type=PlaceType.CAFE,
            rating=4.2,
            price_range=PriceRange.BUDGET,
            average_price=6.5,
            latitude=40.7180,
            longitude=-74.0020,
            address="111 Campus Dr",
            city=city,
            review_count=345,
            popularity_score=72.0,
            student_discount=True,
            wifi_available=True,
            study_friendly=True,
            wallet_friendly=True,
            cuisine_type="Coffee & Snacks",
            amenities=["WiFi", "Power Outlets", "Student Discounts"],
            opening_hours="6:00 AM - 10:00 PM"
        ),
        
        # Restaurants
        Place(
            id="restaurant_001",
            name="Budget Bites Eatery",
            place_type=PlaceType.RESTAURANT,
            rating=4.0,
            price_range=PriceRange.BUDGET,
            average_price=15.0,
            latitude=40.7350,
            longitude=-73.9950,
            address="222 Food St",
            city=city,
            review_count=412,
            popularity_score=65.5,
            student_discount=True,
            wifi_available=True,
            study_friendly=False,
            wallet_friendly=True,
            cuisine_type="American",
            amenities=["WiFi", "Takeout", "Student Menu"],
            opening_hours="11:00 AM - 10:00 PM"
        ),
        Place(
            id="restaurant_002",
            name="Fine Dining Experience",
            place_type=PlaceType.RESTAURANT,
            rating=4.9,
            price_range=PriceRange.LUXURY,
            average_price=120.0,
            latitude=40.7614,
            longitude=-73.9776,
            address="888 Gourmet Ave",
            city=city,
            review_count=1234,
            popularity_score=98.5,
            student_discount=False,
            wifi_available=False,
            study_friendly=False,
            wallet_friendly=False,
            cuisine_type="French",
            amenities=["Reservations Required", "Dress Code", "Wine Cellar"],
            opening_hours="5:00 PM - 11:00 PM"
        ),
        Place(
            id="restaurant_003",
            name="Casual Family Restaurant",
            place_type=PlaceType.RESTAURANT,
            rating=4.3,
            price_range=PriceRange.MODERATE,
            average_price=25.0,
            latitude=40.7420,
            longitude=-73.9880,
            address="444 Family Blvd",
            city=city,
            review_count=678,
            popularity_score=78.2,
            student_discount=False,
            wifi_available=True,
            study_friendly=False,
            wallet_friendly=True,
            cuisine_type="Italian",
            amenities=["WiFi", "Outdoor Seating", "Kids Menu", "Takeout"],
            opening_hours="11:00 AM - 10:00 PM"
        ),
        Place(
            id="restaurant_004",
            name="Quick Bite Express",
            place_type=PlaceType.RESTAURANT,
            rating=3.8,
            price_range=PriceRange.BUDGET,
            average_price=10.0,
            latitude=40.7200,
            longitude=-74.0000,
            address="333 Fast Food Ln",
            city=city,
            review_count=189,
            popularity_score=58.0,
            student_discount=True,
            wifi_available=True,
            study_friendly=False,
            wallet_friendly=True,
            cuisine_type="Fast Food",
            amenities=["WiFi", "Quick Service", "Delivery"],
            opening_hours="10:00 AM - 11:00 PM"
        ),
    ]


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/ranked-places", response_model=SuccessResponse[RankingResponse])
async def get_ranked_places(
    request: RankingRequest
):
    """
    Get ranked places using multi-criteria weighted scoring
    
    **Scoring Formula:**
    ```
    Total Score = 0.4 × rating_score 
                + 0.25 × budget_match_score 
                + 0.2 × distance_score 
                + 0.1 × popularity_score 
                + 0.05 × student_friendly_score
    ```
    
    **Request Parameters:**
    - **user_budget**: Maximum budget per person/night (required)
    - **user_location**: Current location coordinates (required)
    - **place_types**: Types to include (hotel/cafe/restaurant)
    - **max_distance_km**: Maximum distance filter (default: 10 km)
    - **min_rating**: Minimum rating filter (0-5)
    - **student_friendly_only**: Filter for student-friendly places
    - **limit**: Maximum number of results (1-100)
    
    **Response:**
    - Ranked list of places with scores (0-100)
    - Detailed score breakdown for each place
    - Match reasons and warnings
    - Distance from user location
    
    **Example Request:**
    ```json
    {
      "user_budget": 50.0,
      "user_location": {"latitude": 40.7128, "longitude": -74.0060},
      "place_types": ["cafe", "restaurant"],
      "max_distance_km": 5.0,
      "min_rating": 3.5,
      "student_friendly_only": true,
      "limit": 10
    }
    ```
    
    **Caching:**
    - Results cached for 5 minutes
    - Cache key based on request parameters
    """
    try:
        # Generate cache key from request
        cache_key = f"ranking:{request.user_budget}:{request.user_location.latitude},{request.user_location.longitude}:{','.join([pt.value for pt in request.place_types])}:{request.limit}"
        
        # Check cache first
        cached_result = ranking_cache.get(cache_key)
        if cached_result:
            return SuccessResponse(
                message="Ranked places retrieved from cache",
                data=cached_result
            )
        
        # Get all available places (in production, query from database)
        all_places = generate_sample_places()
        
        # Rank places using the service
        ranked_places = ranking_service.rank_places(
            places=all_places,
            request=request
        )
        
        # Create response
        response = RankingResponse(
            places=ranked_places,
            total_candidates=len(all_places),
            filters_applied={
                "place_types": [pt.value for pt in request.place_types],
                "max_distance_km": request.max_distance_km,
                "min_rating": request.min_rating,
                "user_budget": request.user_budget,
                "student_friendly_only": request.student_friendly_only
            },
            search_location=request.user_location,
            timestamp=datetime.utcnow()
        )
        
        # Cache the result
        ranking_cache.set(cache_key, response, ttl=300)
        
        return SuccessResponse(
            message=f"Successfully ranked {len(ranked_places)} places out of {len(all_places)} candidates",
            data=response
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rank places: {str(e)}"
        )


@router.get("/ranked-places/sample", response_model=SuccessResponse[List[Place]])
async def get_sample_places(
    city: str = Query(default="New York", description="City name")
):
    """
    Get sample places for testing (without ranking)
    
    Returns the raw place data that would be ranked by the main endpoint.
    Useful for understanding the data structure and available places.
    """
    try:
        places = generate_sample_places(city)
        return SuccessResponse(
            message=f"Retrieved {len(places)} sample places",
            data=places
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sample places: {str(e)}"
        )


@router.get("/ranked-places/weights", response_model=SuccessResponse[dict])
async def get_scoring_weights():
    """
    Get the current scoring weights configuration
    
    Returns the weights used in the ranking algorithm.
    Useful for understanding how scores are calculated.
    """
    from app.services.ranking_service import (
        WEIGHT_RATING,
        WEIGHT_BUDGET,
        WEIGHT_DISTANCE,
        WEIGHT_POPULARITY,
        WEIGHT_STUDENT
    )
    
    weights = {
        "rating": {
            "weight": WEIGHT_RATING,
            "percentage": f"{WEIGHT_RATING * 100}%",
            "description": "Place rating quality (0-5 scale)"
        },
        "budget_match": {
            "weight": WEIGHT_BUDGET,
            "percentage": f"{WEIGHT_BUDGET * 100}%",
            "description": "Alignment with user budget"
        },
        "distance": {
            "weight": WEIGHT_DISTANCE,
            "percentage": f"{WEIGHT_DISTANCE * 100}%",
            "description": "Proximity to user location"
        },
        "popularity": {
            "weight": WEIGHT_POPULARITY,
            "percentage": f"{WEIGHT_POPULARITY * 100}%",
            "description": "Review count and popularity score"
        },
        "student_friendly": {
            "weight": WEIGHT_STUDENT,
            "percentage": f"{WEIGHT_STUDENT * 100}%",
            "description": "Student-friendly features and discounts"
        },
        "total": {
            "sum": WEIGHT_RATING + WEIGHT_BUDGET + WEIGHT_DISTANCE + WEIGHT_POPULARITY + WEIGHT_STUDENT,
            "note": "All weights sum to 1.0"
        },
        "formula": "Total Score = 0.4×rating + 0.25×budget + 0.2×distance + 0.1×popularity + 0.05×student"
    }
    
    return SuccessResponse(
        message="Current scoring weights",
        data=weights
    )

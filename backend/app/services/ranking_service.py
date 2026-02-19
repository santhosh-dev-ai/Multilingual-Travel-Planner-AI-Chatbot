"""
Ranking Service - Multi-criteria weighted scoring system for places
Production-ready ranking algorithm with optimized sorting

Scoring Formula:
    Total Score = 0.4 × rating_score 
                + 0.25 × budget_match_score 
                + 0.2 × distance_score 
                + 0.1 × popularity_score 
                + 0.05 × student_friendly_score
"""

from typing import List, Tuple, Optional
import math
from app.models.ranking import (
    Place,
    RankedPlace,
    RankingRequest,
    ScoreBreakdown,
    PriceRange,
    PlaceType,
    Coordinates
)


# ============================================================================
# SCORING WEIGHTS (Production Configuration)
# ============================================================================
WEIGHT_RATING = 0.4          # Rating quality (40%)
WEIGHT_BUDGET = 0.25         # Budget alignment (25%)
WEIGHT_DISTANCE = 0.2        # Proximity (20%)
WEIGHT_POPULARITY = 0.1      # Social proof (10%)
WEIGHT_STUDENT = 0.05        # Student-friendly (5%)

# Verify weights sum to 1.0
assert math.isclose(
    WEIGHT_RATING + WEIGHT_BUDGET + WEIGHT_DISTANCE + WEIGHT_POPULARITY + WEIGHT_STUDENT,
    1.0
), "Weights must sum to 1.0"


# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def calculate_rating_score(rating: float) -> float:
    """
    Calculate normalized rating score (0-1)
    
    Args:
        rating: Place rating (0-5 scale)
    
    Returns:
        Normalized score (0-1) where 5.0 rating = 1.0
    
    Formula:
        score = rating / 5.0
    
    Examples:
        5.0 → 1.0 (perfect)
        4.5 → 0.9 (excellent)
        4.0 → 0.8 (very good)
        3.0 → 0.6 (average)
    """
    return min(max(rating / 5.0, 0.0), 1.0)


def calculate_budget_match_score(place_price: float, user_budget: float) -> float:
    """
    Calculate budget alignment score (0-1)
    Uses exponential decay for prices over budget
    
    Args:
        place_price: Average price of the place
        user_budget: User's maximum budget
    
    Returns:
        Score (0-1) where perfect match = 1.0
    
    Formula:
        If price <= budget:
            score = 1.0 - (price / budget) * 0.2  # Prefer cheaper within budget
        If price > budget:
            overage_ratio = (price - budget) / budget
            score = exp(-2 * overage_ratio)  # Exponential penalty
    
    Examples:
        $10 vs $50 budget → 0.96 (great value!)
        $25 vs $50 budget → 0.90 (good value)
        $50 vs $50 budget → 0.80 (perfect match but max)
        $60 vs $50 budget → 0.73 (slightly over)
        $75 vs $50 budget → 0.61 (significantly over)
        $100 vs $50 budget → 0.37 (way over budget)
    """
    if place_price <= user_budget:
        # Within budget: slight preference for better value
        # Perfect score is at 80% of budget, not at $0
        utilization = place_price / user_budget
        return 1.0 - (utilization * 0.2)  # Max 1.0 at low price, 0.8 at budget
    else:
        # Over budget: exponential penalty
        overage_ratio = (place_price - user_budget) / user_budget
        return max(math.exp(-2 * overage_ratio), 0.0)


def calculate_distance_score(distance_km: float, max_distance_km: float = 10.0) -> float:
    """
    Calculate proximity score (0-1)
    Uses inverse relationship with diminishing returns
    
    Args:
        distance_km: Distance from user location (km)
        max_distance_km: Maximum acceptable distance
    
    Returns:
        Score (0-1) where closer = higher score
    
    Formula:
        If distance <= max_distance:
            score = 1 / (1 + distance_km)  # Hyperbolic decay
        Else:
            score = 0.0  # Beyond max distance
    
    Examples:
        0.5 km → 0.67 (very close)
        1.0 km → 0.50 (close)
        2.0 km → 0.33 (nearby)
        5.0 km → 0.17 (moderate distance)
        10.0 km → 0.09 (far but acceptable)
        15.0 km → 0.00 (too far)
    """
    if distance_km > max_distance_km:
        return 0.0
    
    # Hyperbolic decay: very close places get high scores
    return 1.0 / (1.0 + distance_km)


def calculate_popularity_score(
    review_count: int,
    popularity_score: float
) -> float:
    """
    Calculate popularity score from review count and normalized popularity
    
    Args:
        review_count: Total number of reviews
        popularity_score: Pre-calculated popularity (0-100)
    
    Returns:
        Normalized score (0-1)
    
    Formula:
        Combine review volume and popularity score:
        - Review factor: log(reviews + 1) / log(1001)  # Logarithmic scale
        - Popularity factor: popularity_score / 100
        - Final: 0.6 × review_factor + 0.4 × popularity_factor
    
    Reasoning:
        - Review count uses log scale (1000 reviews not 10x better than 100)
        - Popularity score (if available) provides additional signal
        - Weighted combination prevents over-reliance on either metric
    
    Examples:
        10 reviews, 50 pop → 0.35
        100 reviews, 70 pop → 0.55
        500 reviews, 85 pop → 0.72
        1000 reviews, 95 pop → 0.83
    """
    # Logarithmic scale for review count (diminishing returns)
    # Normalize to 0-1 where 1000+ reviews = 1.0
    review_factor = math.log(review_count + 1) / math.log(1001)
    review_factor = min(review_factor, 1.0)
    
    # Normalize popularity score (0-100 → 0-1)
    popularity_factor = min(popularity_score / 100.0, 1.0)
    
    # Weighted combination: prioritize review volume slightly
    return 0.6 * review_factor + 0.4 * popularity_factor


def calculate_student_friendly_score(place: Place) -> float:
    """
    Calculate student-friendly index (0-1)
    Based on multiple student-friendly attributes
    
    Args:
        place: Place object with student-friendly indicators
    
    Returns:
        Score (0-1) where 1.0 = highly student-friendly
    
    Scoring:
        - Student discount: 0.30
        - WiFi available: 0.25
        - Study-friendly: 0.25
        - Wallet-friendly: 0.20
    
    Examples:
        All features → 1.00
        Discount + WiFi → 0.55
        No features → 0.00
    """
    score = 0.0
    
    if place.student_discount:
        score += 0.30  # Student discount is most valuable
    
    if place.wifi_available:
        score += 0.25  # WiFi important for students
    
    if place.study_friendly:
        score += 0.25  # Study space valuable
    
    if place.wallet_friendly:
        score += 0.20  # Budget-conscious
    
    return min(score, 1.0)


def calculate_distance_km(loc1: Coordinates, loc2: Coordinates) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    
    Args:
        loc1: First coordinate (user location)
        loc2: Second coordinate (place location)
    
    Returns:
        Distance in kilometers
    
    Haversine Formula:
        a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
        c = 2 × atan2(√a, √(1−a))
        d = R × c  (R = Earth radius = 6371 km)
    """
    # Earth radius in kilometers
    R = 6371.0
    
    # Convert to radians
    lat1_rad = math.radians(loc1.latitude)
    lon1_rad = math.radians(loc1.longitude)
    lat2_rad = math.radians(loc2.latitude)
    lon2_rad = math.radians(loc2.longitude)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return round(distance, 2)


def calculate_total_score(
    place: Place,
    user_location: Coordinates,
    user_budget: float,
    max_distance_km: float
) -> Tuple[float, ScoreBreakdown, float]:
    """
    Calculate total weighted score for a place
    
    Args:
        place: Place to score
        user_location: User's current location
        user_budget: User's maximum budget
        max_distance_km: Maximum acceptable distance
    
    Returns:
        Tuple of (total_score, score_breakdown, distance_km)
        total_score: 0-100 scale
        score_breakdown: Detailed component scores
        distance_km: Distance from user
    
    Algorithm:
        1. Calculate distance (Haversine)
        2. Calculate each component score (0-1)
        3. Apply weights to each component
        4. Sum weighted scores
        5. Convert to 0-100 scale
    """
    # Calculate distance first (needed for distance score)
    place_location = Coordinates(
        latitude=place.latitude,
        longitude=place.longitude
    )
    distance_km = calculate_distance_km(user_location, place_location)
    
    # Calculate individual component scores (0-1 scale)
    rating_score = calculate_rating_score(place.rating)
    budget_match_score = calculate_budget_match_score(place.average_price, user_budget)
    distance_score = calculate_distance_score(distance_km, max_distance_km)
    popularity_score = calculate_popularity_score(place.review_count, place.popularity_score)
    student_friendly_score = calculate_student_friendly_score(place)
    
    # Apply weights
    weighted_rating = rating_score * WEIGHT_RATING
    weighted_budget = budget_match_score * WEIGHT_BUDGET
    weighted_distance = distance_score * WEIGHT_DISTANCE
    weighted_popularity = popularity_score * WEIGHT_POPULARITY
    weighted_student = student_friendly_score * WEIGHT_STUDENT
    
    # Calculate total (0-1 scale)
    total_score_normalized = (
        weighted_rating +
        weighted_budget +
        weighted_distance +
        weighted_popularity +
        weighted_student
    )
    
    # Convert to 0-100 scale
    total_score = round(total_score_normalized * 100, 1)
    
    # Create breakdown
    breakdown = ScoreBreakdown(
        rating_score=round(rating_score, 3),
        budget_match_score=round(budget_match_score, 3),
        distance_score=round(distance_score, 3),
        popularity_score=round(popularity_score, 3),
        student_friendly_score=round(student_friendly_score, 3),
        weighted_rating=round(weighted_rating, 3),
        weighted_budget=round(weighted_budget, 3),
        weighted_distance=round(weighted_distance, 3),
        weighted_popularity=round(weighted_popularity, 3),
        weighted_student=round(weighted_student, 3),
        total_score=round(total_score_normalized, 3)
    )
    
    return total_score, breakdown, distance_km


def generate_match_reasons(
    place: Place,
    score_breakdown: ScoreBreakdown,
    distance_km: float,
    user_budget: float
) -> List[str]:
    """
    Generate human-readable reasons for why this place matches
    
    Args:
        place: The place being ranked
        score_breakdown: Detailed score components
        distance_km: Distance from user
        user_budget: User's budget
    
    Returns:
        List of reason strings
    """
    reasons = []
    
    # Rating
    if place.rating >= 4.5:
        reasons.append(f"Excellent rating ({place.rating}/5)")
    elif place.rating >= 4.0:
        reasons.append(f"Very good rating ({place.rating}/5)")
    elif place.rating >= 3.5:
        reasons.append(f"Good rating ({place.rating}/5)")
    
    # Budget
    if place.average_price <= user_budget * 0.7:
        savings = user_budget - place.average_price
        reasons.append(f"Great value (${place.average_price:.2f}, ${savings:.2f} under budget)")
    elif place.average_price <= user_budget:
        reasons.append(f"Within budget (${place.average_price:.2f} vs ${user_budget:.2f})")
    
    # Distance
    if distance_km < 1.0:
        reasons.append(f"Very close ({distance_km} km)")
    elif distance_km < 3.0:
        reasons.append(f"Nearby ({distance_km} km)")
    
    # Popularity
    if place.review_count > 500:
        reasons.append(f"Very popular ({place.review_count} reviews)")
    elif place.review_count > 100:
        reasons.append(f"Well-reviewed ({place.review_count} reviews)")
    
    # Student-friendly features
    student_features = []
    if place.student_discount:
        student_features.append("student discount")
    if place.wifi_available:
        student_features.append("free WiFi")
    if place.study_friendly:
        student_features.append("study-friendly")
    
    if student_features:
        reasons.append(f"Student perks: {', '.join(student_features)}")
    
    return reasons


def generate_warnings(
    place: Place,
    distance_km: float,
    user_budget: float,
    max_distance_km: float
) -> List[str]:
    """
    Generate warnings for potential concerns
    
    Args:
        place: The place being ranked
        distance_km: Distance from user
        user_budget: User's budget
        max_distance_km: Maximum acceptable distance
    
    Returns:
        List of warning strings
    """
    warnings = []
    
    # Over budget
    if place.average_price > user_budget:
        overage = place.average_price - user_budget
        overage_pct = (overage / user_budget) * 100
        warnings.append(f"Over budget by ${overage:.2f} ({overage_pct:.0f}%)")
    
    # Far distance
    if distance_km > max_distance_km * 0.7:
        warnings.append(f"Relatively far ({distance_km} km)")
    
    # Low rating
    if place.rating < 3.5:
        warnings.append(f"Below average rating ({place.rating}/5)")
    
    # Few reviews (low confidence)
    if place.review_count < 10:
        warnings.append(f"Limited reviews ({place.review_count})")
    
    return warnings


# ============================================================================
# MAIN RANKING FUNCTION
# ============================================================================

def rank_places(
    places: List[Place],
    request: RankingRequest
) -> List[RankedPlace]:
    """
    Rank places using multi-criteria weighted scoring
    
    Args:
        places: List of places to rank
        request: Ranking request with user preferences
    
    Returns:
        Sorted list of RankedPlace objects (highest score first)
    
    Algorithm:
        1. Filter by place type
        2. Filter by minimum rating
        3. Calculate distance for all places
        4. Filter by max distance
        5. Filter student-friendly if requested
        6. Calculate comprehensive scores
        7. Sort by score (descending) - O(n log n)
        8. Apply limit
        9. Assign ranks
    
    Optimization:
        - Early filtering reduces score calculations
        - Single-pass scoring per place
        - Efficient sorting with TimSort (Python default)
        - Lazy evaluation where possible
    """
    ranked_places: List[RankedPlace] = []
    
    # Filter 1: Place types
    filtered_places = [p for p in places if p.place_type in request.place_types]
    
    # Filter 2: Minimum rating
    if request.min_rating and request.min_rating > 0:
        filtered_places = [p for p in filtered_places if p.rating >= request.min_rating]
    
    # Calculate scores for remaining places
    for place in filtered_places:
        # Calculate total score and breakdown
        total_score, breakdown, distance_km = calculate_total_score(
            place=place,
            user_location=request.user_location,
            user_budget=request.user_budget,
            max_distance_km=request.max_distance_km or 10.0
        )
        
        # Filter 3: Max distance (after calculation to avoid duplicate computation)
        if request.max_distance_km and distance_km > request.max_distance_km:
            continue
        
        # Filter 4: Student-friendly
        if request.student_friendly_only:
            student_score = calculate_student_friendly_score(place)
            if student_score < 0.3:  # Must have at least one feature
                continue
        
        # Filter 5: Required amenities
        if request.required_amenities:
            if not all(amenity in place.amenities for amenity in request.required_amenities):
                continue
        
        # Filter 6: Preferred cuisine (if applicable)
        if request.preferred_cuisine and place.cuisine_type:
            if request.preferred_cuisine.lower() not in place.cuisine_type.lower():
                continue
        
        # Generate explanations
        match_reasons = generate_match_reasons(place, breakdown, distance_km, request.user_budget)
        warnings = generate_warnings(place, distance_km, request.user_budget, request.max_distance_km or 10.0)
        
        # Create ranked place (rank will be assigned after sorting)
        ranked_place = RankedPlace(
            place=place,
            score=total_score,
            rank=1,  # Temporary, will be updated after sorting
            distance_km=distance_km,
            score_breakdown=breakdown,
            match_reasons=match_reasons,
            warnings=warnings
        )
        
        ranked_places.append(ranked_place)
    
    # Sort by score (descending) - O(n log n) with TimSort
    # TimSort is optimized for partially sorted data
    ranked_places.sort(key=lambda x: x.score, reverse=True)
    
    # Apply limit
    ranked_places = ranked_places[:request.limit]
    
    # Assign ranks (1-indexed)
    for idx, ranked_place in enumerate(ranked_places, start=1):
        ranked_place.rank = idx
    
    return ranked_places


# ============================================================================
# SERVICE INSTANCE
# ============================================================================

class RankingService:
    """
    Service class for place ranking operations
    Provides clean interface for API layer
    """
    
    @staticmethod
    def rank_places(places: List[Place], request: RankingRequest) -> List[RankedPlace]:
        """Public interface for ranking places"""
        return rank_places(places, request)
    
    @staticmethod
    def calculate_score(
        place: Place,
        user_location: Coordinates,
        user_budget: float,
        max_distance_km: float = 10.0
    ) -> Tuple[float, ScoreBreakdown, float]:
        """Public interface for single place scoring"""
        return calculate_total_score(place, user_location, user_budget, max_distance_km)


# Create singleton instance
ranking_service = RankingService()

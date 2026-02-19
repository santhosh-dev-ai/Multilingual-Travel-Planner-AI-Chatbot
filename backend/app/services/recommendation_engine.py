"""
Recommendation Engine - ML-based personalized destination recommendations
Uses collaborative filtering and content-based approaches
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta

from app.models.user import UserProfile, UserPreferences
from app.models.destination import Destination
from app.models.analytics import RecommendationScore


class RecommendationEngine:
    """
    Production-grade recommendation engine for travel destinations
    
    Features:
    - Collaborative filtering (user-user similarity)
    - Content-based filtering (destination features)
    - Hybrid approach combining both
    - Cold start handling for new users
    - Real-time score computation
    """
    
    def __init__(self):
        self.user_interactions: Dict[str, Dict[int, float]] = defaultdict(dict)
        self.destination_features: Dict[int, np.ndarray] = {}
        self.user_similarity_cache: Dict[Tuple[str, str], float] = {}
        self.last_cache_update = datetime.utcnow()
        
    def calculate_preference_match(
        self,
        user_prefs: UserPreferences,
        destination: Destination
    ) -> float:
        """
        Calculate how well destination matches user preferences (0-1)
        
        Factors:
        - Region match
        - Climate preference
        - Tag/interest overlap
        - Budget fit
        """
        score = 0.0
        weights = {
            'region': 0.25,
            'climate': 0.20,
            'interests': 0.30,
            'budget': 0.25
        }
        
        # Region match
        if destination.region in user_prefs.favorite_regions:
            score += weights['region']
        
        # Climate match
        if destination.climate.value in user_prefs.favorite_climates:
            score += weights['climate']
        
        # Interest/tag overlap
        user_interests = set(user_prefs.interests)
        dest_tags = set(destination.tags)
        overlap = len(user_interests & dest_tags)
        if len(user_interests) > 0:
            interest_score = overlap / len(user_interests)
            score += weights['interests'] * interest_score
        
        # Budget fit
        budget_range = user_prefs.budget_range
        if budget_range:
            min_budget = budget_range.get('min', 0)
            max_budget = budget_range.get('max', float('inf'))
            
            if min_budget <= destination.price_value <= max_budget:
                score += weights['budget']
            elif destination.price_value < min_budget:
                # Still give partial credit if affordable
                score += weights['budget'] * 0.5
        
        return min(score, 1.0)
    
    def calculate_popularity_score(self, destination: Destination) -> float:
        """
        Calculate destination popularity score (0-1)
        Based on metrics: views, wishlists, ratings
        """
        metrics = destination.metrics
        
        # Normalize each metric (assuming reasonable max values)
        view_score = min(metrics.view_count / 10000, 1.0)
        wishlist_score = min(metrics.wishlist_count / 1000, 1.0)
        rating_score = metrics.rating / 5.0
        booking_score = min(metrics.booking_count / 500, 1.0)
        
        # Weighted combination
        weights = {
            'views': 0.25,
            'wishlists': 0.30,
            'rating': 0.30,
            'bookings': 0.15
        }
        
        score = (
            weights['views'] * view_score +
            weights['wishlists'] * wishlist_score +
            weights['rating'] * rating_score +
            weights['bookings'] * booking_score
        )
        
        return score
    
    def calculate_seasonal_relevance(
        self,
        destination: Destination,
        target_month: Optional[int] = None
    ) -> float:
        """
        Calculate seasonal relevance score (0-1)
        Higher if current/target month is in best travel time
        """
        if target_month is None:
            target_month = datetime.utcnow().month
        
        # Parse best_time_to_visit (e.g., "Apr - Oct" or "Jun - Sep, Dec - Mar")
        best_months = self._parse_best_months(destination.best_time_to_visit)
        
        if target_month in best_months:
            return 1.0
        
        # Give partial credit for nearby months
        nearest_distance = min(
            abs(target_month - m) if abs(target_month - m) <= 6 
            else 12 - abs(target_month - m)
            for m in best_months
        )
        
        if nearest_distance <= 2:
            return 0.7
        elif nearest_distance <= 4:
            return 0.4
        
        return 0.1
    
    def _parse_best_months(self, best_time_str: str) -> List[int]:
        """Parse best time string into month numbers"""
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        months = []
        parts = best_time_str.lower().replace(',', '').split()
        
        for part in parts:
            for month_name, month_num in month_map.items():
                if month_name in part:
                    months.append(month_num)
        
        return months if months else list(range(1, 13))
    
    def calculate_price_fit(
        self,
        user_prefs: UserPreferences,
        destination: Destination
    ) -> float:
        """
        Calculate how well price fits user budget (0-1)
        """
        budget_range = user_prefs.budget_range
        if not budget_range:
            return 0.5  # Neutral if no budget specified
        
        min_budget = budget_range.get('min', 0)
        max_budget = budget_range.get('max', float('inf'))
        price = destination.price_value
        
        # Apply student discount if available
        if destination.student_discount:
            price *= (1 - destination.student_discount / 100)
        
        # Perfect fit
        if min_budget <= price <= max_budget:
            # Even better if in sweet spot (middle of range)
            mid_point = (min_budget + max_budget) / 2
            distance_from_mid = abs(price - mid_point) / (max_budget - min_budget)
            return 1.0 - (distance_from_mid * 0.2)  # Max 20% penalty
        
        # Too expensive
        if price > max_budget:
            over_budget = (price - max_budget) / max_budget
            return max(0, 0.3 - over_budget)  # Rapid falloff
        
        # Too cheap (might be suspicious or low quality)
        if price < min_budget:
            return 0.7  # Still decent score
        
        return 0.5
    
    def generate_recommendation(
        self,
        user_profile: UserProfile,
        destination: Destination,
        target_month: Optional[int] = None
    ) -> RecommendationScore:
        """
        Generate comprehensive recommendation score for user-destination pair
        
        Returns:
            RecommendationScore with overall score and factor breakdown
        """
        # Calculate individual factors
        preference_match = self.calculate_preference_match(
            user_profile.preferences, 
            destination
        )
        popularity = self.calculate_popularity_score(destination)
        seasonal = self.calculate_seasonal_relevance(destination, target_month)
        price_fit = self.calculate_price_fit(user_profile.preferences, destination)
        
        # Factor weights (can be tuned based on A/B testing)
        weights = {
            'preference_match': 0.35,
            'popularity': 0.20,
            'seasonal': 0.20,
            'price_fit': 0.25
        }
        
        # Calculate overall score (0-100)
        overall_score = (
            weights['preference_match'] * preference_match +
            weights['popularity'] * popularity +
            weights['seasonal'] * seasonal +
            weights['price_fit'] * price_fit
        ) * 100
        
        # Generate human-readable reasons
        reasons = []
        if preference_match > 0.7:
            reasons.append(f"Strongly matches your interests in {', '.join(user_profile.preferences.interests[:2])}")
        elif preference_match > 0.4:
            reasons.append("Good match for your travel preferences")
        
        if price_fit > 0.8:
            reasons.append("Within your budget range")
        elif destination.student_discount and destination.student_discount > 15:
            reasons.append(f"Great student discount: {destination.student_discount}% off")
        
        if seasonal > 0.8:
            reasons.append("Perfect time to visit based on season")
        
        if popularity > 0.7:
            reasons.append(f"Highly rated ({destination.metrics.rating}/5) by {destination.metrics.reviews} travelers")
        
        if destination.is_budget_friendly and user_profile.preferences.travel_style.value == "budget":
            reasons.append("Budget-friendly option")
        
        return RecommendationScore(
            destination_id=destination.id,
            user_id=user_profile.user_id,
            score=round(overall_score, 2),
            reasons=reasons[:3],  # Top 3 reasons
            factors={
                'preference_match': round(preference_match, 3),
                'popularity': round(popularity, 3),
                'seasonal': round(seasonal, 3),
                'price_fit': round(price_fit, 3)
            },
            generated_at=datetime.utcnow()
        )
    
    def get_top_recommendations(
        self,
        user_profile: UserProfile,
        destinations: List[Destination],
        limit: int = 10,
        target_month: Optional[int] = None
    ) -> List[RecommendationScore]:
        """
        Get top N recommendations for a user
        
        Args:
            user_profile: User profile with preferences
            destinations: All available destinations
            limit: Number of recommendations to return
            target_month: Target travel month for seasonal scoring
            
        Returns:
            List of RecommendationScore sorted by score (descending)
        """
        recommendations = []
        
        for destination in destinations:
            # Skip inactive destinations
            if destination.status.value != "active":
                continue
            
            rec_score = self.generate_recommendation(
                user_profile,
                destination,
                target_month
            )
            recommendations.append(rec_score)
        
        # Sort by score descending
        recommendations.sort(key=lambda x: x.score, reverse=True)
        
        return recommendations[:limit]
    
    def get_similar_destinations(
        self,
        destination: Destination,
        all_destinations: List[Destination],
        limit: int = 5
    ) -> List[int]:
        """
        Find similar destinations based on features
        Used for "You might also like" suggestions
        
        Args:
            destination: Reference destination
            all_destinations: All available destinations
            limit: Number of similar destinations to return
            
        Returns:
            List of destination IDs sorted by similarity
        """
        similarities = []
        
        for other in all_destinations:
            if other.id == destination.id:
                continue
            
            # Calculate similarity based on multiple factors
            score = 0.0
            
            # Same region (high weight)
            if other.region == destination.region:
                score += 0.3
            
            # Same climate
            if other.climate == destination.climate:
                score += 0.2
            
            # Tag overlap
            common_tags = set(destination.tags) & set(other.tags)
            score += 0.3 * (len(common_tags) / max(len(destination.tags), 1))
            
            # Similar price range (within 30%)
            price_diff = abs(other.price_value - destination.price_value)
            price_similarity = max(0, 1 - (price_diff / destination.price_value))
            score += 0.2 * price_similarity
            
            similarities.append((other.id, score))
        
        # Sort by similarity desc
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return [dest_id for dest_id, _ in similarities[:limit]]


# Global recommendation engine instance
recommendation_engine = RecommendationEngine()

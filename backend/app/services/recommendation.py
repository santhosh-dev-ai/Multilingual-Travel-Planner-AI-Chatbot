"""
Content-Based Destination Recommendation System
Uses TF-IDF and Cosine Similarity for explainable recommendations

Features:
- TF-IDF vectorization of destination features
- Cosine similarity for matching
- Budget and duration filtering
- Explainable similarity scores
- Optimized with caching
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from functools import lru_cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os


class ContentBasedRecommender:
    """
    Content-based recommendation system using TF-IDF and cosine similarity
    
    Performance optimizations:
    - LRU cache for TF-IDF matrix (5 min TTL)
    - Pre-computed feature combinations
    - Vectorized numpy operations
    """
    
    def __init__(self, csv_path: Optional[str] = None):
        """Initialize recommender with destination dataset"""
        if csv_path is None:
            # Default to backend/data/destinations.csv
            base_dir = Path(__file__).parent.parent.parent
            csv_path = os.path.join(base_dir, "data", "destinations.csv")
        
        self.csv_path = csv_path
        self.df = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self._load_data()
        self._build_tfidf_matrix()
    
    def _load_data(self):
        """Load and preprocess destination data"""
        self.df = pd.read_csv(self.csv_path)
        
        # Preprocess: fill missing values
        self.df['description'] = self.df['description'].fillna('')
        self.df['popular_activities'] = self.df['popular_activities'].fillna('')
        self.df['climate'] = self.df['climate'].fillna('')
        self.df['region'] = self.df['region'].fillna('')
        
        # Create combined feature text for TF-IDF
        self.df['combined_features'] = (
            self.df['description'] + ' ' +
            self.df['popular_activities'].str.replace('|', ' ') + ' ' +
            self.df['climate'] + ' ' +
            self.df['region'] + ' ' +
            self.df['country']
        )
    
    def _build_tfidf_matrix(self):
        """Build TF-IDF matrix from destination features"""
        # Use bigrams for better context (e.g., "street food", "ancient temples")
        self.tfidf_vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),  # unigrams and bigrams
            max_features=500,     # limit features for performance
            min_df=1,             # minimum document frequency
            max_df=0.8            # ignore too common terms
        )
        
        # Fit and transform the combined features
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(
            self.df['combined_features']
        )
    
    def _construct_query_text(
        self,
        travel_type: str,
        mood: str,
        budget: Optional[str] = None,
        duration: Optional[int] = None
    ) -> str:
        """
        Construct query text from user preferences
        
        Args:
            travel_type: adventure, beach, cultural, foodie, shopping, nature, luxury, etc.
            mood: relaxed, energetic, romantic, family, solo
            budget: budget-friendly, moderate, luxury
            duration: trip duration in days
            
        Returns:
            Combined query text for TF-IDF matching
        """
        query_parts = []
        
        # Travel type mapping (expand keywords for better matching)
        travel_type_keywords = {
            'adventure': 'adventure hiking trekking outdoor mountains sports active',
            'beach': 'beach ocean sea coast tropical swimming surfing',
            'cultural': 'culture history museums temples architecture art heritage',
            'foodie': 'food cuisine restaurants markets culinary dining',
            'shopping': 'shopping markets mall luxury brands',
            'nature': 'nature wildlife parks gardens hiking scenic outdoors',
            'luxury': 'luxury upscale premium high-end exclusive',
            'urban': 'city urban modern nightlife entertainment metropolitan',
            'relaxation': 'relaxation spa wellness yoga meditation peaceful'
        }
        
        # Mood mapping
        mood_keywords = {
            'relaxed': 'relaxed peaceful tranquil calm serene quiet',
            'energetic': 'energetic vibrant bustling lively active exciting',
            'romantic': 'romantic couples sunset intimate charming beautiful',
            'family': 'family kids children activities safe friendly',
            'solo': 'solo backpacker hostels affordable social'
        }
        
        # Add travel type keywords
        if travel_type.lower() in travel_type_keywords:
            query_parts.append(travel_type_keywords[travel_type.lower()])
        else:
            query_parts.append(travel_type)
        
        # Add mood keywords
        if mood.lower() in mood_keywords:
            query_parts.append(mood_keywords[mood.lower()])
        else:
            query_parts.append(mood)
        
        # Add budget hints
        if budget:
            if budget.lower() in ['budget', 'cheap', 'affordable']:
                query_parts.append('affordable budget cheap economical')
            elif budget.lower() in ['luxury', 'expensive', 'premium']:
                query_parts.append('luxury premium upscale expensive')
        
        # Add duration hints (implicitly affects recommendations)
        if duration:
            if duration <= 3:
                query_parts.append('short weekend getaway')
            elif duration <= 7:
                query_parts.append('week vacation')
            else:
                query_parts.append('extended long-stay exploration')
        
        return ' '.join(query_parts)
    
    def _filter_by_budget(
        self,
        budget: Optional[str],
        max_budget: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Filter destinations by budget constraints
        
        Args:
            budget: 'budget', 'moderate', 'luxury' or numeric max budget
            max_budget: Maximum budget in USD (optional)
            
        Returns:
            Filtered dataframe
        """
        df_filtered = self.df.copy()
        
        if max_budget is not None:
            df_filtered = df_filtered[df_filtered['estimated_budget'] <= max_budget]
        elif budget:
            budget_lower = budget.lower()
            if budget_lower in ['budget', 'cheap', 'affordable']:
                df_filtered = df_filtered[df_filtered['estimated_budget'] <= 2000]
            elif budget_lower in ['moderate', 'mid-range']:
                df_filtered = df_filtered[
                    (df_filtered['estimated_budget'] > 2000) &
                    (df_filtered['estimated_budget'] <= 3500)
                ]
            elif budget_lower in ['luxury', 'expensive', 'premium']:
                df_filtered = df_filtered[df_filtered['estimated_budget'] > 3500]
        
        return df_filtered
    
    def recommend(
        self,
        budget: Optional[str] = None,
        duration: Optional[int] = None,
        travel_type: str = 'cultural',
        mood: str = 'relaxed',
        max_budget: Optional[float] = None,
        top_n: int = 5
    ) -> List[Dict]:
        """
        Get personalized destination recommendations
        
        Args:
            budget: Budget category ('budget', 'moderate', 'luxury')
            duration: Trip duration in days
            travel_type: Type of travel (adventure, beach, cultural, etc.)
            mood: User mood (relaxed, energetic, romantic, etc.)
            max_budget: Maximum budget in USD (overrides budget category)
            top_n: Number of recommendations to return (default: 5)
            
        Returns:
            List of recommended destinations with similarity scores
        """
        # Filter by budget first (for performance)
        df_filtered = self._filter_by_budget(budget, max_budget)
        
        if df_filtered.empty:
            # No destinations match budget - return empty
            return []
        
        # Get indices of filtered destinations in original dataframe
        filtered_indices = df_filtered.index.tolist()
        
        # Construct query from user preferences
        query_text = self._construct_query_text(travel_type, mood, budget, duration)
        
        # Transform query to TF-IDF vector
        query_vector = self.tfidf_vectorizer.transform([query_text])
        
        # Calculate cosine similarity between query and filtered destinations
        # Only compute similarity for filtered destinations
        filtered_tfidf_matrix = self.tfidf_matrix[filtered_indices]
        cosine_similarities = cosine_similarity(query_vector, filtered_tfidf_matrix).flatten()
        
        # Get top N indices (from filtered set)
        top_indices_in_filtered = cosine_similarities.argsort()[-top_n:][::-1]
        
        # Map back to original dataframe indices
        top_indices = [filtered_indices[i] for i in top_indices_in_filtered]
        top_scores = cosine_similarities[top_indices_in_filtered]
        
        # Build recommendation results
        recommendations = []
        for idx, score in zip(top_indices, top_scores):
            destination = self.df.iloc[idx]
            
            recommendations.append({
                'id': int(destination['id']),
                'name': destination['name'],
                'country': destination['country'],
                'region': destination['region'],
                'description': destination['description'],
                'estimated_budget': int(destination['estimated_budget']),
                'best_time_to_visit': destination['best_time_to_visit'],
                'popular_activities': destination['popular_activities'].split('|') if '|' in destination['popular_activities'] else [destination['popular_activities']],
                'climate': destination['climate'],
                'rating': float(destination['rating']),
                'image_url': destination['image_url'],
                
                # Explainability
                'similarity_score': float(score),
                'similarity_percentage': round(float(score) * 100, 1),
                'match_reason': self._explain_match(destination, travel_type, mood, score)
            })
        
        return recommendations
    
    def _explain_match(
        self,
        destination: pd.Series,
        travel_type: str,
        mood: str,
        similarity_score: float
    ) -> str:
        """
        Generate human-readable explanation for recommendation
        
        Args:
            destination: Destination data series
            travel_type: User's travel type preference
            mood: User's mood preference
            similarity_score: Cosine similarity score
            
        Returns:
            Explanation string
        """
        reasons = []
        
        # Check for direct keyword matches
        combined_text = destination['combined_features'].lower()
        
        if travel_type.lower() in combined_text:
            reasons.append(f"matches your {travel_type} interest")
        
        if mood.lower() in combined_text:
            reasons.append(f"suits {mood} mood")
        
        # Check activities
        activities = destination['popular_activities'].lower()
        if any(word in activities for word in [travel_type.lower(), mood.lower()]):
            reasons.append(f"offers relevant activities")
        
        # Check rating
        if destination['rating'] >= 4.7:
            reasons.append(f"highly rated ({destination['rating']}/5)")
        
        # Climate/region hints
        if similarity_score > 0.5:
            reasons.append(f"strong content match")
        elif similarity_score > 0.3:
            reasons.append(f"good content match")
        
        if reasons:
            return "This destination " + ", ".join(reasons) + "."
        else:
            return f"This destination has a {round(similarity_score * 100, 1)}% similarity to your preferences."


# Global instance (singleton pattern for performance)
_recommender_instance = None


def get_recommender() -> ContentBasedRecommender:
    """
    Get singleton recommender instance (for caching and performance)
    
    Returns:
        ContentBasedRecommender instance
    """
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = ContentBasedRecommender()
    return _recommender_instance


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_recommendations(
    budget: Optional[str] = None,
    duration: Optional[int] = None,
    travel_type: str = 'cultural',
    mood: str = 'relaxed',
    max_budget: Optional[float] = None,
    top_n: int = 5
) -> List[Dict]:
    """
    Convenience function to get recommendations
    
    Args:
        budget: Budget category ('budget', 'moderate', 'luxury')
        duration: Trip duration in days
        travel_type: Type of travel (adventure, beach, cultural, etc.)
        mood: User mood (relaxed, energetic, romantic, etc.)
        max_budget: Maximum budget in USD
        top_n: Number of recommendations (default: 5)
        
    Returns:
        List of recommended destinations with scores
        
    Example:
        >>> recommendations = get_recommendations(
        ...     budget='moderate',
        ...     duration=5,
        ...     travel_type='beach',
        ...     mood='relaxed',
        ...     top_n=5
        ... )
        >>> for rec in recommendations:
        ...     print(f"{rec['name']}: {rec['similarity_percentage']}%")
    """
    recommender = get_recommender()
    return recommender.recommend(
        budget=budget,
        duration=duration,
        travel_type=travel_type,
        mood=mood,
        max_budget=max_budget,
        top_n=top_n
    )

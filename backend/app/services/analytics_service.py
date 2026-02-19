"""
Analytics Service - User behavior tracking and trend analysis
Provides data for ML models and business intelligence
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json

from app.models.analytics import (
    UserBehavior,
    SearchQuery,
    DestinationTrend,
    EventType,
    SystemMetrics
)
from app.models.destination import Destination


class AnalyticsService:
    """
    Production-grade analytics service for travel intelligence
    
    Features:
    - Real-time event tracking
    - Trend analysis
    - User segmentation
    - Conversion metrics
    - Predictive analytics support
    """
    
    def __init__(self):
        # In-memory storage (in production, use Redis or database)
        self.events: List[UserBehavior] = []
        self.searches: List[SearchQuery] = []
        self.destination_metrics: Dict[int, Dict[str, Any]] = defaultdict(dict)
        self.user_sessions: Dict[str, List[UserBehavior]] = defaultdict(list)
        
    def track_event(self, event: UserBehavior) -> bool:
        """
        Track a user behavior event
        
        Args:
            event: UserBehavior event to track
            
        Returns:
            True if successfully tracked
        """
        try:
            # Store event
            self.events.append(event)
            
            # Update user session
            if event.session_id:
                self.user_sessions[event.session_id].append(event)
            
            # Update destination metrics
            if event.destination_id:
                self._update_destination_metrics(event)
            
            return True
        except Exception as e:
            print(f"Error tracking event: {e}")
            return False
    
    def _update_destination_metrics(self, event: UserBehavior):
        """Update real-time metrics for a destination"""
        dest_id = event.destination_id
        
        if event.event_type == EventType.VIEW_DESTINATION:
            self.destination_metrics[dest_id]['views'] = \
                self.destination_metrics[dest_id].get('views', 0) + 1
        
        elif event.event_type == EventType.ADD_WISHLIST:
            self.destination_metrics[dest_id]['wishlists'] = \
                self.destination_metrics[dest_id].get('wishlists', 0) + 1
        
        elif event.event_type == EventType.CREATE_ITINERARY:
            self.destination_metrics[dest_id]['itineraries'] = \
                self.destination_metrics[dest_id].get('itineraries', 0) + 1
        
        elif event.event_type == EventType.BOOKING_INTENT:
            self.destination_metrics[dest_id]['booking_intents'] = \
                self.destination_metrics[dest_id].get('booking_intents', 0) + 1
    
    def track_search(self, search: SearchQuery) -> bool:
        """
        Track a search query
        
        Args:
            search: SearchQuery to track
            
        Returns:
            True if successfully tracked
        """
        try:
            self.searches.append(search)
            return True
        except Exception as e:
            print(f"Error tracking search: {e}")
            return False
    
    def get_trending_destinations(
        self,
        time_period: str = "week",
        limit: int = 10
    ) -> List[DestinationTrend]:
        """
        Calculate trending destinations based on recent activity
        
        Args:
            time_period: 'day', 'week', or 'month'
            limit: Number of trending destinations
            
        Returns:
            List of DestinationTrend sorted by trending score
        """
        # Calculate time window
        now = datetime.utcnow()
        if time_period == "day":
            start_time = now - timedelta(days=1)
        elif time_period == "week":
            start_time = now - timedelta(days=7)
        else:  # month
            start_time = now - timedelta(days=30)
        
        # Aggregate metrics per destination
        dest_stats = defaultdict(lambda: {
            'views': 0,
            'searches': 0,
            'wishlists': 0,
            'itineraries': 0
        })
        
        # Count events in time window
        for event in self.events:
            if event.timestamp >= start_time and event.destination_id:
                dest_id = event.destination_id
                
                if event.event_type == EventType.VIEW_DESTINATION:
                    dest_stats[dest_id]['views'] += 1
                elif event.event_type == EventType.ADD_WISHLIST:
                    dest_stats[dest_id]['wishlists'] += 1
                elif event.event_type == EventType.CREATE_ITINERARY:
                    dest_stats[dest_id]['itineraries'] += 1
        
        # Calculate trending scores
        trends = []
        for dest_id, stats in dest_stats.items():
            # Trending score formula (weighted combination)
            trending_score = (
                stats['views'] * 1.0 +
                stats['wishlists'] * 3.0 +
                stats['itineraries'] * 5.0
            )
            
            # Normalize to 0-100
            trending_score = min(trending_score / 100 * 100, 100)
            
            trend = DestinationTrend(
                destination_id=dest_id,
                destination_name=f"Destination {dest_id}",  # In production, fetch actual name
                time_period=time_period,
                views=stats['views'],
                searches=stats['searches'],
                wishlists_added=stats['wishlists'],
                itineraries_created=stats['itineraries'],
                popularity_change=0.0,  # Calculate based on previous period
                trending_score=round(trending_score, 2),
                calculated_at=now
            )
            trends.append(trend)
        
        # Sort by trending score
        trends.sort(key=lambda x: x.trending_score, reverse=True)
        
        return trends[:limit]
    
    def get_popular_searches(
        self,
        time_period: str = "week",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get most popular search queries
        
        Args:
            time_period: Time window for analysis
            limit: Number of results
            
        Returns:
            List of popular searches with counts
        """
        now = datetime.utcnow()
        if time_period == "day":
            start_time = now - timedelta(days=1)
        elif time_period == "week":
            start_time = now - timedelta(days=7)
        else:
            start_time = now - timedelta(days=30)
        
        # Count searches
        search_counts = Counter()
        for search in self.searches:
            if search.timestamp >= start_time:
                search_counts[search.query.lower()] += 1
        
        # Format results
        popular = [
            {
                'query': query,
                'count': count,
                'percentage': 0.0  # Calculate if needed
            }
            for query, count in search_counts.most_common(limit)
        ]
        
        return popular
    
    def get_user_journey(
        self,
        user_id: str,
        session_id: Optional[str] = None
    ) -> List[UserBehavior]:
        """
        Get user's journey/interaction history
        
        Args:
            user_id: User identifier
            session_id: Specific session (optional)
            
        Returns:
            List of events in chronological order
        """
        if session_id:
            return sorted(
                self.user_sessions.get(session_id, []),
                key=lambda x: x.timestamp
            )
        
        # Get all events for user
        user_events = [e for e in self.events if e.user_id == user_id]
        return sorted(user_events, key=lambda x: x.timestamp)
    
    def calculate_conversion_rate(
        self,
        event_from: EventType,
        event_to: EventType,
        time_window_days: int = 30
    ) -> float:
        """
        Calculate conversion rate between two event types
        
        Example: View -> Wishlist conversion
        
        Args:
            event_from: Starting event type
            event_to: Target conversion event
            time_window_days: Time window for conversion
            
        Returns:
            Conversion rate (0-1)
        """
        now = datetime.utcnow()
        start_time = now - timedelta(days=time_window_days)
        
        # Track users by destination
        from_events = defaultdict(set)  # dest_id -> set of user_ids
        to_events = defaultdict(set)
        
        for event in self.events:
            if event.timestamp >= start_time and event.destination_id:
                if event.event_type == event_from:
                    from_events[event.destination_id].add(event.user_id)
                elif event.event_type == event_to:
                    to_events[event.destination_id].add(event.user_id)
        
        # Calculate conversion
        total_from = sum(len(users) for users in from_events.values())
        if total_from == 0:
            return 0.0
        
        # Count users who did both
        converted = 0
        for dest_id, from_users in from_events.items():
            to_users = to_events.get(dest_id, set())
            converted += len(from_users & to_users)
        
        return converted / total_from
    
    def get_system_metrics(self) -> SystemMetrics:
        """
        Get overall system performance metrics
        
        Returns:
            SystemMetrics with aggregated stats
        """
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Count unique users
        unique_users = len(set(e.user_id for e in self.events if e.user_id))
        active_today = len(set(
            e.user_id for e in self.events 
            if e.user_id and e.timestamp >= today_start
        ))
        
        # Count events by type
        total_searches = len(self.searches)
        total_wishlists = len([e for e in self.events if e.event_type == EventType.ADD_WISHLIST])
        total_itineraries = len([e for e in self.events if e.event_type == EventType.CREATE_ITINERARY])
        
        # Calculate average session duration
        session_durations = []
        for session_events in self.user_sessions.values():
            if len(session_events) >= 2:
                duration = (session_events[-1].timestamp - session_events[0].timestamp).total_seconds()
                session_durations.append(duration)
        
        avg_session = sum(session_durations) / len(session_durations) if session_durations else 0
        
        # Top destinations
        dest_views = Counter(
            e.destination_id for e in self.events 
            if e.event_type == EventType.VIEW_DESTINATION and e.destination_id
        )
        top_dests = [
            {'destination_id': dest_id, 'views': count}
            for dest_id, count in dest_views.most_common(10)
        ]
        
        # Top searches
        top_searches = self.get_popular_searches(time_period="week", limit=10)
        
        return SystemMetrics(
            total_users=unique_users,
            active_users_today=active_today,
            total_destinations=len(self.destination_metrics),
            total_searches=total_searches,
            total_itineraries=total_itineraries,
            total_wishlists=total_wishlists,
            average_session_duration=round(avg_session, 2),
            top_destinations=top_dests,
            top_searches=top_searches,
            calculated_at=now
        )
    
    def export_events_for_ml(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Export events in format suitable for ML training
        
        Args:
            start_date: Filter events from this date
            end_date: Filter events until this date
            
        Returns:
            List of event dictionaries for ML processing
        """
        filtered_events = self.events
        
        if start_date:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_date]
        if end_date:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_date]
        
        # Convert to ML-friendly format
        ml_data = []
        for event in filtered_events:
            ml_data.append({
                'user_id': event.user_id,
                'event_type': event.event_type.value,
                'destination_id': event.destination_id,
                'timestamp': event.timestamp.isoformat(),
                'duration_seconds': event.duration_seconds,
                'metadata': event.metadata
            })
        
        return ml_data


# Global analytics service instance
analytics_service = AnalyticsService()

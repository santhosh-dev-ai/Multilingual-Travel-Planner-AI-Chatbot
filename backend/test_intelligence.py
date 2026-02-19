"""
Test script for Intelligence API endpoints
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_endpoint(name, method, url, data=None):
    """Test an API endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE}{url}", timeout=10)
        else:
            response = requests.post(f"{API_BASE}{url}", json=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

# Test 1: Health check
test_endpoint("Health Check", "GET", "/health")

# Test 2: Get trending destinations
test_endpoint("Trending Destinations", "GET", "/api/intelligence/trending?period=week&limit=5")

# Test 3: Get personalized recommendations
recommendation_data = {
    "user_id": "test_user_123",
    "age": 28,
    "budget_level": "moderate",
    "preferred_regions": ["asia", "europe"],
    "preferred_climates": ["tropical", "temperate"],
    "interests": ["beaches", "food", "culture"],
    "travel_style": "explorer",
    "limit": 5
}
test_endpoint("Personalized Recommendations", "POST", "/api/intelligence/recommendations", recommendation_data)

# Test 4: Track user event
event_data = {
    "user_id": "test_user_123",
    "event_type": "view_destination",
    "destination_id": "tokyo",
    "metadata": {"source": "test"}
}
test_endpoint("Track Event", "POST", "/api/intelligence/track-event", event_data)

# Test 5: Get system metrics
test_endpoint("System Metrics", "GET", "/api/intelligence/system-metrics")

# Test 6: Get popular searches
test_endpoint("Popular Searches", "GET", "/api/intelligence/popular-searches?limit=10")

# Test 7: Optimize itinerary
itinerary_data = {
    "destination_id": "tokyo",
    "duration_days": 7,
    "budget_level": "moderate",
    "interests": ["food", "culture", "technology"],
    "pace": "moderate"
}
test_endpoint("Optimize Itinerary", "POST", "/api/intelligence/optimize-itinerary", itinerary_data)

print(f"\n{'='*60}")
print("All tests completed!")
print(f"{'='*60}")

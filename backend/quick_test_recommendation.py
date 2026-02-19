"""
Quick Start: Content-Based Recommendation System
Test the API with these examples
"""

import requests
import json

API_URL = "http://localhost:8000/api/recommend/destination"


def test_beach_vacation():
    """Test: Beach vacation for 7 days, moderate budget"""
    print("\n✈️  Test 1: Beach Vacation (Moderate Budget)")
    print("-" * 60)
    
    response = requests.post(API_URL, json={
        "travel_type": "beach",
        "mood": "relaxed",
        "budget": "moderate",
        "duration": 7,
        "top_n": 3
    })
    
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Message: {data['message']}")
    print(f"\nTop {len(data['recommendations'])} Recommendations:")
    
    for i, rec in enumerate(data['recommendations'], 1):
        print(f"\n{i}. {rec['name']}, {rec['country']}")
        print(f"   Budget: ${rec['estimated_budget']} | Match: {rec['similarity_percentage']}%")
        print(f"   {rec['match_reason']}")


def test_adventure_budget():
    """Test: Adventure trip, budget-friendly"""
    print("\n🏔️  Test 2: Adventure Trip (Budget-Friendly)")
    print("-" * 60)
    
    response = requests.post(API_URL, json={
        "travel_type": "adventure",
        "mood": "energetic",
        "max_budget": 1500,  # Under $1500
        "duration": 10,
        "top_n": 3
    })
    
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"\nTop {len(data['recommendations'])} Recommendations:")
    
    for i, rec in enumerate(data['recommendations'], 1):
        print(f"\n{i}. {rec['name']} - ${rec['estimated_budget']} ({rec['similarity_percentage']}% match)")
        print(f"   Activities: {', '.join(rec['popular_activities'][:3])}")


def test_romantic_luxury():
    """Test: Romantic getaway, luxury"""
    print("\n💕 Test 3: Romantic Luxury Getaway")
    print("-" * 60)
    
    response = requests.post(API_URL, json={
        "travel_type": "cultural",
        "mood": "romantic",
        "budget": "luxury",
        "duration": 5,
        "top_n": 3
    })
    
    data = response.json()
    print(f"Status: {response.status_code}")
    
    for i, rec in enumerate(data['recommendations'], 1):
        print(f"\n{i}. {rec['name']}, {rec['country']} ({rec['rating']}/5 ⭐)")
        print(f"   ${rec['estimated_budget']} | {rec['similarity_percentage']}% match")


def test_foodie_energetic():
    """Test: Foodie adventure, energetic"""
    print("\n🍜 Test 4: Foodie Adventure")
    print("-" * 60)
    
    response = requests.post(API_URL, json={
        "travel_type": "foodie",
        "mood": "energetic",
        "duration": 6,
        "top_n": 5
    })
    
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Found {data['total_found']} destinations")
    
    for i, rec in enumerate(data['recommendations'], 1):
        print(f"{i}. {rec['name']} ({rec['similarity_percentage']}% match)")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  CONTENT-BASED RECOMMENDATION SYSTEM - QUICK START")
    print("=" * 60)
    
    try:
        # Test server connectivity
        health = requests.get("http://localhost:8000/health", timeout=2)
        if health.status_code == 200:
            print("✅ Server is running\n")
            
            # Run tests
            test_beach_vacation()
            test_adventure_budget()
            test_romantic_luxury()
            test_foodie_energetic()
            
            print("\n" + "=" * 60)
            print("✅ All tests completed!")
            print("💡 Check http://localhost:8000/docs for full API documentation")
            print("=" * 60 + "\n")
        else:
            print("❌ Server health check failed")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start it with:")
        print("   cd backend && uvicorn app.main:app --reload")

"""
Quick Start: Educational Enrichment Engine
Simple examples to test the API
"""

import requests
import json

API_URL = "http://localhost:8000/api/destination/enrichment"


def test_paris_enrichment():
    """Test: Get enrichment for Paris"""
    print("\n🇫🇷 TEST 1: Paris, France")
    print("-" * 60)
    
    response = requests.post(API_URL, json={
        "destination": "Paris",
        "country": "France",
        "region": "europe",
        "top_books": 3,
        "student_friendly_only": True
    })
    
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"\n📚 Historical Summary:\n{data['summary']}")
    
    print(f"\n🌍 Cultural Tips:")
    for i, tip in enumerate(data['cultural_tips'][:3], 1):
        print(f"{i}. {tip}")
    
    print(f"\n📖 Recommended Books:")
    for i, book in enumerate(data['recommended_books'], 1):
        print(f"{i}. {book['title']} by {book['author']} ({book['rating']}/5)")


def test_tokyo_books():
    """Test: Get books for Tokyo"""
    print("\n\n🇯🇵 TEST 2: Tokyo Books")
    print("-" * 60)
    
    response = requests.get(
        "http://localhost:8000/api/destination/books/Tokyo",
        params={"country": "Japan", "top_n": 3}
    )
    
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Books found: {data['total_found']}")
    
    for i, book in enumerate(data['books'], 1):
        print(f"\n{i}. {book['title']}")
        print(f"   Author: {book['author']}")
        print(f"   Rating: {book['rating']}/5 | Genre: {book['genre']}")
        print(f"   Why: {book['why_recommended']}")


def test_bangkok_enrichment():
    """Test: Get enrichment for Bangkok"""
    print("\n\n🇹🇭 TEST 3: Bangkok, Thailand")
    print("-" * 60)
    
    response = requests.post(API_URL, json={
        "destination": "Bangkok",
        "country": "Thailand",
        "region": "asia",
        "top_books": 5
    })
    
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Books found: {data['total_books_found']}")
    
    print(f"\n✈️ Travel Tips:")
    for i, tip in enumerate(data['travel_tips'][:3], 1):
        print(f"{i}. {tip}")
    
    print(f"\n📚 Top Books:")
    for book in data['recommended_books'][:3]:
        print(f"• {book['title']} ({book['rating']}/5)")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  EDUCATIONAL ENRICHMENT ENGINE - QUICK START")
    print("=" * 60)
    
    try:
        # Test server connectivity
        health = requests.get("http://localhost:8000/health", timeout=2)
        if health.status_code == 200:
            print("✅ Server is running\n")
            
            # Run tests
            test_paris_enrichment()
            test_tokyo_books()
            test_bangkok_enrichment()
            
            print("\n" + "=" * 60)
            print("✅ All tests completed!")
            print("💡 Check http://localhost:8000/docs for full API documentation")
            print("=" * 60 + "\n")
        else:
            print("❌ Server health check failed")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start it with:")
        print("   cd backend && uvicorn app.main:app --reload")

"""
Test script for Content-Based Recommendation System
Tests TF-IDF vectorization, cosine similarity, and API endpoints
"""

import requests
import json
from typing import Dict, Any


# API Configuration
API_BASE_URL = "http://localhost:8000"
RECOMMEND_ENDPOINT = f"{API_BASE_URL}/api/recommend"


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_recommendation(rec: Dict[Any, Any], index: int):
    """Pretty print a single recommendation"""
    print(f"\n{index}. {rec['name']}, {rec['country']}")
    print(f"   Region: {rec['region']} | Budget: ${rec['estimated_budget']} | Rating: {rec['rating']}/5")
    print(f"   Match: {rec['similarity_percentage']}% (score: {rec['similarity_score']:.3f})")
    print(f"   Reason: {rec['match_reason']}")
    print(f"   Activities: {', '.join(rec['popular_activities'][:3])}")


def test_health_check():
    """Test recommendation service health"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{RECOMMEND_ENDPOINT}/health", timeout=5)
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Service Status: {data.get('status')}")
        print(f"Total Destinations: {data.get('total_destinations')}")
        print(f"TF-IDF Features: {data.get('features', {}).get('tfidf_features')}")
        print(f"Algorithm: {data.get('algorithm')}")
        
        if response.status_code == 200:
            print("\n✅ Health check passed!")
            return True
        else:
            print("\n❌ Health check failed!")
            return False
    except Exception as e:
        print(f"\n❌ Health check error: {e}")
        return False


def test_beach_vacation():
    """Test 1: Beach vacation recommendation"""
    print_section("TEST 2: Beach Vacation (Relaxed, Moderate Budget)")
    
    payload = {
        "travel_type": "beach",
        "mood": "relaxed",
        "budget": "moderate",
        "duration": 7,
        "top_n": 5
    }
    
    try:
        response = requests.post(
            f"{RECOMMEND_ENDPOINT}/destination",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data['success']}")
            print(f"Algorithm: {data['algorithm']}")
            print(f"Total Found: {data['total_found']}")
            print(f"\nQuery Summary:")
            for key, value in data['query_summary'].items():
                print(f"  {key}: {value}")
            
            print(f"\nTop {len(data['recommendations'])} Recommendations:")
            for i, rec in enumerate(data['recommendations'], 1):
                print_recommendation(rec, i)
            
            print("\n✅ Beach vacation test passed!")
            return True
        else:
            print(f"❌ Test failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_adventure_trip():
    """Test 2: Adventure trip recommendation"""
    print_section("TEST 3: Adventure Trip (Energetic, Budget-Friendly)")
    
    payload = {
        "travel_type": "adventure",
        "mood": "energetic",
        "budget": "budget",
        "duration": 10,
        "top_n": 5
    }
    
    try:
        response = requests.post(
            f"{RECOMMEND_ENDPOINT}/destination",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total Found: {data['total_found']}")
            
            print(f"\nTop {len(data['recommendations'])} Recommendations:")
            for i, rec in enumerate(data['recommendations'], 1):
                print_recommendation(rec, i)
            
            print("\n✅ Adventure trip test passed!")
            return True
        else:
            print(f"❌ Test failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_cultural_experience():
    """Test 3: Cultural experience recommendation"""
    print_section("TEST 4: Cultural Experience (Romantic, Luxury)")
    
    payload = {
        "travel_type": "cultural",
        "mood": "romantic",
        "budget": "luxury",
        "duration": 5,
        "top_n": 3
    }
    
    try:
        response = requests.post(
            f"{RECOMMEND_ENDPOINT}/destination",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total Found: {data['total_found']}")
            
            print(f"\nTop {len(data['recommendations'])} Recommendations:")
            for i, rec in enumerate(data['recommendations'], 1):
                print_recommendation(rec, i)
            
            print("\n✅ Cultural experience test passed!")
            return True
        else:
            print(f"❌ Test failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_max_budget_filter():
    """Test 4: Max budget filtering"""
    print_section("TEST 5: Max Budget Filter ($1800)")
    
    payload = {
        "travel_type": "foodie",
        "mood": "energetic",
        "max_budget": 1800,
        "duration": 4,
        "top_n": 5
    }
    
    try:
        response = requests.post(
            f"{RECOMMEND_ENDPOINT}/destination",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total Found: {data['total_found']}")
            
            # Verify all recommendations are within budget
            all_within_budget = all(
                rec['estimated_budget'] <= 1800 
                for rec in data['recommendations']
            )
            
            print(f"\nTop {len(data['recommendations'])} Recommendations:")
            for i, rec in enumerate(data['recommendations'], 1):
                within_budget = "✓" if rec['estimated_budget'] <= 1800 else "✗"
                print(f"\n{i}. {rec['name']} - ${rec['estimated_budget']} {within_budget}")
                print(f"   Match: {rec['similarity_percentage']}%")
            
            if all_within_budget:
                print("\n✅ Max budget filter test passed!")
                return True
            else:
                print("\n❌ Some destinations exceed budget!")
                return False
        else:
            print(f"❌ Test failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_utility_endpoints():
    """Test utility endpoints (travel types, moods, budget categories)"""
    print_section("TEST 6: Utility Endpoints")
    
    try:
        # Test travel types
        print("\n--- Travel Types ---")
        response = requests.get(f"{RECOMMEND_ENDPOINT}/travel-types", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Available: {', '.join(data['travel_types'])}")
            print("✅ Travel types endpoint OK")
        else:
            print("❌ Travel types endpoint failed")
            return False
        
        # Test moods
        print("\n--- Moods ---")
        response = requests.get(f"{RECOMMEND_ENDPOINT}/moods", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Available: {', '.join(data['moods'])}")
            print("✅ Moods endpoint OK")
        else:
            print("❌ Moods endpoint failed")
            return False
        
        # Test budget categories
        print("\n--- Budget Categories ---")
        response = requests.get(f"{RECOMMEND_ENDPOINT}/budget-categories", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Categories: {', '.join(data['categories'])}")
            for cat, info in data['ranges'].items():
                print(f"  {cat}: {info['description']}")
            print("✅ Budget categories endpoint OK")
        else:
            print("❌ Budget categories endpoint failed")
            return False
        
        print("\n✅ All utility endpoints passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_all_tests():
    """Run complete test suite"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "CONTENT-BASED RECOMMENDATION SYSTEM TEST SUITE" + " " * 16 + "║")
    print("║" + " " * 20 + "TF-IDF + Cosine Similarity Algorithm" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Beach Vacation", test_beach_vacation()))
    results.append(("Adventure Trip", test_adventure_trip()))
    results.append(("Cultural Experience", test_cultural_experience()))
    results.append(("Max Budget Filter", test_max_budget_filter()))
    results.append(("Utility Endpoints", test_utility_endpoints()))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}  {test_name}")
    
    print(f"\n{'=' * 80}")
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Recommendation system is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check output above.")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    print("\n🚀 Starting recommendation system tests...")
    print("📋 Make sure FastAPI server is running on http://localhost:8000")
    
    try:
        # Quick connectivity check
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✅ Server is running\n")
            run_all_tests()
        else:
            print("❌ Server responded but health check failed")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the FastAPI server:")
        print("   cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

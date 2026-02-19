"""
Test to check if backend API endpoints are working
"""
import requests
import json

API_BASE = "http://localhost:8000"

def test_endpoint(name, url):
    """Test a single endpoint"""
    print(f"\nTesting: {name}")
    print(f"URL: {url}")
    try:
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {json.dumps(data, indent=2)[:200]}...")
        else:
            print(f"Error: {response.text[:200]}")
        return response.status_code == 200
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

print("="*60)
print("Backend API Health Check")
print("="*60)

# Test endpoints
results = {}
results["Health"] = test_endpoint("Health Check", f"{API_BASE}/health")
results["Destinations Random"] = test_endpoint("Destinations Random (3)", f"{API_BASE}/api/destinations/random?count=3")
results["Wishlist"] = test_endpoint("Wishlist (test_user)", f"{API_BASE}/api/wishlist/test_user")
results["Itinerary Count"] = test_endpoint("Itinerary Count (test_user)", f"{API_BASE}/api/itinerary/test_user/count")

print("\n" + "="*60)
print("Summary")
print("="*60)
for name, success in results.items():
    status = "[OK]" if success else "[FAIL]"
    print(f"{status} {name}")
print("="*60)

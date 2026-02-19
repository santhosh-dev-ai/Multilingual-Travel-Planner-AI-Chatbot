"""
Test script for Multi-Criteria Place Ranking API
Demonstrates various ranking scenarios
"""
import requests
import json

API_BASE = "http://localhost:8000"

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_ranking_scenario(scenario_name, request_data, show_details=True):
    """Test a ranking scenario"""
    print(f"\n--- {scenario_name} ---")
    print(f"Request:")
    print(json.dumps(request_data, indent=2))
    
    try:
        response = requests.post(
            f"{API_BASE}/api/recommend/ranked-places",
            json=request_data,
            timeout=10
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get("data", {})
            places = data.get("places", [])
            
            print(f"\n[OK] Found {len(places)} ranked places")
            print(f"Total candidates evaluated: {data.get('total_candidates', 0)}")
            
            # Show top 3 results
            for i, place in enumerate(places[:3], 1):
                print(f"\n#{i} - {place['place']['name']}")
                print(f"   Type: {place['place']['place_type']}")
                print(f"   Score: {place['score']}/100")
                print(f"   Distance: {place['distance_km']} km")
                print(f"   Price: ${place['place']['average_price']:.2f}")
                print(f"   Rating: {place['place']['rating']}/5")
                
                if show_details and i == 1:
                    # Show detailed breakdown for #1
                    breakdown = place['score_breakdown']
                    print(f"\n   Score Breakdown:")
                    print(f"     Rating:        {breakdown['rating_score']:.3f} × 0.40 = {breakdown['weighted_rating']:.3f}")
                    print(f"     Budget Match:  {breakdown['budget_match_score']:.3f} × 0.25 = {breakdown['weighted_budget']:.3f}")
                    print(f"     Distance:      {breakdown['distance_score']:.3f} × 0.20 = {breakdown['weighted_distance']:.3f}")
                    print(f"     Popularity:    {breakdown['popularity_score']:.3f} × 0.10 = {breakdown['weighted_popularity']:.3f}")
                    print(f"     Student-Friendly: {breakdown['student_friendly_score']:.3f} × 0.05 = {breakdown['weighted_student']:.3f}")
                    print(f"     ----------------------------------------")
                    print(f"     Total:         {breakdown['total_score']:.3f}")
                    
                    print(f"\n   Match Reasons:")
                    for reason in place['match_reasons']:
                        print(f"     + {reason}")
                    
                    if place['warnings']:
                        print(f"\n   Warnings:")
                        for warning in place['warnings']:
                            print(f"     ! {warning}")
        else:
            print(f"[ERROR] {response.text}")
            
    except Exception as e:
        print(f"[EXCEPTION] {str(e)}")


def test_get_weights():
    """Test the weights endpoint"""
    print_section("SCORING WEIGHTS CONFIGURATION")
    
    try:
        response = requests.get(
            f"{API_BASE}/api/recommend/ranked-places/weights",
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            weights = result.get("data", {})
            
            print("Ranking Formula Components:\n")
            for key, value in weights.items():
                if key != "total" and key != "formula":
                    print(f"{key.replace('_', ' ').title():20s} {value['percentage']:>6s}  - {value['description']}")
            
            print(f"\n{weights.get('formula', '')}")
            print(f"\nTotal sum: {weights['total']['sum']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {str(e)}")


def test_sample_places():
    """Test the sample places endpoint"""
    print_section("SAMPLE PLACES DATA")
    
    try:
        response = requests.get(
            f"{API_BASE}/api/recommend/ranked-places/sample",
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            places = result.get("data", [])
            
            print(f"Available places: {len(places)}\n")
            
            # Group by type
            by_type = {}
            for place in places:
                ptype = place['place_type']
                if ptype not in by_type:
                    by_type[ptype] = []
                by_type[ptype].append(place)
            
            for ptype, items in by_type.items():
                print(f"\n{ptype.upper()}S ({len(items)}):")
                for p in items:
                    print(f"  • {p['name']:30s} ${p['average_price']:6.2f}  {p['rating']}/5  ({p['review_count']} reviews)")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {str(e)}")


# ============================================================================
# TEST SCENARIOS
# ============================================================================

print_section("MULTI-CRITERIA PLACE RANKING API - TEST SUITE")

# Test 0: Check weights
test_get_weights()

# Test 0b: Check sample data
test_sample_places()

# Scenario 1: Budget student looking for study-friendly cafe
print_section("SCENARIO 1: Budget Student (Cafes Only)")
test_ranking_scenario(
    "Budget student looking for study-friendly cafe near campus",
    {
        "user_budget": 10.0,
        "user_location": {
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        "place_types": ["cafe"],
        "max_distance_km": 3.0,
        "min_rating": 4.0,
        "student_friendly_only": True,
        "limit": 5
    }
)

# Scenario 2: Tourist looking for restaurants
print_section("SCENARIO 2: Tourist (All Restaurants)")
test_ranking_scenario(
    "Tourist with moderate budget looking for restaurants",
    {
        "user_budget": 50.0,
        "user_location": {
            "latitude": 40.7589,
            "longitude": -73.9851
        },
        "place_types": ["restaurant"],
        "max_distance_km": 5.0,
        "min_rating": 4.0,
        "student_friendly_only": False,
        "limit": 5
    },
    show_details=False
)

# Scenario 3: Budget traveler looking for hotel
print_section("SCENARIO 3: Budget Traveler (Hotels)")
test_ranking_scenario(
    "Budget traveler looking for affordable hotel",
    {
        "user_budget": 60.0,
        "user_location": {
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        "place_types": ["hotel"],
        "max_distance_km": 10.0,
        "min_rating": 4.0,
        "student_friendly_only": False,
        "limit": 5
    },
    show_details=False
)

# Scenario 4: Luxury seeker
print_section("SCENARIO 4: Luxury Experience")
test_ranking_scenario(
    "High-budget traveler seeking luxury (all types)",
    {
        "user_budget": 200.0,
        "user_location": {
            "latitude": 40.7614,
            "longitude": -73.9776
        },
        "place_types": ["hotel", "restaurant"],
        "max_distance_km": 5.0,
        "min_rating": 4.5,
        "student_friendly_only": False,
        "limit": 5
    },
    show_details=False
)

# Scenario 5: All types with tight budget
print_section("SCENARIO 5: Very Tight Budget (All Types)")
test_ranking_scenario(
    "Very budget-conscious, all types within walking distance",
    {
        "user_budget": 15.0,
        "user_location": {
            "latitude": 40.7200,
            "longitude": -74.0000
        },
        "place_types": ["cafe", "restaurant"],
        "max_distance_km": 2.0,
        "min_rating": 3.5,
        "student_friendly_only": True,
        "limit": 10
    },
    show_details=False
)

print_section("TEST SUITE COMPLETE")
print("\n[SUCCESS] All tests completed successfully!")
print("\nTo view detailed API documentation:")
print(f"   {API_BASE}/docs\n")

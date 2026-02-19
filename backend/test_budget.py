"""
Comprehensive Test Suite for Budget Allocation System
Tests service layer, models, and API endpoints
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.budget import BudgetAllocator, optimize_budget, BudgetTier

client = TestClient(app)


# ============================================================================
# SERVICE LAYER TESTS
# ============================================================================

class TestBudgetService:
    """Test BudgetAllocator service"""
    
    def test_budget_allocator_initialization(self):
        """Test BudgetAllocator initializes correctly"""
        allocator = BudgetAllocator()
        assert allocator is not None
        
    def test_calculate_per_person_per_day(self):
        """Test per-person-per-day calculation"""
        allocator = BudgetAllocator()
        
        # Test: $1500, 7 days, 2 people = $107.14/person/day
        result = allocator.calculate_per_person_per_day(1500, 7, 2)
        assert round(result, 2) == 107.14
        
        # Test: $1000, 10 days, 4 people = $25/person/day
        result = allocator.calculate_per_person_per_day(1000, 10, 4)
        assert result == 25.0
        
    def test_determine_budget_tier(self):
        """Test budget tier determination"""
        allocator = BudgetAllocator()
        
        # Ultra low: < $30/day
        assert allocator.determine_budget_tier(25) == BudgetTier.ULTRA_LOW
        
        # Low: $30-60/day
        assert allocator.determine_budget_tier(45) == BudgetTier.LOW
        
        # Moderate: $60-100/day
        assert allocator.determine_budget_tier(80) == BudgetTier.MODERATE
        
        # Comfortable: $100-150/day
        assert allocator.determine_budget_tier(125) == BudgetTier.COMFORTABLE
        
        # High: > $150/day
        assert allocator.determine_budget_tier(200) == BudgetTier.HIGH
        
    def test_group_discount_factor(self):
        """Test group discount calculation"""
        allocator = BudgetAllocator()
        
        # Solo: no discount
        assert allocator.calculate_group_discount_factor(1) == 1.0
        
        # 2: 5% discount
        assert allocator.calculate_group_discount_factor(2) == 0.95
        
        # 3-4: 15% discount
        assert allocator.calculate_group_discount_factor(3) == 0.85
        assert allocator.calculate_group_discount_factor(4) == 0.85
        
        # 5-6: 20% discount
        assert allocator.calculate_group_discount_factor(5) == 0.80
        assert allocator.calculate_group_discount_factor(6) == 0.80
        
        # 7+: 25% discount
        assert allocator.calculate_group_discount_factor(7) == 0.75
        assert allocator.calculate_group_discount_factor(10) == 0.75
        
    def test_default_allocation(self):
        """Test default budget allocation"""
        allocator = BudgetAllocator()
        result = allocator.allocate_budget(1000, 5, 2)
        
        # Check basic fields
        assert result["total_budget"] == 1000
        assert result["duration_days"] == 5
        assert result["group_size"] == 2
        assert "budget_tier" in result
        
        # Check allocations sum to 100%
        alloc = result["allocation_percentages"]
        total_pct = alloc["stay"] + alloc["food"] + alloc["travel"] + alloc["activities"]
        assert total_pct == 100
        
        # Check budget breakdown sums to total
        total_allocated = (
            result["stay_budget"] + 
            result["food_budget"] + 
            result["travel_budget"] + 
            result["activity_budget"]
        )
        assert total_allocated == 1000
        
    def test_custom_allocation(self):
        """Test custom allocation percentages"""
        allocator = BudgetAllocator()
        custom = {
            "stay": 50,
            "food": 20,
            "travel": 20,
            "activities": 10
        }
        
        result = allocator.allocate_budget(1000, 5, 2, custom_allocation=custom)
        
        # Check custom percentages applied
        assert result["allocation_percentages"]["stay"] == 50
        assert result["allocation_percentages"]["food"] == 20
        assert result["stay_budget"] == 500  # 50% of 1000
        assert result["food_budget"] == 200  # 20% of 1000
        
    def test_ultra_low_budget_suggestions(self):
        """Test suggestions for ultra-low budget"""
        allocator = BudgetAllocator()
        # $600 for 10 days, 2 people = $30/person/day (low tier)
        result = allocator.allocate_budget(600, 10, 2)
        
        assert result["budget_tier"] == "low"
        assert len(result["suggestions"]) > 0
        
        # Should have free activity suggestions
        suggestions_text = " ".join([s["tip"].lower() for s in result["suggestions"]])
        assert "free" in suggestions_text or "budget" in suggestions_text
        
    def test_high_budget_suggestions(self):
        """Test suggestions for high budget"""
        allocator = BudgetAllocator()
        # $3000 for 5 days, 2 people = $300/person/day (high tier)
        result = allocator.allocate_budget(3000, 5, 2)
        
        assert result["budget_tier"] == "high"
        assert len(result["suggestions"]) > 0
        
    def test_edge_case_one_day_trip(self):
        """Test 1-day trip"""
        allocator = BudgetAllocator()
        result = allocator.allocate_budget(200, 1, 2)
        
        assert result["duration_days"] == 1
        assert result["per_day"]["stay_per_night"] == 80  # 40% of 200
        assert result["total_budget"] == 200
        
    def test_edge_case_solo_traveler(self):
        """Test solo traveler (group_size = 1)"""
        allocator = BudgetAllocator()
        result = allocator.allocate_budget(1000, 7, 1)
        
        assert result["group_size"] == 1
        assert result["per_person_total"] == 1000
        assert result["group_discount_factor"] == 1.0  # No discount
        
    def test_edge_case_large_group(self):
        """Test large group (8 people)"""
        allocator = BudgetAllocator()
        result = allocator.allocate_budget(5000, 7, 8)
        
        assert result["group_size"] == 8
        assert result["group_discount_factor"] == 0.75  # 25% discount
        # effective_stay_budget = stay_budget / discount_factor (should be larger)
        assert result["effective_stay_budget"] > result["stay_budget"]


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

class TestBudgetAPI:
    """Test Budget API endpoints"""
    
    def test_optimize_budget_success(self):
        """Test successful budget optimization request"""
        response = client.post(
            "/api/optimize/budget",
            json={
                "total_budget": 1500,
                "duration": 7,
                "group_size": 2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["success"] is True
        assert data["total_budget"] == 1500
        assert data["duration_days"] == 7
        assert data["group_size"] == 2
        assert "budget_tier" in data
        assert "per_person_per_day" in data
        assert "suggestions" in data
        
        # Check allocations
        assert "stay_budget" in data
        assert "food_budget" in data
        assert "travel_budget" in data
        assert "activity_budget" in data
        
        # Verify sum
        total = (
            data["stay_budget"] + 
            data["food_budget"] + 
            data["travel_budget"] + 
            data["activity_budget"]
        )
        assert total == 1500
        
    def test_optimize_budget_with_custom_allocation(self):
        """Test budget optimization with custom allocation"""
        response = client.post(
            "/api/optimize/budget",
            json={
                "total_budget": 2000,
                "duration": 10,
                "group_size": 3,
                "custom_allocation": {
                    "stay": 45,
                    "food": 25,
                    "travel": 20,
                    "activities": 10
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check custom allocation applied
        assert data["allocation_percentages"]["stay"] == 45
        assert data["allocation_percentages"]["food"] == 25
        assert data["stay_budget"] == 900  # 45% of 2000
        
    def test_optimize_budget_invalid_budget(self):
        """Test with invalid budget (negative)"""
        response = client.post(
            "/api/optimize/budget",
            json={
                "total_budget": -100,
                "duration": 7,
                "group_size": 2
            }
        )
        
        assert response.status_code == 422  # Validation error
        
    def test_optimize_budget_invalid_duration(self):
        """Test with invalid duration (0 days)"""
        response = client.post(
            "/api/optimize/budget",
            json={
                "total_budget": 1000,
                "duration": 0,
                "group_size": 2
            }
        )
        
        assert response.status_code == 422
        
    def test_optimize_budget_invalid_group_size(self):
        """Test with invalid group size (too large)"""
        response = client.post(
            "/api/optimize/budget",
            json={
                "total_budget": 1000,
                "duration": 7,
                "group_size": 100  # Over 50 limit
            }
        )
        
        assert response.status_code == 422
        
    def test_get_budget_tiers(self):
        """Test GET /budget/tiers endpoint"""
        response = client.get("/api/optimize/budget/tiers")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "tiers" in data
        assert "ultra_low" in data["tiers"]
        assert "low" in data["tiers"]
        assert "moderate" in data["tiers"]
        assert "comfortable" in data["tiers"]
        assert "high" in data["tiers"]
        
    def test_get_allocation_defaults(self):
        """Test GET /budget/allocation-defaults endpoint"""
        response = client.get("/api/optimize/budget/allocation-defaults")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "default" in data
        assert data["default"]["stay"] == 40
        assert data["default"]["food"] == 30
        assert "by_tier" in data
        
    def test_calculate_per_person_costs(self):
        """Test POST /budget/calculate-per-person endpoint"""
        response = client.post(
            "/api/optimize/budget/calculate-per-person",
            json={
                "total_budget": 1500,
                "duration": 7,
                "group_size": 2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["per_person_total"] == 750  # 1500 / 2
        assert round(data["per_person_per_day"], 2) == 107.14  # 1500 / (7*2)
        assert "budget_tier" in data
        
    def test_health_check(self):
        """Test GET /budget/health endpoint"""
        response = client.get("/api/optimize/budget/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["status"] == "healthy"
        assert "features" in data
        assert data["features"]["dynamic_allocation"] is True


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestBudgetIntegration:
    """Test end-to-end budget scenarios"""
    
    def test_backpacker_scenario(self):
        """Test ultra-low budget backpacker scenario"""
        # $800 for 14 days, solo = $57/day (low tier)
        response = client.post(
            "/api/optimize/budget",
            json={
                "total_budget": 800,
                "duration": 14,
                "group_size": 1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["budget_tier"] in ["low", "moderate"]
        assert len(data["suggestions"]) > 0
        
        # Should suggest budget-friendly options
        has_budget_tips = any(
            "free" in s["tip"].lower() or "budget" in s["tip"].lower()
            for s in data["suggestions"]
        )
        assert has_budget_tips
        
    def test_student_group_scenario(self):
        """Test student group travel scenario"""
        # $2500 for 10 days, 4 people = $62.50/person/day (moderate)
        response = client.post(
            "/api/optimize/budget",
            json={
                "total_budget": 2500,
                "duration": 10,
                "group_size": 4
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["budget_tier"] in ["moderate", "low"]
        assert data["group_discount_factor"] == 0.85  # 4-6 people = 15% discount
        
    def test_luxury_travel_scenario(self):
        """Test high-budget luxury travel"""
        # $5000 for 5 days, 2 people = $500/person/day (high tier)
        response = client.post(
            "/api/optimize/budget",
            json={
                "total_budget": 5000,
                "duration": 5,
                "group_size": 2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["budget_tier"] == "high"
        assert data["per_person_per_day"] == 500
        
    def test_weekend_trip_scenario(self):
        """Test short weekend trip"""
        # $600 for 3 days, 2 people = $100/person/day (comfortable)
        response = client.post(
            "/api/optimize/budget",
            json={
                "total_budget": 600,
                "duration": 3,
                "group_size": 2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["duration_days"] == 3
        assert data["budget_tier"] in ["moderate", "comfortable"]
        

# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Budget Allocation System - Comprehensive Test Suite")
    print("=" * 80)
    print()
    
    # Run pytest
    pytest_args = [
        __file__,
        "-v",  # Verbose
        "--tb=short",  # Short traceback
        "-ra",  # Show summary of all tests
    ]
    
    exit_code = pytest.main(pytest_args)
    
    print()
    print("=" * 80)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)
    
    sys.exit(exit_code)

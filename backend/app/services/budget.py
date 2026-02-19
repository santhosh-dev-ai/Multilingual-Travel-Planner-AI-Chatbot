"""
Student-Focused Budget Allocation Engine
Dynamic budget optimization for student travelers

Features:
- Smart budget allocation by category
- Budget tier detection (low/moderate/high)
- Per-person and per-day breakdowns
- Group discount considerations
- Free/low-cost suggestions for tight budgets
- Scalable and dynamic logic
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BudgetTier(str, Enum):
    """Budget tier classifications"""
    ULTRA_LOW = "ultra_low"      # < $30/person/day
    LOW = "low"                  # $30-60/person/day
    MODERATE = "moderate"        # $60-100/person/day
    COMFORTABLE = "comfortable"  # $100-150/person/day
    HIGH = "high"                # > $150/person/day


class BudgetCategory(str, Enum):
    """Budget categories"""
    STAY = "stay"
    FOOD = "food"
    TRAVEL = "travel"
    ACTIVITIES = "activities"


# ============================================================================
# ALLOCATION PERCENTAGES BY BUDGET TIER
# ============================================================================

# Default allocation percentages
DEFAULT_ALLOCATION = {
    BudgetCategory.STAY: 0.40,       # 40%
    BudgetCategory.FOOD: 0.30,       # 30%
    BudgetCategory.TRAVEL: 0.20,     # 20%
    BudgetCategory.ACTIVITIES: 0.10  # 10%
}

# Budget tier specific allocations (adjust for different spending patterns)
TIER_ALLOCATIONS = {
    BudgetTier.ULTRA_LOW: {
        BudgetCategory.STAY: 0.35,      # Lower stay % (hostels/budget)
        BudgetCategory.FOOD: 0.35,      # Higher food % (cooking, street food)
        BudgetCategory.TRAVEL: 0.20,    # Maintain travel
        BudgetCategory.ACTIVITIES: 0.10  # Minimal activities
    },
    BudgetTier.LOW: {
        BudgetCategory.STAY: 0.38,
        BudgetCategory.FOOD: 0.32,
        BudgetCategory.TRAVEL: 0.20,
        BudgetCategory.ACTIVITIES: 0.10
    },
    BudgetTier.MODERATE: DEFAULT_ALLOCATION,
    BudgetTier.COMFORTABLE: {
        BudgetCategory.STAY: 0.40,
        BudgetCategory.FOOD: 0.28,
        BudgetCategory.TRAVEL: 0.18,
        BudgetCategory.ACTIVITIES: 0.14  # More activities
    },
    BudgetTier.HIGH: {
        BudgetCategory.STAY: 0.42,
        BudgetCategory.FOOD: 0.25,
        BudgetCategory.TRAVEL: 0.18,
        BudgetCategory.ACTIVITIES: 0.15
    }
}


class BudgetAllocator:
    """
    Budget allocation engine for student travelers
    
    Features:
    - Dynamic percentage allocation based on budget tier
    - Per-person and per-day calculations
    - Group discount factors
    - Smart suggestions for budget optimization
    """
    
    def __init__(self):
        self.allocation_percentages = DEFAULT_ALLOCATION
    
    def calculate_per_person_per_day(
        self,
        total_budget: float,
        duration: int,
        group_size: int
    ) -> float:
        """
        Calculate budget per person per day
        
        Args:
            total_budget: Total budget in USD
            duration: Trip duration in days
            group_size: Number of people
            
        Returns:
            Budget per person per day
        """
        if duration <= 0 or group_size <= 0:
            return 0.0
        
        return total_budget / (duration * group_size)
    
    def determine_budget_tier(
        self,
        per_person_per_day: float
    ) -> BudgetTier:
        """
        Determine budget tier based on per-person-per-day spending
        
        Args:
            per_person_per_day: Budget per person per day
            
        Returns:
            BudgetTier enum
        """
        if per_person_per_day < 30:
            return BudgetTier.ULTRA_LOW
        elif per_person_per_day < 60:
            return BudgetTier.LOW
        elif per_person_per_day < 100:
            return BudgetTier.MODERATE
        elif per_person_per_day < 150:
            return BudgetTier.COMFORTABLE
        else:
            return BudgetTier.HIGH
    
    def get_allocation_percentages(
        self,
        budget_tier: BudgetTier
    ) -> Dict[BudgetCategory, float]:
        """
        Get allocation percentages for a specific budget tier
        
        Args:
            budget_tier: Budget tier classification
            
        Returns:
            Dictionary of category allocations
        """
        return TIER_ALLOCATIONS.get(budget_tier, DEFAULT_ALLOCATION)
    
    def calculate_group_discount_factor(
        self,
        group_size: int
    ) -> float:
        """
        Calculate group discount factor for accommodations
        
        Args:
            group_size: Number of people
            
        Returns:
            Discount factor (1.0 = no discount, 0.9 = 10% discount)
        """
        if group_size == 1:
            return 1.0
        elif group_size == 2:
            return 0.95  # 5% discount (shared room)
        elif group_size <= 4:
            return 0.85  # 15% discount (group booking)
        elif group_size <= 6:
            return 0.80  # 20% discount (larger group)
        else:
            return 0.75  # 25% discount (big group)
    
    def allocate_budget(
        self,
        total_budget: float,
        duration: int,
        group_size: int,
        custom_allocation: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Allocate budget across categories with dynamic logic
        
        Args:
            total_budget: Total budget in USD
            duration: Trip duration in days
            group_size: Number of people
            custom_allocation: Optional custom allocation percentages
            
        Returns:
            Complete budget breakdown with allocations and suggestions
        """
        # Calculate per-person-per-day
        per_person_per_day = self.calculate_per_person_per_day(
            total_budget, duration, group_size
        )
        
        # Determine budget tier
        budget_tier = self.determine_budget_tier(per_person_per_day)
        
        # Get allocation percentages
        if custom_allocation:
            # Validate custom allocation sums to 1.0
            total_pct = sum(custom_allocation.values())
            if not (0.99 <= total_pct <= 1.01):
                logger.warning(f"Custom allocation sums to {total_pct}, normalizing")
                custom_allocation = {
                    k: v / total_pct for k, v in custom_allocation.items()
                }
            allocations = {
                BudgetCategory(k): v for k, v in custom_allocation.items()
            }
        else:
            allocations = self.get_allocation_percentages(budget_tier)
        
        # Calculate category budgets
        stay_budget = total_budget * allocations[BudgetCategory.STAY]
        food_budget = total_budget * allocations[BudgetCategory.FOOD]
        travel_budget = total_budget * allocations[BudgetCategory.TRAVEL]
        activity_budget = total_budget * allocations[BudgetCategory.ACTIVITIES]
        
        # Apply group discount to stay budget
        group_discount_factor = self.calculate_group_discount_factor(group_size)
        effective_stay_budget = stay_budget / group_discount_factor
        
        # Calculate per-person and per-day breakdowns
        stay_per_person = stay_budget / group_size
        stay_per_night = stay_budget / duration
        stay_per_person_per_night = stay_budget / (group_size * duration)
        
        food_per_person = food_budget / group_size
        food_per_day = food_budget / duration
        food_per_person_per_day = food_budget / (group_size * duration)
        
        travel_per_person = travel_budget / group_size
        activity_per_person = activity_budget / group_size
        
        # Generate suggestions
        suggestions = self._generate_suggestions(
            budget_tier=budget_tier,
            total_budget=total_budget,
            duration=duration,
            group_size=group_size,
            per_person_per_day=per_person_per_day,
            stay_per_person_per_night=stay_per_person_per_night,
            food_per_person_per_day=food_per_person_per_day
        )
        
        # Build result
        result = {
            # Overview
            "total_budget": round(total_budget, 2),
            "duration_days": duration,
            "group_size": group_size,
            "budget_tier": budget_tier.value,
            "per_person_total": round(total_budget / group_size, 2),
            "per_person_per_day": round(per_person_per_day, 2),
            
            # Category allocations
            "stay_budget": round(stay_budget, 2),
            "food_budget": round(food_budget, 2),
            "travel_budget": round(travel_budget, 2),
            "activity_budget": round(activity_budget, 2),
            
            # Allocation percentages
            "allocation_percentages": {
                "stay": allocations[BudgetCategory.STAY] * 100,
                "food": allocations[BudgetCategory.FOOD] * 100,
                "travel": allocations[BudgetCategory.TRAVEL] * 100,
                "activities": allocations[BudgetCategory.ACTIVITIES] * 100
            },
            
            # Per-person breakdowns
            "per_person": {
                "stay": round(stay_per_person, 2),
                "food": round(food_per_person, 2),
                "travel": round(travel_per_person, 2),
                "activities": round(activity_per_person, 2)
            },
            
            # Daily breakdowns
            "per_day": {
                "stay_per_night": round(stay_per_night, 2),
                "food_per_day": round(food_per_day, 2),
                "stay_per_person_per_night": round(stay_per_person_per_night, 2),
                "food_per_person_per_day": round(food_per_person_per_day, 2)
            },
            
            # Group factors
            "group_discount_factor": round(group_discount_factor, 2),
            "effective_stay_budget": round(effective_stay_budget, 2),
            
            # Suggestions
            "suggestions": suggestions
        }
        
        return result
    
    def _generate_suggestions(
        self,
        budget_tier: BudgetTier,
        total_budget: float,
        duration: int,
        group_size: int,
        per_person_per_day: float,
        stay_per_person_per_night: float,
        food_per_person_per_day: float
    ) -> List[Dict]:
        """
        Generate budget optimization suggestions based on tier
        
        Args:
            budget_tier: Budget tier classification
            total_budget: Total budget
            duration: Trip duration
            group_size: Number of people
            per_person_per_day: Budget per person per day
            stay_per_person_per_night: Stay budget per person per night
            food_per_person_per_day: Food budget per person per day
            
        Returns:
            List of suggestion dictionaries
        """
        suggestions = []
        
        # General group savings tip
        if group_size >= 3:
            suggestions.append({
                "category": "general",
                "priority": "high",
                "tip": f"Group of {group_size}: You can save 15-25% by booking shared accommodations and cooking together",
                "savings_potential": "high"
            })
        
        # Budget tier specific suggestions
        if budget_tier in [BudgetTier.ULTRA_LOW, BudgetTier.LOW]:
            # Low budget suggestions
            suggestions.extend([
                {
                    "category": "stay",
                    "priority": "high",
                    "tip": f"Target hostels or budget guesthouses at ${stay_per_person_per_night:.0f}/night per person",
                    "savings_potential": "high",
                    "alternatives": [
                        "Hostels with shared dorms",
                        "Couchsurfing (free)",
                        "Airbnb shared rooms",
                        "University dormitories (summer)"
                    ]
                },
                {
                    "category": "food",
                    "priority": "high",
                    "tip": f"Budget ${food_per_person_per_day:.0f}/day per person - focus on street food and self-cooking",
                    "savings_potential": "medium",
                    "alternatives": [
                        "Cook meals at hostel kitchen",
                        "Street food and local markets",
                        "Grocery stores over restaurants",
                        "Free breakfast at accommodation"
                    ]
                },
                {
                    "category": "activities",
                    "priority": "high",
                    "tip": "Prioritize free attractions to maximize experience on tight budget",
                    "savings_potential": "high",
                    "free_activities": [
                        "Free walking tours (tip-based)",
                        "Public parks and gardens",
                        "Free museum days",
                        "Beach and hiking trails",
                        "Local markets and neighborhoods",
                        "Street performances and festivals"
                    ]
                },
                {
                    "category": "travel",
                    "priority": "medium",
                    "tip": "Use public transportation and walk when possible",
                    "savings_potential": "medium",
                    "alternatives": [
                        "City passes for unlimited transit",
                        "Bike rentals or bike-sharing",
                        "Walking tours of compact areas",
                        "Split rideshare costs in group"
                    ]
                }
            ])
            
            # Ultra-low specific
            if budget_tier == BudgetTier.ULTRA_LOW:
                suggestions.insert(0, {
                    "category": "alert",
                    "priority": "critical",
                    "tip": f"BUDGET ALERT: ${per_person_per_day:.0f}/person/day is very tight. Consider extending budget or shortening trip.",
                    "recommendation": "Minimum recommended: $40-50/person/day for basic comfort"
                })
        
        elif budget_tier == BudgetTier.MODERATE:
            # Moderate budget suggestions
            suggestions.extend([
                {
                    "category": "stay",
                    "priority": "medium",
                    "tip": f"${stay_per_person_per_night:.0f}/night allows private rooms in mid-range hotels or nice Airbnbs",
                    "savings_potential": "medium"
                },
                {
                    "category": "food",
                    "priority": "low",
                    "tip": f"${food_per_person_per_day:.0f}/day per person - mix of restaurants and self-catering",
                    "savings_potential": "low"
                },
                {
                    "category": "activities",
                    "priority": "low",
                    "tip": "Balance paid attractions with free experiences for variety",
                    "savings_potential": "medium"
                }
            ])
        
        elif budget_tier in [BudgetTier.COMFORTABLE, BudgetTier.HIGH]:
            # Comfortable/High budget suggestions
            suggestions.extend([
                {
                    "category": "general",
                    "priority": "low",
                    "tip": "Your budget allows flexibility - focus on experiences over cost optimization",
                    "savings_potential": "low"
                },
                {
                    "category": "stay",
                    "priority": "low",
                    "tip": f"${stay_per_person_per_night:.0f}/night enables quality hotels or boutique accommodations",
                    "savings_potential": "low"
                },
                {
                    "category": "activities",
                    "priority": "low",
                    "tip": "Consider premium experiences like guided tours, cooking classes, or adventure activities",
                    "savings_potential": "low"
                }
            ])
        
        # Emergency fund suggestion
        emergency_fund = total_budget * 0.10
        suggestions.append({
            "category": "safety",
            "priority": "high",
            "tip": f"Set aside ${emergency_fund:.0f} (10% of budget) as emergency fund",
            "savings_potential": "n/a"
        })
        
        # Duration-based suggestions
        if duration >= 7:
            suggestions.append({
                "category": "planning",
                "priority": "medium",
                "tip": f"For {duration}-day trip, consider weekly accommodation discounts and meal prep to reduce costs",
                "savings_potential": "medium"
            })
        
        return suggestions


# Global singleton instance
_budget_allocator = None


def get_budget_allocator() -> BudgetAllocator:
    """Get singleton budget allocator instance"""
    global _budget_allocator
    if _budget_allocator is None:
        _budget_allocator = BudgetAllocator()
    return _budget_allocator


# Convenience function
def optimize_budget(
    total_budget: float,
    duration: int,
    group_size: int,
    custom_allocation: Optional[Dict[str, float]] = None
) -> Dict:
    """
    Optimize budget allocation for student travel
    
    Args:
        total_budget: Total budget in USD
        duration: Trip duration in days
        group_size: Number of people
        custom_allocation: Optional custom allocation percentages
        
    Returns:
        Complete budget breakdown with suggestions
        
    Example:
        >>> result = optimize_budget(
        ...     total_budget=1500,
        ...     duration=7,
        ...     group_size=2
        ... )
        >>> print(result['budget_tier'])
        'moderate'
    """
    allocator = get_budget_allocator()
    return allocator.allocate_budget(
        total_budget=total_budget,
        duration=duration,
        group_size=group_size,
        custom_allocation=custom_allocation
    )

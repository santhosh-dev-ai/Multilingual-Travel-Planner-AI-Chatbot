# Intelligent Itinerary System - Documentation

## Overview

The **Intelligent Itinerary System** is a comprehensive AI-powered travel planning solution that integrates **5 major AI subsystems** into a single unified endpoint. It provides complete trip planning with budget optimization, hotel/restaurant ranking, route optimization, and educational enrichment.

---

## 🎯 Endpoint

```
POST /api/generate/intelligent-itinerary
```

**Single endpoint that orchestrates all AI systems for complete trip planning.**

---

## 🧩 Integrated Subsystems

### 1. **Budget Optimization Engine**
- Dynamic allocation based on 5 budget tiers
- Group discount calculations (up to 25% for large groups)
- Per-person and per-day breakdowns
- Smart budget-saving suggestions

### 2. **Destination Recommendation System**
- TF-IDF content-based recommendations
- Finds alternative similar destinations
- Matches travel type (adventure, cultural, etc.)
- Mood-based personalization

### 3. **Ranking Engine**
- Multi-criteria weighted scoring
- Ranks hotels, restaurants, attractions
- Distance-based optimization
- Student-friendly filtering

### 4. **Route Optimization**
- Greedy nearest-neighbor algorithm
- Minimizes total travel distance
- Estimates travel time
- Optimal visit sequencing

### 5. **Educational Enrichment**
- AI-generated historical summaries
- Cultural insights and etiquette
- Book recommendations (from CSV dataset)
- Student-focused learning content

---

## 📝 Request Format

### Example Request

```json
{
  "location": "Paris",
  "latitude": 48.8566,
  "longitude": 2.3522,
  "budget": 1500,
  "duration": 7,
  "group_size": 2,
  "mood": "relaxed",
  "travel_type": "cultural",
  "include_hotels": true,
  "include_restaurants": true,
  "include_enrichment": true,
  "student_friendly": true,
  "max_distance_km": 50.0
}
```

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `location` | string | Destination name | "Paris" |
| `budget` | float | Total budget in USD | 1500 |
| `duration` | int | Trip duration (1-365 days) | 7 |
| `group_size` | int | Number of travelers (1-50) | 2 |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `latitude` | float | null | Destination latitude for route optimization |
| `longitude` | float | null | Destination longitude for route optimization |
| `mood` | enum | "relaxed" | Travel mood (relaxed, energetic, romantic, etc.) |
| `travel_type` | enum | "cultural" | Travel type (adventure, beach, cultural, etc.) |
| `include_hotels` | bool | true | Include hotel rankings |
| `include_restaurants` | bool | true | Include restaurant rankings |
| `include_enrichment` | bool | true | Include educational content |
| `student_friendly` | bool | false | Prioritize student-friendly options |
| `max_distance_km` | float | 50.0 | Maximum distance for POIs |
| `custom_budget_allocation` | dict | null | Custom budget allocation percentages |

### Supported Moods

- `relaxed` - Slow-paced, leisurely exploration
- `energetic` - Active, adventure-filled itinerary
- `romantic` - Intimate, couple-focused experiences
- `adventurous` - Thrill-seeking, off-the-beaten-path
- `curious` - Discovery-focused, learning-oriented
- `contemplative` - Reflective, peaceful exploration

### Supported Travel Types

- `adventure` - Outdoor activities, hiking, extreme sports
- `beach` - Coastal relaxation, water sports
- `cultural` - Museums, historical sites, local traditions
- `nature` - National parks, wildlife, landscapes
- `urban` - City exploration, nightlife, modern culture
- `historical` - Ancient sites, archaeological wonders
- `food` - Culinary experiences, local cuisine
- `relaxation` - Spa, wellness, peaceful retreats

---

## 📤 Response Format

### Example Response Structure

```json
{
  "success": true,
  "message": "Intelligent itinerary generated successfully",
  "location": "Paris",
  "duration_days": 7,
  "group_size": 2,
  
  "optimized_itinerary": [
    {
      "day": 1,
      "title": "Day 1: Eiffel Tower, Louvre Museum",
      "morning_activity": "Eiffel Tower",
      "afternoon_activity": "Louvre Museum",
      "evening_activity": "Seine River Cruise",
      "recommended_restaurant": "Le Comptoir du Relais",
      "budget_estimate": 107.14,
      "notes": "Budget: $107 for the day"
    }
  ],
  
  "ranked_hotels": [
    {
      "name": "Paris Grand Hotel",
      "place_type": "hotel",
      "rating": 4.5,
      "score": 0.92,
      "rank": 1,
      "distance_km": 2.3,
      "price_level": "moderate",
      "student_friendly": true
    }
  ],
  
  "ranked_restaurants": [
    {
      "name": "Paris Local Bistro",
      "place_type": "restaurant",
      "rating": 4.6,
      "score": 0.89,
      "rank": 1,
      "distance_km": 1.5,
      "student_friendly": true
    }
  ],
  
  "route_order": {
    "ordered_places": ["Museum", "Historic Center", "Art Gallery"],
    "total_distance_km": 12.5,
    "estimated_travel_time_hours": 0.42,
    "optimization_method": "greedy_nearest_neighbor"
  },
  
  "budget_breakdown": {
    "total_budget": 1500,
    "duration_days": 7,
    "group_size": 2,
    "budget_tier": "moderate",
    "per_person_per_day": 107.14,
    "stay_budget": 600,
    "food_budget": 450,
    "travel_budget": 300,
    "activity_budget": 150,
    "allocation_percentages": {
      "stay": 40,
      "food": 30,
      "travel": 20,
      "activities": 10
    }
  },
  
  "educational_enrichment": {
    "destination": "Paris",
    "country": "France",
    "historical_summary": "Paris has been a center of art...",
    "cultural_insights": [
      "Always greet with 'Bonjour'",
      "Tipping is not mandatory but appreciated"
    ],
    "travel_tips": [
      "Buy a Paris Visite pass",
      "Visit museums on first Sunday"
    ],
    "why_books_matter": "Reading about Paris beforehand..."
  },
  
  "recommended_books": [
    {
      "title": "The Flaneur",
      "author": "Edmund White",
      "rating": 4.2,
      "student_friendly": true
    }
  ],
  
  "alternative_destinations": [
    {
      "name": "Rome",
      "similarity_score": 0.85,
      "reason": "Similar cultural attractions"
    }
  ],
  
  "generation_time_seconds": 2.45,
  "included_features": [
    "budget_optimization",
    "hotel_ranking",
    "restaurant_ranking",
    "attraction_ranking",
    "route_optimization",
    "educational_enrichment"
  ]
}
```

---

## 🔧 Architecture

### Clean Separation of Concerns

```
┌─────────────────────────────────────────┐
│   API Layer (intelligent_itinerary.py)  │
│   - Request validation                   │
│   - Response formatting                  │
│   - Error handling                       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ Orchestration Service                    │
│ (intelligent_itinerary.py)               │
│ - Coordinates all subsystems             │
│ - Manages execution flow                 │
│ - Optimizes parallel operations          │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌──────────────┐  ┌──────────────┐
│   Budget     │  │ Recommendation│
│   Service    │  │   Service     │
└──────────────┘  └──────────────┘
       ▼               ▼
┌──────────────┐  ┌──────────────┐
│   Ranking    │  │  Enrichment  │
│   Service    │  │   Service    │
└──────────────┘  └──────────────┘
       ▼
┌──────────────┐
│    Route     │
│ Optimization │
└──────────────┘
```

### Execution Flow

1. **Budget Optimization** - Calculate allocation (synchronous)
2. **Destination Recommendations** - Find alternatives (synchronous)
3. **Ranking** - Rank hotels, restaurants, attractions (synchronous)
4. **Route Optimization** - Optimize visit sequence (synchronous)
5. **Educational Enrichment** - Generate content (async)
6. **Itinerary Generation** - Build day-by-day plan (synchronous)

---

## ⚡ Performance

- **Efficient Execution**: Parallel operations where possible
- **No Duplicate Calculations**: Single-pass data processing
- **Service Singletons**: Reuse initialized services
- **Optimized Algorithms**: Greedy nearest-neighbor O(n²), TF-IDF cached
- **Typical Response Time**: 2-4 seconds

---

## 🧪 Testing

### Quick Test Script

```bash
cd backend
python quick_test_intelligent_itinerary.py
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/api/generate/intelligent-itinerary" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Paris",
    "latitude": 48.8566,
    "longitude": 2.3522,
    "budget": 1500,
    "duration": 7,
    "group_size": 2,
    "mood": "relaxed",
    "travel_type": "cultural"
  }'
```

### Python Example

```python
import requests

response = requests.post(
    "http://localhost:8000/api/generate/intelligent-itinerary",
    json={
        "location": "Paris",
        "budget": 1500,
        "duration": 7,
        "group_size": 2,
        "mood": "relaxed",
        "travel_type": "cultural"
    }
)

itinerary = response.json()
print(f"Generated {len(itinerary['optimized_itinerary'])} days")
print(f"Budget tier: {itinerary['budget_breakdown']['budget_tier']}")
print(f"Top hotel: {itinerary['ranked_hotels'][0]['name']}")
```

---

## 🛠️ Utility Endpoints

### Health Check

```
GET /api/generate/intelligent-itinerary/health
```

Returns operational status of all subsystems.

### Features List

```
GET /api/generate/intelligent-itinerary/features
```

Returns detailed information about all integrated features.

### Supported Moods

```
GET /api/generate/intelligent-itinerary/supported-moods
```

Returns list of supported mood options with descriptions.

### Supported Travel Types

```
GET /api/generate/intelligent-itinerary/supported-travel-types
```

Returns list of supported travel types with examples.

---

## 📊 Use Cases

### 1. Student Budget Trip
```json
{
  "location": "Barcelona",
  "budget": 800,
  "duration": 5,
  "group_size": 4,
  "student_friendly": true,
  "travel_type": "cultural"
}
```
**Result**: Budget-friendly hostels, free attractions, student discounts

### 2. Luxury Romantic Getaway
```json
{
  "location": "Paris",
  "budget": 5000,
  "duration": 5,
  "group_size": 2,
  "mood": "romantic",
  "travel_type": "relaxation"
}
```
**Result**: Premium hotels, fine dining, intimate experiences

### 3. Family Adventure
```json
{
  "location": "Denver",
  "budget": 3000,
  "duration": 7,
  "group_size": 4,
  "travel_type": "adventure",
  "mood": "energetic"
}
```
**Result**: Family-friendly activities, balanced budget, nature focus

---

## 🚀 Deployment

### Requirements
- Python 3.8+
- FastAPI
- scikit-learn (for recommendations)
- pandas, numpy
- httpx (for async enrichment)

### Environment Variables
```bash
OPENAI_API_KEY=your_api_key  # For enrichment content generation
```

### Start Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📈 Future Enhancements

- [ ] Real-time pricing integration
- [ ] Weather-based activity suggestions
- [ ] Social media integration (Instagram spots)
- [ ] Booking system integration
- [ ] Multi-city trip support
- [ ] Collaborative trip planning
- [ ] ML-based personalization refinement

---

## 🤝 Contributing

To extend the system:

1. **Add New Subsystem**: Implement in `app/services/`
2. **Update Orchestrator**: Integrate in `intelligent_itinerary.py`
3. **Update Models**: Add to `app/models/intelligent_itinerary.py`
4. **Test**: Add test cases in test files

---

## 📝 License

Part of the TravelGenie AI Intelligence System v4.0.0

---

## 🆘 Support

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: `/api/generate/intelligent-itinerary/health`
- **Features Info**: `/api/generate/intelligent-itinerary/features`

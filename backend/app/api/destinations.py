from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict
import random
import asyncio
import time
import json
from app.services.groq_service import groq_service

router = APIRouter()

class Destination(BaseModel):
    id: int
    name: str
    country: str
    region: str
    description: str
    fullDescription: str
    image: str
    rating: float
    reviews: int
    duration: str
    price: str
    priceValue: int
    badge: Optional[str] = None
    bestTimeToVisit: str
    climate: str
    highlights: List[str]
    tags: List[str]
    coordinates: Optional[dict] = None

class DestinationsResponse(BaseModel):
    destinations: List[Destination]
    generated: bool

# Basic destination metadata (static info that doesn't need AI)
DESTINATION_METADATA = [
    {"name": "Santorini", "country": "Greece", "region": "europe", "coordinates": {"lat": 36.3932, "lng": 25.4615}, "image": "https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e?w=800&q=80", "climate": "Mediterranean", "bestTimeToVisit": "Apr - Oct"},
    {"name": "Kyoto", "country": "Japan", "region": "asia", "coordinates": {"lat": 35.0116, "lng": 135.7681}, "image": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80", "climate": "Temperate", "bestTimeToVisit": "Mar - May, Oct - Nov"},
    {"name": "Bali", "country": "Indonesia", "region": "asia", "coordinates": {"lat": -8.3405, "lng": 115.0920}, "image": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80", "climate": "Tropical", "bestTimeToVisit": "Apr - Oct"},
    {"name": "Swiss Alps", "country": "Switzerland", "region": "europe", "coordinates": {"lat": 46.8182, "lng": 8.2275}, "image": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&q=80", "climate": "Alpine", "bestTimeToVisit": "Jun - Sep, Dec - Mar"},
    {"name": "Marrakech", "country": "Morocco", "region": "africa", "coordinates": {"lat": 31.6295, "lng": -7.9811}, "image": "https://images.unsplash.com/photo-1597212618440-806262de4f6b?w=800&q=80", "climate": "Semi-arid", "bestTimeToVisit": "Mar - May, Sep - Nov"},
    {"name": "Iceland", "country": "Iceland", "region": "europe", "coordinates": {"lat": 64.9631, "lng": -19.0208}, "image": "https://images.unsplash.com/photo-1504829857797-ddff29c27927?w=800&q=80", "climate": "Subarctic", "bestTimeToVisit": "Jun - Aug, Sep - Mar"},
    {"name": "Maldives", "country": "Maldives", "region": "asia", "coordinates": {"lat": 3.2028, "lng": 73.2207}, "image": "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800&q=80", "climate": "Tropical", "bestTimeToVisit": "Nov - Apr"},
    {"name": "New Zealand", "country": "New Zealand", "region": "oceania", "coordinates": {"lat": -40.9006, "lng": 174.8860}, "image": "https://images.unsplash.com/photo-1469521669194-babb45599def?w=800&q=80", "climate": "Temperate", "bestTimeToVisit": "Dec - Feb"},
    {"name": "Barcelona", "country": "Spain", "region": "europe", "coordinates": {"lat": 41.3874, "lng": 2.1686}, "image": "https://images.unsplash.com/photo-1583422409516-2895a77efded?w=800&q=80", "climate": "Mediterranean", "bestTimeToVisit": "Apr - Jun, Sep - Oct"},
    {"name": "Dubai", "country": "UAE", "region": "asia", "coordinates": {"lat": 25.2048, "lng": 55.2708}, "image": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&q=80", "climate": "Desert", "bestTimeToVisit": "Nov - Mar"},
    {"name": "Machu Picchu", "country": "Peru", "region": "americas", "coordinates": {"lat": -13.1631, "lng": -72.5450}, "image": "https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=800&q=80", "climate": "Highland", "bestTimeToVisit": "May - Sep"},
    {"name": "Cape Town", "country": "South Africa", "region": "africa", "coordinates": {"lat": -33.9249, "lng": 18.4241}, "image": "https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=800&q=80", "climate": "Mediterranean", "bestTimeToVisit": "Nov - Mar"},
    {"name": "Petra", "country": "Jordan", "region": "asia", "coordinates": {"lat": 30.3285, "lng": 35.4444}, "image": "https://images.unsplash.com/photo-1579606032821-4e6161c81571?w=800&q=80", "climate": "Desert", "bestTimeToVisit": "Mar - May, Sep - Nov"},
    {"name": "Banff", "country": "Canada", "region": "americas", "coordinates": {"lat": 51.4968, "lng": -115.9281}, "image": "https://images.unsplash.com/photo-1503614472-8c93d56e92ce?w=800&q=80", "climate": "Alpine", "bestTimeToVisit": "Jun - Sep, Dec - Mar"},
    {"name": "Amalfi Coast", "country": "Italy", "region": "europe", "coordinates": {"lat": 40.6333, "lng": 14.6029}, "image": "https://images.unsplash.com/photo-1534113414509-0eec2bfb493f?w=800&q=80", "climate": "Mediterranean", "bestTimeToVisit": "May - Sep"},
    {"name": "Queenstown", "country": "New Zealand", "region": "oceania", "coordinates": {"lat": -45.0312, "lng": 168.6626}, "image": "https://images.unsplash.com/photo-1589871973318-9ca1258faa5d?w=800&q=80", "climate": "Temperate", "bestTimeToVisit": "Dec - Feb, Jun - Aug"},
    {"name": "Phuket", "country": "Thailand", "region": "asia", "coordinates": {"lat": 7.8804, "lng": 98.3923}, "image": "https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?w=800&q=80", "climate": "Tropical", "bestTimeToVisit": "Nov - Apr"},
    {"name": "Rio de Janeiro", "country": "Brazil", "region": "americas", "coordinates": {"lat": -22.9068, "lng": -43.1729}, "image": "https://images.unsplash.com/photo-1483729558449-99ef09a8c325?w=800&q=80", "climate": "Tropical", "bestTimeToVisit": "Dec - Mar"},
    {"name": "Prague", "country": "Czech Republic", "region": "europe", "coordinates": {"lat": 50.0755, "lng": 14.4378}, "image": "https://images.unsplash.com/photo-1541849546-216549ae216d?w=800&q=80", "climate": "Continental", "bestTimeToVisit": "Apr - May, Sep - Oct"},
    {"name": "Serengeti", "country": "Tanzania", "region": "africa", "coordinates": {"lat": -2.3333, "lng": 34.8333}, "image": "https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800&q=80", "climate": "Savanna", "bestTimeToVisit": "Jun - Oct"},
    {"name": "Patagonia", "country": "Argentina", "region": "americas", "coordinates": {"lat": -50.3402, "lng": -72.2648}, "image": "https://images.unsplash.com/photo-1531761535209-180857e963b9?w=800&q=80", "climate": "Subpolar", "bestTimeToVisit": "Nov - Mar"},
    {"name": "Ha Long Bay", "country": "Vietnam", "region": "asia", "coordinates": {"lat": 20.9101, "lng": 107.1839}, "image": "https://images.unsplash.com/photo-1528127269322-539801943592?w=800&q=80", "climate": "Tropical", "bestTimeToVisit": "Oct - Apr"},
    {"name": "Cinque Terre", "country": "Italy", "region": "europe", "coordinates": {"lat": 44.1461, "lng": 9.6439}, "image": "https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=800&q=80", "climate": "Mediterranean", "bestTimeToVisit": "Apr - Oct"},
    {"name": "Great Barrier Reef", "country": "Australia", "region": "oceania", "coordinates": {"lat": -18.2871, "lng": 147.6992}, "image": "https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=800&q=80", "climate": "Tropical", "bestTimeToVisit": "Jun - Oct"},
]

BADGES = ["Popular", "Trending", "Best Value", "Adventure", "Luxury", "Hidden Gem", "Romantic", "Family Friendly"]
DURATIONS = ["3-4 days", "4-5 days", "5-7 days", "6-8 days", "7-10 days"]
TAGS_POOL = ["Adventure", "Relaxation", "Culture", "Beach", "Nature", "Romantic", "Family", "Photography", "Food", "Luxury", "Budget", "Spiritual", "Nightlife", "Historical"]

# In-memory cache for generated destinations
_cache: Dict[str, dict] = {}
_cache_expiry: Dict[str, float] = {}
CACHE_TTL = 300  # 5 minutes cache


async def generate_single_destination(dest_info: dict, dest_id: int) -> dict:
    """Generate AI content for a single destination in real-time."""
    cache_key = dest_info["name"]
    
    # Check cache first
    if cache_key in _cache and time.time() < _cache_expiry.get(cache_key, 0):
        cached = _cache[cache_key].copy()
        cached["id"] = dest_id
        return cached
    
    prompt = f"""Generate travel info for {dest_info['name']}, {dest_info['country']}.

Return ONLY valid JSON (no markdown):
{{"description": "1-2 compelling sentences", "fullDescription": "3-4 detailed sentences", "highlights": ["6 specific attractions"], "tags": ["4 tags from: Adventure, Relaxation, Culture, Beach, Nature, Romantic, Family, Photography, Food, Luxury, Historical, Spiritual"], "priceValue": 800-3000, "rating": 4.5-5.0, "reviews": 1000-5000}}"""

    try:
        response = await groq_service.generate_response(
            messages=[{"role": "user", "content": prompt}],
            language="en-US",
            temperature=0.7,
            max_tokens=400
        )
        
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        cleaned = cleaned.strip()
        
        # Find JSON boundaries
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            cleaned = cleaned[start:end]
        
        data = json.loads(cleaned)
        
        price_value = data.get("priceValue", random.randint(800, 2500))
        
        result = {
            "id": dest_id,
            "name": dest_info["name"],
            "country": dest_info["country"],
            "region": dest_info["region"],
            "description": data.get("description", f"Discover the beauty of {dest_info['name']}"),
            "fullDescription": data.get("fullDescription", f"Experience {dest_info['name']}, a destination offering unforgettable adventures."),
            "image": dest_info["image"],
            "rating": round(data.get("rating", random.uniform(4.5, 5.0)), 1),
            "reviews": data.get("reviews", random.randint(1000, 5000)),
            "duration": random.choice(DURATIONS),
            "price": f"${price_value:,}",
            "priceValue": price_value,
            "badge": random.choice(BADGES) if random.random() > 0.4 else None,
            "bestTimeToVisit": dest_info["bestTimeToVisit"],
            "climate": dest_info["climate"],
            "highlights": data.get("highlights", [])[:6],
            "tags": data.get("tags", random.sample(TAGS_POOL, 4))[:4],
            "coordinates": dest_info.get("coordinates"),
        }
        
        # Cache the result (without ID since that changes)
        cache_result = result.copy()
        _cache[cache_key] = cache_result
        _cache_expiry[cache_key] = time.time() + CACHE_TTL
        
        return result
        
    except Exception as e:
        print(f"AI generation failed for {dest_info['name']}: {e}")
        # Return fallback
        price_value = random.randint(800, 2500)
        return {
            "id": dest_id,
            "name": dest_info["name"],
            "country": dest_info["country"],
            "region": dest_info["region"],
            "description": f"Discover the wonders of {dest_info['name']}, {dest_info['country']}.",
            "fullDescription": f"{dest_info['name']} offers travelers an unforgettable experience with stunning landscapes and rich culture.",
            "image": dest_info["image"],
            "rating": round(random.uniform(4.5, 5.0), 1),
            "reviews": random.randint(1000, 5000),
            "duration": random.choice(DURATIONS),
            "price": f"${price_value:,}",
            "priceValue": price_value,
            "badge": random.choice(BADGES) if random.random() > 0.4 else None,
            "bestTimeToVisit": dest_info["bestTimeToVisit"],
            "climate": dest_info["climate"],
            "highlights": [f"Explore {dest_info['name']}", "Local cuisine", "Cultural experiences", "Scenic views", "Historic sites", "Natural beauty"],
            "tags": random.sample(TAGS_POOL, 4),
            "coordinates": dest_info.get("coordinates"),
        }


@router.get("/random", response_model=DestinationsResponse)
async def get_random_destinations(count: int = 9):
    """Get random destinations with real-time AI-generated content (parallel processing for speed)."""
    selected = random.sample(DESTINATION_METADATA, min(count, len(DESTINATION_METADATA)))
    
    # Generate all destinations in PARALLEL for speed (not sequential!)
    tasks = [generate_single_destination(dest, i + 1) for i, dest in enumerate(selected)]
    destinations = await asyncio.gather(*tasks)
    
    return DestinationsResponse(destinations=list(destinations), generated=True)


@router.get("/all", response_model=DestinationsResponse)
async def get_all_destinations():
    """Get all destinations with AI-generated content."""
    tasks = [generate_single_destination(dest, i + 1) for i, dest in enumerate(DESTINATION_METADATA)]
    destinations = await asyncio.gather(*tasks)
    
    return DestinationsResponse(destinations=list(destinations), generated=True)


class SearchRequest(BaseModel):
    query: str
    limit: int = 6


async def generate_destination_from_search(place_name: str, dest_id: int) -> Optional[dict]:
    """Generate a complete destination from a search query using AI."""
    cache_key = f"search_{place_name.lower()}"
    
    # Check cache first
    if cache_key in _cache and time.time() < _cache_expiry.get(cache_key, 0):
        cached = _cache[cache_key].copy()
        cached["id"] = dest_id
        return cached
    
    prompt = f"""Generate complete travel destination info for "{place_name}".

If this is NOT a real travel destination or tourist place, return exactly: {{"error": "not_found"}}

For valid destinations, return ONLY valid JSON (no markdown):
{{
  "name": "Official destination name",
  "country": "Country name",
  "region": "One of: europe, asia, americas, africa, oceania",
  "description": "1-2 compelling sentences about this destination",
  "fullDescription": "3-4 detailed sentences about attractions and experiences",
  "climate": "Climate type (e.g., Mediterranean, Tropical, etc.)",
  "bestTimeToVisit": "Best months to visit (e.g., Apr - Oct)",
  "highlights": ["6 specific must-see attractions or experiences"],
  "tags": ["4 tags from: Adventure, Relaxation, Culture, Beach, Nature, Romantic, Family, Photography, Food, Luxury, Historical, Spiritual"],
  "priceValue": 800-3500,
  "rating": 4.0-5.0,
  "reviews": 500-10000,
  "coordinates": {{"lat": latitude_number, "lng": longitude_number}}
}}"""

    try:
        response = await groq_service.generate_response(
            messages=[{"role": "user", "content": prompt}],
            language="en-US",
            temperature=0.5,
            max_tokens=600
        )
        
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        cleaned = cleaned.strip()
        
        # Find JSON boundaries
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            cleaned = cleaned[start:end]
        
        data = json.loads(cleaned)
        
        # Check if it's an error response
        if data.get("error") == "not_found":
            return None
        
        price_value = data.get("priceValue", random.randint(800, 2500))
        
        # Get an appropriate image from Unsplash based on the destination
        image_query = data.get("name", place_name).replace(" ", "-").lower()
        image_url = f"https://source.unsplash.com/800x600/?{image_query},travel,landmark"
        
        result = {
            "id": dest_id,
            "name": data.get("name", place_name),
            "country": data.get("country", "Unknown"),
            "region": data.get("region", "asia"),
            "description": data.get("description", f"Discover the beauty of {place_name}"),
            "fullDescription": data.get("fullDescription", f"Experience {place_name}, a destination offering unforgettable adventures."),
            "image": image_url,
            "rating": round(data.get("rating", random.uniform(4.0, 5.0)), 1),
            "reviews": data.get("reviews", random.randint(500, 5000)),
            "duration": random.choice(DURATIONS),
            "price": f"${price_value:,}",
            "priceValue": price_value,
            "badge": random.choice(BADGES) if random.random() > 0.5 else None,
            "bestTimeToVisit": data.get("bestTimeToVisit", "Year-round"),
            "climate": data.get("climate", "Varies"),
            "highlights": data.get("highlights", [])[:6],
            "tags": data.get("tags", random.sample(TAGS_POOL, 4))[:4],
            "coordinates": data.get("coordinates"),
        }
        
        # Cache the result
        _cache[cache_key] = result.copy()
        _cache_expiry[cache_key] = time.time() + CACHE_TTL
        
        return result
        
    except Exception as e:
        print(f"AI search generation failed for {place_name}: {e}")
        # Return a basic fallback destination instead of None
        price_value = random.randint(800, 2500)
        return {
            "id": dest_id,
            "name": place_name.title(),
            "country": "Worldwide",
            "region": "asia",
            "description": f"Explore the amazing destination of {place_name.title()}.",
            "fullDescription": f"{place_name.title()} is a wonderful travel destination waiting to be explored. Discover its unique attractions and experiences.",
            "image": f"https://source.unsplash.com/800x600/?{place_name.replace(' ', '-')},travel,tourism",
            "rating": round(random.uniform(4.2, 4.9), 1),
            "reviews": random.randint(500, 3000),
            "duration": random.choice(DURATIONS),
            "price": f"${price_value:,}",
            "priceValue": price_value,
            "badge": "AI Generated",
            "bestTimeToVisit": "Year-round",
            "climate": "Varies",
            "highlights": [f"Explore {place_name.title()}", "Local experiences", "Cultural attractions", "Scenic views", "Local cuisine", "Historic sites"],
            "tags": ["Adventure", "Culture", "Photography", "Historical"],
            "coordinates": None,
        }


@router.get("/search")
async def search_destinations(query: str, limit: int = 6):
    """Search for any destination worldwide using AI. 
    Returns matching predefined destinations plus AI-generated results for new places."""
    
    query_lower = query.lower().strip()
    
    if not query_lower or len(query_lower) < 2:
        return {"destinations": [], "query": query}
    
    # First, search in predefined destinations
    matching_predefined = []
    for i, dest in enumerate(DESTINATION_METADATA):
        if (query_lower in dest["name"].lower() or 
            query_lower in dest["country"].lower()):
            matching_predefined.append((dest, i))
    
    # Generate predefined matches with AI content
    predefined_tasks = [
        generate_single_destination(dest, i + 1) 
        for dest, i in matching_predefined[:limit]
    ]
    
    # Always try to generate AI destination for the search query
    # This allows searching for any place in the world
    ai_result = await generate_destination_from_search(query, 1000)
    
    # Wait for predefined results
    predefined_results = await asyncio.gather(*predefined_tasks) if predefined_tasks else []
    
    # Combine results, avoiding duplicates
    all_destinations = []
    seen_names = set()
    
    # Add AI result first if it exists and matches query well
    if ai_result:
        all_destinations.append(ai_result)
        seen_names.add(ai_result["name"].lower())
    
    # Add predefined matches
    for dest in predefined_results:
        if dest["name"].lower() not in seen_names:
            all_destinations.append(dest)
            seen_names.add(dest["name"].lower())
    
    return {
        "destinations": all_destinations[:limit],
        "query": query,
        "total": len(all_destinations)
    }


@router.delete("/cache")
async def clear_cache():
    """Clear the destination cache to force fresh AI generation."""
    global _cache, _cache_expiry
    _cache = {}
    _cache_expiry = {}
    return {"message": "Cache cleared", "status": "success"}

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.groq_service import groq_service
import json

router = APIRouter()

class ItineraryRequest(BaseModel):
    destination: str
    duration: int  # days
    interests: List[str]
    budget: str  # "budget", "moderate", "luxury"
    travel_style: str  # "relaxed", "balanced", "packed"
    language: str = "en-US"

class Activity(BaseModel):
    time: str
    title: str
    description: str
    location: str
    duration: str
    cost: Optional[str] = None
    tips: Optional[str] = None

class DayPlan(BaseModel):
    day: int
    title: str
    activities: List[Activity]
    meals: Optional[dict] = None
    notes: Optional[str] = None

class ItineraryResponse(BaseModel):
    destination: str
    duration: int
    summary: str
    days: List[DayPlan]
    budget_estimate: str
    packing_tips: List[str]
    local_phrases: Optional[List[dict]] = None


@router.post("/generate")
async def generate_itinerary(request: ItineraryRequest):
    """Generate a detailed trip itinerary using AI."""
    
    interests_str = ", ".join(request.interests)
    
    # Determine number of activities based on travel style
    activities_per_day = {
        "relaxed": "3-4",
        "balanced": "4-5", 
        "packed": "5-7"
    }.get(request.travel_style, "4-5")
    
    prompt = f"""You are an expert travel planner. Create a DETAILED and SPECIFIC {request.duration}-day travel itinerary for {request.destination}.

IMPORTANT REQUIREMENTS:
1. Each day MUST have DIFFERENT activities - no repetition across days
2. Use REAL, SPECIFIC places with actual names (not generic "city center" or "local restaurant")
3. Include exact addresses or well-known location names
4. Vary the times - not every day should start at 9 AM
5. Activities should match the traveler's interests: {interests_str}
6. Budget level: {request.budget} (budget=$20-50/day, moderate=$50-150/day, luxury=$150+/day for activities)
7. Travel pace: {request.travel_style} ({activities_per_day} activities per day)

For {request.destination}, include famous landmarks, hidden gems, local favorites, specific restaurants by name, museums, parks, neighborhoods to explore, etc.

Return ONLY valid JSON (no markdown):
{{
    "summary": "Exciting 2-3 sentence overview mentioning specific highlights",
    "days": [
        {{
            "day": 1,
            "title": "Specific theme like 'Historic Old Town & River Cruise' or 'Beach Day at [specific beach name]'",
            "activities": [
                {{
                    "time": "08:30 AM",
                    "title": "Specific activity like 'Sunrise at [landmark name]'",
                    "description": "Detailed 2-3 sentences about what to do, what to see, why it's special",
                    "location": "Exact place name with neighborhood/area",
                    "duration": "2 hours",
                    "cost": "$XX or Free",
                    "tips": "Specific practical tip for this exact place"
                }}
            ],
            "meals": {{
                "breakfast": "Specific restaurant name - specialty dish recommendation",
                "lunch": "Specific restaurant name - what to order",
                "dinner": "Specific restaurant name - known for what cuisine"
            }},
            "notes": "Specific transportation or timing advice for this day"
        }}
    ],
    "budget_estimate": "Total $X,XXX - $X,XXX breakdown",
    "packing_tips": ["5 specific tips for {request.destination}'s weather/culture"],
    "local_phrases": [
        {{"phrase": "Hello", "translation": "actual local translation", "pronunciation": "phonetic guide"}}
    ]
}}

Generate exactly {request.duration} unique days with {activities_per_day} activities each. Make it feel like a real, personalized travel guide."""

    try:
        response = await groq_service.generate_response(
            messages=[{"role": "user", "content": prompt}],
            language=request.language,
            temperature=0.9,
            max_tokens=6000
        )
        
        # Clean up response
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        cleaned = cleaned.strip()
        
        # Find JSON object boundaries
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            cleaned = cleaned[start:end]
        
        data = json.loads(cleaned)
        
        # Validate we have proper days
        days = data.get("days", [])
        if not days or len(days) < request.duration:
            return generate_smart_fallback_itinerary(request)
        
        return {
            "destination": request.destination,
            "duration": request.duration,
            "summary": data.get("summary", f"An amazing {request.duration}-day adventure in {request.destination}"),
            "days": days,
            "budget_estimate": data.get("budget_estimate", "Varies based on choices"),
            "packing_tips": data.get("packing_tips", []),
            "local_phrases": data.get("local_phrases", [])
        }
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return generate_smart_fallback_itinerary(request)
    except Exception as e:
        print(f"Itinerary generation error: {e}")
        return generate_smart_fallback_itinerary(request)


def generate_smart_fallback_itinerary(request: ItineraryRequest) -> dict:
    """Generate a smarter fallback itinerary with destination-aware content."""
    
    # Destination-specific activity templates - plenty of activities to avoid repetition
    DESTINATION_DATA = {
        "paris": {
            "day_plans": [
                {"title": "Iconic Landmarks & First Impressions", "activities": [
                    {"time": "09:00 AM", "title": "Eiffel Tower Visit", "location": "Champ de Mars, 5 Avenue Anatole France", "description": "Start your Parisian adventure at the iconic Eiffel Tower. Take the elevator to the top for breathtaking city views.", "cost": "$28", "tips": "Book tickets online to skip the long queues", "duration": "2-3 hours"},
                    {"time": "12:00 PM", "title": "Trocadéro Gardens & Lunch", "location": "Place du Trocadéro", "description": "Walk across to Trocadéro for the best photo opportunity of the Eiffel Tower, then enjoy lunch at Café de l'Homme.", "cost": "$30-50", "tips": "Great for Instagram photos in the morning light", "duration": "1.5 hours"},
                    {"time": "02:30 PM", "title": "Seine River Walk to Musée d'Orsay", "location": "Along the Seine", "description": "Stroll along the riverbank, cross Pont Alexandre III, and visit the stunning Impressionist collection at Musée d'Orsay.", "cost": "$16", "tips": "Thursday evenings are open late", "duration": "3 hours"},
                    {"time": "06:00 PM", "title": "Seine River Cruise at Sunset", "location": "Port de la Bourdonnais", "description": "Enjoy a romantic sunset cruise along the Seine, passing Notre-Dame and illuminated bridges.", "cost": "$18", "tips": "Book the 6 PM departure for golden hour", "duration": "1 hour"},
                    {"time": "08:00 PM", "title": "Dinner in Saint-Germain-des-Prés", "location": "6th Arrondissement", "description": "Dine at Le Procope, Paris's oldest café, or explore bistros on Rue de Buci.", "cost": "$45-70", "tips": "Try the classic French onion soup", "duration": "2 hours"},
                ]},
                {"title": "Art, Culture & Montmartre", "activities": [
                    {"time": "08:30 AM", "title": "Montmartre & Sacré-Cœur Sunrise", "location": "35 Rue du Chevalier de la Barre", "description": "Beat the crowds and watch the sunrise from the steps of Sacré-Cœur Basilica with panoramic city views.", "cost": "Free", "tips": "Take the funicular to save your legs", "duration": "2 hours"},
                    {"time": "11:00 AM", "title": "Place du Tertre Artists", "location": "Place du Tertre, Montmartre", "description": "Watch local artists paint, get a portrait done, and explore the charming cobblestone streets.", "cost": "$20-50 for portrait", "tips": "Negotiate prices before sitting", "duration": "1.5 hours"},
                    {"time": "01:00 PM", "title": "Lunch at Pink Mamma", "location": "20bis Rue de Douai", "description": "Instagram-famous Italian restaurant with incredible pasta and stunning interior design.", "cost": "$25-40", "tips": "Book ahead or arrive at 12:30", "duration": "1.5 hours"},
                    {"time": "03:00 PM", "title": "Louvre Museum Deep Dive", "location": "Rue de Rivoli, 75001", "description": "Explore the world's largest art museum. See Mona Lisa, Venus de Milo, Winged Victory, and Egyptian antiquities.", "cost": "$17", "tips": "Enter through Carrousel entrance for shorter lines", "duration": "4 hours"},
                    {"time": "08:00 PM", "title": "Le Marais Evening Stroll & Dinner", "location": "Le Marais District", "description": "Explore the trendy Le Marais, visit L'As du Fallafel, then dinner at Chez Janou with famous chocolate mousse.", "cost": "$30-50", "tips": "Walk along Rue des Rosiers", "duration": "2.5 hours"},
                ]},
                {"title": "Royal Grandeur at Versailles", "activities": [
                    {"time": "08:00 AM", "title": "Early Train to Versailles", "location": "RER C from Paris", "description": "Take the 40-minute train ride to beat the crowds at the Palace of Versailles.", "cost": "$7 round trip", "tips": "Buy tickets at any RER station", "duration": "45 mins"},
                    {"time": "09:30 AM", "title": "Palace of Versailles Tour", "location": "Place d'Armes, 78000 Versailles", "description": "Explore the opulent Hall of Mirrors, King's apartments, and Marie Antoinette's chambers.", "cost": "$21", "tips": "Download the free audio guide app", "duration": "3 hours"},
                    {"time": "01:00 PM", "title": "Gardens of Versailles Picnic", "location": "Palace Gardens", "description": "Rent a rowboat on the Grand Canal, explore the fountains, and enjoy a French picnic on the lawns.", "cost": "$20", "tips": "Buy supplies at the market near the station", "duration": "2.5 hours"},
                    {"time": "04:00 PM", "title": "Marie Antoinette's Estate", "location": "Petit Trianon", "description": "Visit the Queen's private retreat, including the charming Hamlet where she played at being a peasant.", "cost": "Included", "tips": "Less crowded in late afternoon", "duration": "1.5 hours"},
                    {"time": "07:00 PM", "title": "Return & Champs-Élysées Dinner", "location": "Avenue des Champs-Élysées", "description": "Return to Paris, stroll the famous avenue, and dine at a classic brasserie near Arc de Triomphe.", "cost": "$40-60", "tips": "Try Le Fouquet's for a splurge", "duration": "2.5 hours"},
                ]},
            ],
            "restaurants": {"breakfast": "Café de Flore - classic croissants", "lunch": "Le Comptoir du Panthéon", "dinner": "Le Bouillon Chartier"},
            "phrases": [{"phrase": "Hello", "translation": "Bonjour", "pronunciation": "bohn-ZHOOR"}, {"phrase": "Thank you", "translation": "Merci", "pronunciation": "mehr-SEE"}, {"phrase": "Please", "translation": "S'il vous plaît", "pronunciation": "seel voo PLEH"}, {"phrase": "Excuse me", "translation": "Excusez-moi", "pronunciation": "ex-koo-zay MWAH"}]
        },
        "tokyo": {
            "day_plans": [
                {"title": "Classic Tokyo Icons", "activities": [
                    {"time": "06:00 AM", "title": "Tsukiji Outer Market Breakfast", "location": "4 Chome-16-2 Tsukiji, Chuo City", "description": "Experience the buzzing atmosphere of Tokyo's famous fish market and enjoy the freshest sushi breakfast of your life.", "cost": "$15-30", "tips": "Arrive early for the freshest seafood. Try Sushi Dai or Daiwa Sushi.", "duration": "1.5 hours"},
                    {"time": "08:30 AM", "title": "Senso-ji Temple & Asakusa", "location": "2 Chome-3-1 Asakusa, Taito City", "description": "Visit Tokyo's oldest and most significant temple. Walk through the iconic Thunder Gate (Kaminarimon) and Nakamise shopping street.", "cost": "Free", "tips": "Draw an omikuji fortune for ¥100. Get there before 9 AM for fewer crowds.", "duration": "2 hours"},
                    {"time": "11:00 AM", "title": "Tokyo Skytree Observation", "location": "1 Chome-1-2 Oshiage, Sumida City", "description": "Ascend the world's tallest tower (634m) for 360-degree views of Tokyo and Mount Fuji on clear days.", "cost": "$18", "tips": "Visit on a clear morning for best visibility. Tembo Deck at 350m offers stunning views.", "duration": "1.5 hours"},
                    {"time": "01:30 PM", "title": "Ramen Lunch at Ichiran", "location": "Various locations - try Shibuya", "description": "Experience solo-dining booths at Japan's most famous tonkotsu ramen chain. Customize your broth, noodles, and toppings.", "cost": "$12", "tips": "Order extra chashu and a soft-boiled egg. Use the ticket machine.", "duration": "1 hour"},
                    {"time": "03:30 PM", "title": "Shibuya Crossing & Hachiko", "location": "Shibuya Station", "description": "Cross the world's busiest intersection with 3,000 people at once. Visit the famous Hachiko dog statue.", "cost": "Free", "tips": "Watch from Starbucks 2nd floor or Magnet by Shibuya 109 rooftop for best views.", "duration": "1.5 hours"},
                    {"time": "06:00 PM", "title": "Shinjuku Golden Gai", "location": "1 Chome Kabukicho, Shinjuku", "description": "Explore 200+ tiny themed bars in narrow alleys. Each bar seats only 6-10 people with unique personalities.", "cost": "$20-40", "tips": "Some bars charge ¥500-1000 seating fee. Look for foreigner-friendly signs.", "duration": "3 hours"},
                ]},
                {"title": "Culture, Art & Harajuku", "activities": [
                    {"time": "08:00 AM", "title": "Meiji Shrine Morning Walk", "location": "1-1 Yoyogikamizonocho, Shibuya", "description": "Start your day with a peaceful walk through the forested path to this serene Shinto shrine dedicated to Emperor Meiji.", "cost": "Free", "tips": "Write a wish on an ema wooden plaque. Watch for traditional Shinto weddings.", "duration": "1.5 hours"},
                    {"time": "10:00 AM", "title": "Harajuku & Takeshita Street", "location": "Harajuku Station", "description": "Dive into Tokyo's youth culture, unique fashion, and try colorful cotton candy and crepes.", "cost": "$10-20", "tips": "Visit on weekends for the best people-watching. Try a rainbow crepe!", "duration": "2 hours"},
                    {"time": "12:30 PM", "title": "Omotesando Avenue Lunch", "location": "Omotesando", "description": "Tokyo's Champs-Élysées with designer boutiques. Lunch at Omotesando Koffee or kawaii-themed café.", "cost": "$15-25", "tips": "Visit the Tokyu Plaza rooftop garden for photos.", "duration": "1.5 hours"},
                    {"time": "02:30 PM", "title": "teamLab Borderless", "location": "Azabudai Hills Garden Plaza B", "description": "Immerse yourself in digital art installations at this mind-bending interactive museum where art moves between rooms.", "cost": "$32", "tips": "Wear white for photos - colors reflect beautifully. Allow 3+ hours.", "duration": "3 hours"},
                    {"time": "06:30 PM", "title": "Shibuya Sky Sunset", "location": "Shibuya Scramble Square, 45-46F", "description": "Watch sunset from the stunning rooftop observation deck with 360-degree views of Tokyo.", "cost": "$20", "tips": "Book the 6 PM slot for golden hour. Open-air rooftop!", "duration": "1.5 hours"},
                    {"time": "08:30 PM", "title": "Gonpachi 'Kill Bill' Dinner", "location": "Nishi-Azabu", "description": "Dine at the restaurant that inspired the famous Kill Bill fight scene. Try the robata-grilled dishes.", "cost": "$40-60", "tips": "Reservation recommended. Get the soba noodles.", "duration": "2 hours"},
                ]},
                {"title": "Geek Culture & Hidden Gems", "activities": [
                    {"time": "09:00 AM", "title": "Akihabara Electric Town", "location": "Akihabara Station", "description": "Explore anime shops, retro gaming arcades, electronics stores, and experience a maid café.", "cost": "Varies", "tips": "Visit Yodobashi Camera for duty-free electronics. Try Super Potato for retro games.", "duration": "3 hours"},
                    {"time": "12:30 PM", "title": "Themed Café Experience", "location": "Akihabara", "description": "Visit a maid café, robot café, or animal café for a uniquely Japanese lunch experience.", "cost": "$20-30", "tips": "Maidreamin is tourist-friendly. Prepare for kawaii overload!", "duration": "1.5 hours"},
                    {"time": "02:30 PM", "title": "Yanaka Old Town District", "location": "Yanaka, Taito City", "description": "Step back in time in this traditional neighborhood that survived WWII. Visit temples, craft shops, and Yanaka Cemetery.", "cost": "Free", "tips": "Try the famous Yanaka Ginza shopping street snacks.", "duration": "2 hours"},
                    {"time": "05:00 PM", "title": "Ueno Park & Museums", "location": "Ueno Park", "description": "Explore Japan's first public park with Tokyo National Museum, temples, and the famous Shinobazu Pond.", "cost": "$5-10", "tips": "Great for cherry blossoms in spring. Visit Ameya-Yokocho market nearby.", "duration": "2 hours"},
                    {"time": "07:30 PM", "title": "Izakaya Dinner in Yurakucho", "location": "Under the train tracks, Yurakucho", "description": "Experience authentic Japanese pub culture at the atmospheric izakayas built under the railway tracks.", "cost": "$25-45", "tips": "Try yakitori and highballs. Very local atmosphere!", "duration": "2.5 hours"},
                ]},
            ],
            "restaurants": {"breakfast": "Tsukiji Market - fresh sushi", "lunch": "Ichiran Ramen - famous tonkotsu", "dinner": "Gonpachi Nishi-Azabu"},
            "phrases": [{"phrase": "Hello", "translation": "Konnichiwa", "pronunciation": "koh-nee-chee-WAH"}, {"phrase": "Thank you", "translation": "Arigatou gozaimasu", "pronunciation": "ah-ree-GAH-toh go-zai-MAHS"}, {"phrase": "Excuse me", "translation": "Sumimasen", "pronunciation": "soo-mee-mah-SEN"}, {"phrase": "Delicious!", "translation": "Oishii!", "pronunciation": "oy-SHEE"}]
        },
        "bali": {
            "day_plans": [
                {"title": "Ubud Culture & Rice Terraces", "activities": [
                    {"time": "06:00 AM", "title": "Tegallalang Rice Terraces Sunrise", "location": "Tegallalang, Ubud", "description": "Watch the sunrise over the iconic UNESCO rice terraces. Walk through the lush paddies on wooden walkways.", "cost": "$3", "tips": "Arrive before 7 AM for fewer crowds. Wear sturdy shoes.", "duration": "2 hours"},
                    {"time": "09:00 AM", "title": "Tirta Empul Holy Water Temple", "location": "Tampaksiring", "description": "Experience a Balinese purification ritual at this sacred water temple. Bathe in the holy springs.", "cost": "$3", "tips": "Wear modest clothing. Bring change of clothes to get wet.", "duration": "1.5 hours"},
                    {"time": "11:30 AM", "title": "Ubud Monkey Forest", "location": "Jl. Monkey Forest, Ubud", "description": "Walk through the mystical forest with 700+ Balinese long-tailed macaques and ancient temples.", "cost": "$5", "tips": "Don't bring food or shiny objects. Monkeys will grab!", "duration": "1.5 hours"},
                    {"time": "01:30 PM", "title": "Lunch at Locavore", "location": "Jl. Dewisita No.10, Ubud", "description": "Award-winning farm-to-table restaurant featuring Indonesian ingredients in creative presentations.", "cost": "$40-60", "tips": "Book well in advance. Try the tasting menu.", "duration": "2 hours"},
                    {"time": "04:00 PM", "title": "Ubud Art Market & Palace", "location": "Jl. Raya Ubud", "description": "Shop for handmade crafts, paintings, and textiles. Visit the royal Ubud Palace next door.", "cost": "Free-varies", "tips": "Bargain! Start at 50% of asking price.", "duration": "2 hours"},
                    {"time": "07:00 PM", "title": "Traditional Kecak Fire Dance", "location": "Ubud Palace or Uluwatu", "description": "Watch the mesmerizing Kecak dance performed at sunset with a chorus of 100+ men.", "cost": "$10-15", "tips": "Arrive early for front seats. No instruments - all vocal!", "duration": "1.5 hours"},
                ]},
                {"title": "Beaches, Temples & Waterfalls", "activities": [
                    {"time": "07:00 AM", "title": "Sekumpul Waterfall Adventure", "location": "Sekumpul, North Bali", "description": "Trek through jungle to Bali's most beautiful multi-strand waterfall. A true hidden paradise.", "cost": "$5 + guide", "tips": "Wear water shoes. 300+ steps down (and back up!)", "duration": "3 hours"},
                    {"time": "11:00 AM", "title": "Lempuyang Temple Gates of Heaven", "location": "Karangasem", "description": "Photograph the iconic 'Gates of Heaven' framing Mount Agung. One of Bali's most sacred temples.", "cost": "$5", "tips": "Book sunrise photos in advance. Queue can be 2+ hours.", "duration": "2 hours"},
                    {"time": "02:00 PM", "title": "Traditional Balinese Lunch", "location": "Warung local restaurant", "description": "Enjoy authentic Nasi Campur (mixed rice plate) at a local warung with volcano views.", "cost": "$5-10", "tips": "Try babi guling (suckling pig) if non-vegetarian.", "duration": "1 hour"},
                    {"time": "04:00 PM", "title": "Seminyak Beach Sunset", "location": "Seminyak Beach", "description": "Relax on stylish beach beds, swim in the waves, and watch the legendary Bali sunset.", "cost": "Free-$20", "tips": "Ku De Ta or Potato Head for upscale beach clubs.", "duration": "3 hours"},
                    {"time": "08:00 PM", "title": "Seminyak Restaurant & Nightlife", "location": "Jl. Laksmana (Eat Street)", "description": "Dine at world-class restaurants and experience Bali's famous nightlife scene.", "cost": "$30-60", "tips": "Try Sarong for Asian fusion or Mama San for Southeast Asian.", "duration": "3 hours"},
                ]},
            ],
            "restaurants": {"breakfast": "Café Organic - healthy bowls", "lunch": "Warung Babi Guling - local pork", "dinner": "Locavore - fine dining"},
            "phrases": [{"phrase": "Hello", "translation": "Om Swastiastu", "pronunciation": "ohm swas-tee-AH-stoo"}, {"phrase": "Thank you", "translation": "Suksma", "pronunciation": "SOOK-sma"}, {"phrase": "Delicious", "translation": "Jaen", "pronunciation": "ja-EN"}]
        }
    }
    
    # Default for unknown destinations
    DEFAULT_DAY_PLANS = [
        {"title": "Iconic Landmarks & First Impressions", "activities": [
            {"time": "09:00 AM", "title": "Historic City Center Walking Tour", "location": "Main Square / Old Town", "description": f"Start with a walking tour of {request.destination}'s historic center, discovering iconic architecture and local culture.", "cost": "$10-20", "tips": "Join a free walking tour for local insights", "duration": "2.5 hours"},
            {"time": "12:00 PM", "title": "Famous Local Market", "location": "Central Market", "description": "Explore the main market, sample local delicacies and interact with friendly vendors.", "cost": "$15-25", "tips": "Bring cash for small vendors", "duration": "1.5 hours"},
            {"time": "02:00 PM", "title": "Top Museum or Gallery", "location": "National/City Museum", "description": "Discover the history and art of the region at the main cultural institution.", "cost": "$12-25", "tips": "Check for free admission days", "duration": "2.5 hours"},
            {"time": "05:00 PM", "title": "Sunset at Famous Viewpoint", "location": "Popular Lookout Point", "description": "Head to the best viewpoint for sunset photos and panoramic views.", "cost": "Free-$10", "tips": "Arrive 30 mins before sunset", "duration": "1.5 hours"},
            {"time": "07:30 PM", "title": "Traditional Restaurant Dinner", "location": "Local Restaurant District", "description": "Enjoy authentic local cuisine at a highly-rated traditional restaurant.", "cost": "$25-50", "tips": "Make reservations in advance", "duration": "2 hours"},
        ]},
        {"title": "Cultural Immersion Day", "activities": [
            {"time": "08:00 AM", "title": "Local Neighborhood Exploration", "location": "Authentic Local District", "description": f"Explore a non-touristy neighborhood to experience real life in {request.destination}.", "cost": "Free", "tips": "Get breakfast at a local café", "duration": "2 hours"},
            {"time": "10:30 AM", "title": "Cooking Class Experience", "location": "Local Cooking School", "description": "Learn to make traditional dishes with a local chef in a hands-on cooking class.", "cost": "$40-80", "tips": "Book in advance online", "duration": "3 hours"},
            {"time": "02:30 PM", "title": "Hidden Gem Landmark", "location": "Lesser-known Attraction", "description": "Visit a beautiful but less crowded attraction that locals love.", "cost": "$5-15", "tips": "Ask your guide for recommendations", "duration": "2 hours"},
            {"time": "05:00 PM", "title": "Local Park or Garden", "location": "City Park", "description": "Relax in a beautiful park, people-watch, and enjoy the local atmosphere.", "cost": "Free", "tips": "Great for photography", "duration": "1.5 hours"},
            {"time": "07:00 PM", "title": "Street Food Tour", "location": "Food Stall District", "description": "Sample various street food specialties on a self-guided or organized food tour.", "cost": "$15-30", "tips": "Come hungry! Try at least 5 things", "duration": "2.5 hours"},
        ]},
        {"title": "Day Trip & Adventure", "activities": [
            {"time": "07:00 AM", "title": "Early Morning Departure", "location": "Hotel/City Center", "description": f"Head out early for a day trip to a popular destination near {request.destination}.", "cost": "$20-50 transport", "tips": "Pack snacks and water", "duration": "1-2 hours travel"},
            {"time": "09:30 AM", "title": "Major Day Trip Attraction", "location": "Nearby Famous Site", "description": "Explore the main attraction of your day trip with guided or self-guided touring.", "cost": "$15-30", "tips": "Download offline maps", "duration": "3 hours"},
            {"time": "01:00 PM", "title": "Local Lunch Experience", "location": "Day Trip Location", "description": "Enjoy lunch at a local restaurant in the day trip area, trying regional specialties.", "cost": "$15-25", "tips": "Ask locals for recommendations", "duration": "1.5 hours"},
            {"time": "03:00 PM", "title": "Secondary Attractions", "location": "Nearby Sites", "description": "Visit additional points of interest in the area before heading back.", "cost": "$10-20", "tips": "Check closing times", "duration": "2 hours"},
            {"time": "06:00 PM", "title": "Return & Relaxed Dinner", "location": "Back in City", "description": "Return to the city and enjoy a relaxed dinner at a restaurant you've been wanting to try.", "cost": "$30-50", "tips": "Book ahead for popular spots", "duration": "2.5 hours"},
        ]},
    ]
    
    # Get destination-specific data or default
    dest_lower = request.destination.lower()
    dest_data = None
    for key in DESTINATION_DATA:
        if key in dest_lower:
            dest_data = DESTINATION_DATA[key]
            break
    
    # Build days from day_plans
    days = []
    if dest_data and "day_plans" in dest_data:
        day_plans = dest_data["day_plans"]
        for i in range(request.duration):
            plan = day_plans[i % len(day_plans)]
            days.append({
                "day": i + 1,
                "title": plan["title"],
                "activities": plan["activities"],
                "meals": dest_data.get("restaurants", {}),
                "notes": f"Day {i+1}: {plan['title']} - Take your time and enjoy!"
            })
        phrases = dest_data.get("phrases", [])
    else:
        # Use default plans
        for i in range(request.duration):
            plan = DEFAULT_DAY_PLANS[i % len(DEFAULT_DAY_PLANS)]
            days.append({
                "day": i + 1,
                "title": plan["title"],
                "activities": plan["activities"],
                "meals": {"breakfast": "Local café", "lunch": "Popular eatery", "dinner": "Traditional restaurant"},
                "notes": f"Day {i+1}: {plan['title']} - Enjoy your adventure!"
            })
        phrases = [{"phrase": "Hello", "translation": "Hello", "pronunciation": "Hello"}, {"phrase": "Thank you", "translation": "Thank you", "pronunciation": "Thank you"}]
    
    budget_estimates = {
        "budget": f"${request.duration * 80}-${request.duration * 120}",
        "moderate": f"${request.duration * 150}-${request.duration * 250}",
        "luxury": f"${request.duration * 300}-${request.duration * 500}"
    }
    
    return {
        "destination": request.destination,
        "duration": request.duration,
        "summary": f"Experience {request.duration} amazing days in {request.destination}! From iconic landmarks to hidden local gems, this itinerary balances must-see attractions with authentic experiences tailored to your {request.travel_style} travel style.",
        "days": days,
        "budget_estimate": budget_estimates.get(request.budget, "$1,000 - $2,500"),
        "packing_tips": [
            "Comfortable walking shoes - you'll cover lots of ground",
            "Universal power adapter for your electronics",
            "Light layers for changing temperatures",
            "Small daypack for daily essentials",
            "Portable phone charger for navigation"
        ],
        "local_phrases": phrases
    }


@router.post("/customize")
async def customize_itinerary(
    itinerary: dict,
    modifications: str,
    language: str = "en-US"
):
    """Customize an existing itinerary based on user modifications."""
    
    prompt = f"""Here is a travel itinerary:
{json.dumps(itinerary, indent=2)}

The user wants to make these modifications: {modifications}

Return the updated itinerary as a JSON object with the same structure, incorporating the requested changes. Return ONLY the JSON, no other text."""

    try:
        response = await groq_service.generate_response(
            messages=[{"role": "user", "content": prompt}],
            language=language,
            temperature=0.7,
            max_tokens=4000
        )
        
        # Clean up response
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        cleaned = cleaned.strip()
        
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            cleaned = cleaned[start:end]
        
        return json.loads(cleaned)
        
    except Exception as e:
        print(f"Customization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

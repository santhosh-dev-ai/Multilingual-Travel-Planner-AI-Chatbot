from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import random

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

# Pre-generated complete destination data for instant loading
DESTINATION_POOL = [
    {
        "name": "Santorini",
        "country": "Greece",
        "region": "europe",
        "coordinates": {"lat": 36.3932, "lng": 25.4615},
        "image": "https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e?w=800&q=80",
        "climate": "Mediterranean",
        "bestTimeToVisit": "Apr - Oct",
        "description": "Santorini captivates with its iconic white-washed buildings, stunning sunsets, and crystal-clear waters of the Aegean Sea.",
        "fullDescription": "Santorini is a breathtaking Greek island known for its dramatic cliffs, romantic ambiance, and ancient history. Explore the charming villages of Oia and Fira, relax on unique volcanic beaches, and savor exquisite Mediterranean cuisine while watching legendary sunsets.",
        "highlights": ["Oia sunset views", "Volcanic beaches", "Ancient Akrotiri ruins", "Wine tasting tours", "Caldera boat trips", "Traditional Greek cuisine"],
        "tags": ["Romantic", "Photography", "Beach", "Culture"],
        "priceValue": 1800,
        "rating": 4.9,
        "reviews": 4250,
        "duration": "4-5 days",
        "badge": "Romantic"
    },
    {
        "name": "Kyoto",
        "country": "Japan",
        "region": "asia",
        "coordinates": {"lat": 35.0116, "lng": 135.7681},
        "image": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80",
        "climate": "Temperate",
        "bestTimeToVisit": "Mar - May, Oct - Nov",
        "description": "Kyoto is Japan's cultural heart, home to ancient temples, traditional geisha districts, and serene bamboo forests.",
        "fullDescription": "Step back in time in Kyoto, where centuries-old traditions blend seamlessly with modern life. Wander through thousands of vermillion torii gates at Fushimi Inari, experience a traditional tea ceremony, and witness the beauty of cherry blossoms or autumn foliage in historic gardens.",
        "highlights": ["Fushimi Inari Shrine", "Arashiyama Bamboo Grove", "Kinkaku-ji Temple", "Gion geisha district", "Traditional tea ceremonies", "Nishiki Market"],
        "tags": ["Culture", "Historical", "Spiritual", "Photography"],
        "priceValue": 2200,
        "rating": 4.8,
        "reviews": 3800,
        "duration": "5-7 days",
        "badge": "Cultural"
    },
    {
        "name": "Bali",
        "country": "Indonesia",
        "region": "asia",
        "coordinates": {"lat": -8.3405, "lng": 115.0920},
        "image": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80",
        "climate": "Tropical",
        "bestTimeToVisit": "Apr - Oct",
        "description": "Bali enchants visitors with lush rice terraces, ancient temples, world-class surfing, and a vibrant spiritual culture.",
        "fullDescription": "The Island of the Gods offers an irresistible blend of adventure, relaxation, and cultural immersion. From the artistic hub of Ubud to the beach parties of Seminyak, Bali caters to every traveler with its stunning landscapes, warm hospitality, and affordable luxury.",
        "highlights": ["Tegallalang Rice Terraces", "Uluwatu Temple sunset", "Ubud Monkey Forest", "World-class surfing", "Balinese spa treatments", "Mount Batur sunrise trek"],
        "tags": ["Adventure", "Relaxation", "Spiritual", "Nature"],
        "priceValue": 1200,
        "rating": 4.7,
        "reviews": 5200,
        "duration": "7-10 days",
        "badge": "Popular"
    },
    {
        "name": "Swiss Alps",
        "country": "Switzerland",
        "region": "europe",
        "coordinates": {"lat": 46.8182, "lng": 8.2275},
        "image": "https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&q=80",
        "climate": "Alpine",
        "bestTimeToVisit": "Jun - Sep, Dec - Mar",
        "description": "The Swiss Alps offer majestic mountain scenery, world-renowned ski resorts, and charming alpine villages.",
        "fullDescription": "Experience the pinnacle of natural beauty in the Swiss Alps, where snow-capped peaks meet pristine lakes and meadows. Whether skiing in winter or hiking in summer, indulge in Swiss chocolate, cheese fondue, and the legendary Swiss precision and hospitality.",
        "highlights": ["Matterhorn views", "Jungfrau railway", "Interlaken adventures", "Zermatt skiing", "Lake Geneva", "Swiss chocolate tours"],
        "tags": ["Adventure", "Nature", "Luxury", "Photography"],
        "priceValue": 2800,
        "rating": 4.9,
        "reviews": 3100,
        "duration": "5-7 days",
        "badge": "Luxury"
    },
    {
        "name": "Marrakech",
        "country": "Morocco",
        "region": "africa",
        "coordinates": {"lat": 31.6295, "lng": -7.9811},
        "image": "https://images.unsplash.com/photo-1597212618440-806262de4f6b?w=800&q=80",
        "climate": "Semi-arid",
        "bestTimeToVisit": "Mar - May, Sep - Nov",
        "description": "Marrakech dazzles with its vibrant souks, stunning palaces, and the magical atmosphere of Jemaa el-Fnaa square.",
        "fullDescription": "Immerse yourself in the sensory overload of Marrakech, where ancient medinas hide beautiful riads, aromatic spices fill the air, and skilled artisans craft traditional goods. Experience Moroccan hospitality, savor tagine dishes, and explore the gateway to the Sahara.",
        "highlights": ["Jemaa el-Fnaa square", "Majorelle Garden", "Bahia Palace", "Traditional hammams", "Souks shopping", "Atlas Mountains day trip"],
        "tags": ["Culture", "Food", "Adventure", "Historical"],
        "priceValue": 950,
        "rating": 4.6,
        "reviews": 2900,
        "duration": "3-4 days",
        "badge": "Best Value"
    },
    {
        "name": "Iceland",
        "country": "Iceland",
        "region": "europe",
        "coordinates": {"lat": 64.9631, "lng": -19.0208},
        "image": "https://images.unsplash.com/photo-1504829857797-ddff29c27927?w=800&q=80",
        "climate": "Subarctic",
        "bestTimeToVisit": "Jun - Aug, Sep - Mar",
        "description": "Iceland amazes with otherworldly landscapes featuring glaciers, volcanoes, geysers, and the magical Northern Lights.",
        "fullDescription": "Discover the land of fire and ice, where dramatic waterfalls cascade over ancient cliffs, geothermal hot springs dot the landscape, and the Aurora Borealis dances across winter skies. Iceland offers unparalleled adventures in one of Earth's most unique environments.",
        "highlights": ["Northern Lights viewing", "Golden Circle tour", "Blue Lagoon", "Glacier hiking", "Whale watching", "Geysir geothermal area"],
        "tags": ["Adventure", "Nature", "Photography", "Relaxation"],
        "priceValue": 2400,
        "rating": 4.8,
        "reviews": 3400,
        "duration": "5-7 days",
        "badge": "Adventure"
    },
    {
        "name": "Maldives",
        "country": "Maldives",
        "region": "asia",
        "coordinates": {"lat": 3.2028, "lng": 73.2207},
        "image": "https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800&q=80",
        "climate": "Tropical",
        "bestTimeToVisit": "Nov - Apr",
        "description": "The Maldives offers paradise on Earth with crystal-clear turquoise waters, pristine beaches, and luxurious overwater villas.",
        "fullDescription": "Escape to the ultimate tropical paradise where each resort occupies its own private island. Snorkel among vibrant coral reefs, dine under the stars, and experience unmatched luxury in overwater bungalows surrounded by the Indian Ocean's mesmerizing blue waters.",
        "highlights": ["Overwater villas", "Snorkeling & diving", "Underwater restaurants", "Private island resorts", "Sunset dolphin cruises", "Spa treatments"],
        "tags": ["Romantic", "Luxury", "Beach", "Relaxation"],
        "priceValue": 3500,
        "rating": 4.9,
        "reviews": 2800,
        "duration": "5-7 days",
        "badge": "Luxury"
    },
    {
        "name": "New Zealand",
        "country": "New Zealand",
        "region": "oceania",
        "coordinates": {"lat": -40.9006, "lng": 174.8860},
        "image": "https://images.unsplash.com/photo-1469521669194-babb45599def?w=800&q=80",
        "climate": "Temperate",
        "bestTimeToVisit": "Dec - Feb",
        "description": "New Zealand captivates with dramatic landscapes from fjords to volcanic peaks, and world-famous adventure sports.",
        "fullDescription": "Journey through Middle-earth in New Zealand, where every turn reveals breathtaking scenery. From the glowworm caves of Waitomo to the adrenaline capital of Queenstown, experience Maori culture, pristine wilderness, and adventures that will leave you speechless.",
        "highlights": ["Milford Sound cruises", "Hobbiton Movie Set", "Queenstown adventures", "Rotorua geothermal", "Glowworm caves", "Franz Josef Glacier"],
        "tags": ["Adventure", "Nature", "Photography", "Culture"],
        "priceValue": 2600,
        "rating": 4.8,
        "reviews": 3200,
        "duration": "10-14 days",
        "badge": "Adventure"
    },
    {
        "name": "Barcelona",
        "country": "Spain",
        "region": "europe",
        "coordinates": {"lat": 41.3874, "lng": 2.1686},
        "image": "https://images.unsplash.com/photo-1583422409516-2895a77efded?w=800&q=80",
        "climate": "Mediterranean",
        "bestTimeToVisit": "Apr - Jun, Sep - Oct",
        "description": "Barcelona blends stunning Gaudí architecture, beautiful beaches, world-class cuisine, and vibrant nightlife.",
        "fullDescription": "Experience the creative spirit of Catalonia in Barcelona, where Gaudí's masterpieces like La Sagrada Familia define the skyline. Stroll down Las Ramblas, feast on tapas in Gothic Quarter, relax on Mediterranean beaches, and dance until dawn in legendary clubs.",
        "highlights": ["La Sagrada Familia", "Park Güell", "Las Ramblas", "Gothic Quarter", "La Boqueria Market", "Barceloneta Beach"],
        "tags": ["Culture", "Food", "Nightlife", "Beach"],
        "priceValue": 1500,
        "rating": 4.7,
        "reviews": 4800,
        "duration": "4-5 days",
        "badge": "Popular"
    },
    {
        "name": "Dubai",
        "country": "UAE",
        "region": "asia",
        "coordinates": {"lat": 25.2048, "lng": 55.2708},
        "image": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&q=80",
        "climate": "Desert",
        "bestTimeToVisit": "Nov - Mar",
        "description": "Dubai dazzles with futuristic architecture, luxury shopping, desert adventures, and world-record attractions.",
        "fullDescription": "Welcome to the city of superlatives where the world's tallest building meets traditional souks. Dubai offers an extraordinary blend of ultra-modern luxury and Arabian heritage, from indoor ski slopes to desert safaris, creating experiences found nowhere else on Earth.",
        "highlights": ["Burj Khalifa observation", "Desert safari", "Dubai Mall shopping", "Palm Jumeirah", "Gold & Spice Souks", "Dubai Marina"],
        "tags": ["Luxury", "Adventure", "Family", "Culture"],
        "priceValue": 2000,
        "rating": 4.7,
        "reviews": 4100,
        "duration": "4-5 days",
        "badge": "Family Friendly"
    },
    {
        "name": "Machu Picchu",
        "country": "Peru",
        "region": "americas",
        "coordinates": {"lat": -13.1631, "lng": -72.5450},
        "image": "https://images.unsplash.com/photo-1587595431973-160d0d94add1?w=800&q=80",
        "climate": "Highland",
        "bestTimeToVisit": "May - Sep",
        "description": "Machu Picchu stands as a mystical testament to Incan engineering, set dramatically among Andean peaks.",
        "fullDescription": "Trek through cloud forests to reach the legendary Lost City of the Incas, one of the world's most iconic archaeological sites. Whether arriving by the famous Inca Trail or scenic train, the sunrise over these ancient ruins is an unforgettable spiritual experience.",
        "highlights": ["Inca Trail trek", "Sunrise at the ruins", "Huayna Picchu climb", "Sacred Valley tour", "Cusco exploration", "Traditional Peruvian cuisine"],
        "tags": ["Adventure", "Historical", "Culture", "Spiritual"],
        "priceValue": 1800,
        "rating": 4.9,
        "reviews": 3600,
        "duration": "4-5 days",
        "badge": "Trending"
    },
    {
        "name": "Cape Town",
        "country": "South Africa",
        "region": "africa",
        "coordinates": {"lat": -33.9249, "lng": 18.4241},
        "image": "https://images.unsplash.com/photo-1580060839134-75a5edca2e99?w=800&q=80",
        "climate": "Mediterranean",
        "bestTimeToVisit": "Nov - Mar",
        "description": "Cape Town offers stunning natural beauty with Table Mountain, pristine beaches, and world-renowned wine regions.",
        "fullDescription": "Discover Africa's most beautiful city where mountains meet the ocean. Ascend Table Mountain for panoramic views, explore the Cape Winelands, visit historic Robben Island, and encounter penguins at Boulders Beach in this diverse and vibrant destination.",
        "highlights": ["Table Mountain cable car", "Cape Winelands", "Robben Island", "Boulders Beach penguins", "Cape Point", "V&A Waterfront"],
        "tags": ["Nature", "Adventure", "Culture", "Food"],
        "priceValue": 1400,
        "rating": 4.7,
        "reviews": 2700,
        "duration": "5-7 days",
        "badge": "Best Value"
    },
    {
        "name": "Petra",
        "country": "Jordan",
        "region": "asia",
        "coordinates": {"lat": 30.3285, "lng": 35.4444},
        "image": "https://images.unsplash.com/photo-1579606032821-4e6161c81571?w=800&q=80",
        "climate": "Desert",
        "bestTimeToVisit": "Mar - May, Sep - Nov",
        "description": "Petra's rose-red carved facades emerge from desert cliffs, revealing an ancient Nabataean city of wonder.",
        "fullDescription": "Walk through the narrow Siq canyon as it opens to reveal the Treasury, Petra's most iconic monument. This UNESCO World Heritage site offers days of exploration through ancient tombs, temples, and theaters carved directly into pink sandstone cliffs over 2,000 years ago.",
        "highlights": ["The Treasury (Al-Khazneh)", "The Siq canyon walk", "Monastery climb", "Petra by Night", "Royal Tombs", "High Place of Sacrifice"],
        "tags": ["Historical", "Adventure", "Culture", "Photography"],
        "priceValue": 1300,
        "rating": 4.8,
        "reviews": 2400,
        "duration": "2-3 days",
        "badge": "Hidden Gem"
    },
    {
        "name": "Banff",
        "country": "Canada",
        "region": "americas",
        "coordinates": {"lat": 51.4968, "lng": -115.9281},
        "image": "https://images.unsplash.com/photo-1503614472-8c93d56e92ce?w=800&q=80",
        "climate": "Alpine",
        "bestTimeToVisit": "Jun - Sep, Dec - Mar",
        "description": "Banff National Park showcases the Canadian Rockies with turquoise lakes, majestic peaks, and abundant wildlife.",
        "fullDescription": "Immerse yourself in the raw beauty of the Canadian Rockies in Banff National Park. Paddle on impossibly turquoise Lake Louise, spot grizzly bears and elk, ski world-class slopes, and soak in natural hot springs surrounded by snow-capped mountain grandeur.",
        "highlights": ["Lake Louise", "Moraine Lake", "Banff Gondola", "Johnston Canyon", "Hot springs", "Wildlife spotting"],
        "tags": ["Nature", "Adventure", "Photography", "Relaxation"],
        "priceValue": 2100,
        "rating": 4.8,
        "reviews": 3000,
        "duration": "4-6 days",
        "badge": "Nature"
    },
    {
        "name": "Amalfi Coast",
        "country": "Italy",
        "region": "europe",
        "coordinates": {"lat": 40.6333, "lng": 14.6029},
        "image": "https://images.unsplash.com/photo-1534113414509-0eec2bfb493f?w=800&q=80",
        "climate": "Mediterranean",
        "bestTimeToVisit": "May - Sep",
        "description": "The Amalfi Coast enchants with colorful cliffside villages, azure waters, and authentic Italian dolce vita.",
        "fullDescription": "Wind along one of the world's most scenic coastal roads, discovering charming towns like Positano, Amalfi, and Ravello perched on dramatic cliffs. Savor fresh seafood, homemade limoncello, and the la dolce vita lifestyle on this UNESCO-protected Italian coastline.",
        "highlights": ["Positano village", "Path of the Gods hike", "Ravello gardens", "Amalfi Cathedral", "Boat trips to Capri", "Fresh limoncello tasting"],
        "tags": ["Romantic", "Food", "Beach", "Culture"],
        "priceValue": 2200,
        "rating": 4.8,
        "reviews": 3500,
        "duration": "4-5 days",
        "badge": "Romantic"
    },
    {
        "name": "Queenstown",
        "country": "New Zealand",
        "region": "oceania",
        "coordinates": {"lat": -45.0312, "lng": 168.6626},
        "image": "https://images.unsplash.com/photo-1589871973318-9ca1258faa5d?w=800&q=80",
        "climate": "Temperate",
        "bestTimeToVisit": "Dec - Feb, Jun - Aug",
        "description": "Queenstown is the adventure capital of the world, set against stunning lakeside and mountain scenery.",
        "fullDescription": "Get your adrenaline pumping in Queenstown, birthplace of bungee jumping and home to countless extreme sports. When not jumping, skiing, or jet boating, enjoy world-class wineries, peaceful lake cruises, and some of New Zealand's most spectacular alpine scenery.",
        "highlights": ["Bungee jumping", "Milford Sound day trip", "Skyline Gondola", "Jet boat rides", "Skiing at Remarkables", "Central Otago wineries"],
        "tags": ["Adventure", "Nature", "Photography", "Luxury"],
        "priceValue": 2300,
        "rating": 4.8,
        "reviews": 2900,
        "duration": "4-6 days",
        "badge": "Adventure"
    },
    {
        "name": "Phuket",
        "country": "Thailand",
        "region": "asia",
        "coordinates": {"lat": 7.8804, "lng": 98.3923},
        "image": "https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?w=800&q=80",
        "climate": "Tropical",
        "bestTimeToVisit": "Nov - Apr",
        "description": "Phuket offers tropical paradise with stunning beaches, vibrant nightlife, and affordable Thai hospitality.",
        "fullDescription": "Thailand's largest island delivers the perfect beach holiday with something for everyone. From the bustling Patong Beach to serene hidden coves, explore ancient temples, indulge in Thai massage, feast on incredible street food, and island-hop to nearby paradises.",
        "highlights": ["Phi Phi Islands trip", "Big Buddha", "Patong nightlife", "Thai cooking classes", "Phang Nga Bay", "Traditional Thai massage"],
        "tags": ["Beach", "Relaxation", "Nightlife", "Food"],
        "priceValue": 900,
        "rating": 4.6,
        "reviews": 4500,
        "duration": "5-7 days",
        "badge": "Best Value"
    },
    {
        "name": "Rio de Janeiro",
        "country": "Brazil",
        "region": "americas",
        "coordinates": {"lat": -22.9068, "lng": -43.1729},
        "image": "https://images.unsplash.com/photo-1483729558449-99ef09a8c325?w=800&q=80",
        "climate": "Tropical",
        "bestTimeToVisit": "Dec - Mar",
        "description": "Rio de Janeiro pulses with samba rhythms, iconic beaches, and the outstretched arms of Christ the Redeemer.",
        "fullDescription": "Experience the infectious energy of the Marvelous City, where mountains meet the sea and music fills the streets. Ride the cable car to Sugarloaf, relax on Copacabana and Ipanema beaches, and discover why Rio's blend of natural beauty and vibrant culture is legendary.",
        "highlights": ["Christ the Redeemer", "Sugarloaf Mountain", "Copacabana Beach", "Ipanema sunset", "Tijuca Forest", "Samba shows in Lapa"],
        "tags": ["Beach", "Culture", "Nightlife", "Adventure"],
        "priceValue": 1600,
        "rating": 4.7,
        "reviews": 3300,
        "duration": "5-7 days",
        "badge": "Popular"
    },
    {
        "name": "Prague",
        "country": "Czech Republic",
        "region": "europe",
        "coordinates": {"lat": 50.0755, "lng": 14.4378},
        "image": "https://images.unsplash.com/photo-1541849546-216549ae216d?w=800&q=80",
        "climate": "Continental",
        "bestTimeToVisit": "Apr - May, Sep - Oct",
        "description": "Prague enchants with fairy-tale architecture, rich history, world-famous beer, and magical old-town charm.",
        "fullDescription": "Wander through centuries of history in the City of a Hundred Spires. Cross the iconic Charles Bridge at dawn, explore the world's largest castle complex, and discover cozy pubs serving the world's best beer. Prague offers remarkable value with unforgettable beauty.",
        "highlights": ["Charles Bridge", "Prague Castle", "Old Town Square", "Astronomical Clock", "Czech beer culture", "Jewish Quarter"],
        "tags": ["Historical", "Culture", "Food", "Romantic"],
        "priceValue": 1100,
        "rating": 4.7,
        "reviews": 4200,
        "duration": "3-4 days",
        "badge": "Best Value"
    },
    {
        "name": "Serengeti",
        "country": "Tanzania",
        "region": "africa",
        "coordinates": {"lat": -2.3333, "lng": 34.8333},
        "image": "https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800&q=80",
        "climate": "Savanna",
        "bestTimeToVisit": "Jun - Oct",
        "description": "The Serengeti hosts the world's greatest wildlife spectacle with endless plains teeming with African animals.",
        "fullDescription": "Witness nature's greatest drama unfold on the endless plains of the Serengeti. Experience the Great Migration with millions of wildebeest and zebras, spot the Big Five, and stay in luxury safari camps under star-filled African skies for a truly life-changing adventure.",
        "highlights": ["Great Migration", "Big Five safari", "Balloon safaris", "Luxury tented camps", "Maasai cultural visits", "Ngorongoro Crater"],
        "tags": ["Adventure", "Nature", "Photography", "Luxury"],
        "priceValue": 3200,
        "rating": 4.9,
        "reviews": 1800,
        "duration": "5-7 days",
        "badge": "Adventure"
    },
    {
        "name": "Patagonia",
        "country": "Argentina",
        "region": "americas",
        "coordinates": {"lat": -50.3402, "lng": -72.2648},
        "image": "https://images.unsplash.com/photo-1531761535209-180857e963b9?w=800&q=80",
        "climate": "Subpolar",
        "bestTimeToVisit": "Nov - Mar",
        "description": "Patagonia offers untamed wilderness with towering glaciers, jagged peaks, and pristine natural beauty.",
        "fullDescription": "Journey to the end of the world in Patagonia, where massive glaciers calve into turquoise lakes and granite spires pierce the sky. Trek through Torres del Paine, witness the thundering Perito Moreno Glacier, and experience one of Earth's last great frontiers.",
        "highlights": ["Torres del Paine trek", "Perito Moreno Glacier", "Los Glaciares National Park", "Ushuaia exploration", "Whale watching", "Gaucho estancias"],
        "tags": ["Adventure", "Nature", "Photography", "Relaxation"],
        "priceValue": 2700,
        "rating": 4.8,
        "reviews": 2100,
        "duration": "7-10 days",
        "badge": "Adventure"
    },
    {
        "name": "Ha Long Bay",
        "country": "Vietnam",
        "region": "asia",
        "coordinates": {"lat": 20.9101, "lng": 107.1839},
        "image": "https://images.unsplash.com/photo-1528127269322-539801943592?w=800&q=80",
        "climate": "Tropical",
        "bestTimeToVisit": "Oct - Apr",
        "description": "Ha Long Bay mesmerizes with thousands of limestone karsts rising from emerald waters in mystical formations.",
        "fullDescription": "Cruise through a UNESCO World Heritage seascape where thousands of towering limestone islands create a mystical maze of emerald waters. Kayak through hidden grottoes, visit floating villages, and wake up to sunrise over this legendary Vietnamese wonder.",
        "highlights": ["Overnight junk boat cruise", "Kayaking through caves", "Floating villages", "Ti Top Island viewpoint", "Sung Sot Cave", "Fresh seafood dining"],
        "tags": ["Nature", "Relaxation", "Photography", "Adventure"],
        "priceValue": 800,
        "rating": 4.7,
        "reviews": 3700,
        "duration": "2-3 days",
        "badge": "Best Value"
    },
    {
        "name": "Cinque Terre",
        "country": "Italy",
        "region": "europe",
        "coordinates": {"lat": 44.1461, "lng": 9.6439},
        "image": "https://images.unsplash.com/photo-1516483638261-f4dbaf036963?w=800&q=80",
        "climate": "Mediterranean",
        "bestTimeToVisit": "Apr - Oct",
        "description": "Cinque Terre's five colorful fishing villages cling to dramatic cliffs along Italy's stunning Ligurian coast.",
        "fullDescription": "Discover five enchanting villages connected by ancient footpaths winding through vineyards and olive groves along the Italian Riviera. Swim in crystalline waters, feast on fresh pesto and focaccia, and watch sunset paint the pastel houses in golden light.",
        "highlights": ["Hiking the Blue Trail", "Village hopping by train", "Vernazza harbor", "Fresh pesto tasting", "Swimming in Monterosso", "Sunset in Manarola"],
        "tags": ["Romantic", "Culture", "Nature", "Food"],
        "priceValue": 1700,
        "rating": 4.8,
        "reviews": 3900,
        "duration": "3-4 days",
        "badge": "Romantic"
    },
    {
        "name": "Great Barrier Reef",
        "country": "Australia",
        "region": "oceania",
        "coordinates": {"lat": -18.2871, "lng": 147.6992},
        "image": "https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=800&q=80",
        "climate": "Tropical",
        "bestTimeToVisit": "Jun - Oct",
        "description": "The Great Barrier Reef is Earth's largest living structure, a kaleidoscope of coral and marine life.",
        "fullDescription": "Dive into the world's most spectacular underwater wonderland stretching over 2,300 kilometers. Snorkel among 1,500 species of tropical fish, spot sea turtles and reef sharks, and experience one of the planet's most biodiverse ecosystems from the water or scenic flights above.",
        "highlights": ["Scuba diving adventures", "Snorkeling tours", "Scenic helicopter flights", "Whitsunday Islands", "Glass-bottom boat tours", "Sea turtle encounters"],
        "tags": ["Adventure", "Nature", "Beach", "Photography"],
        "priceValue": 2000,
        "rating": 4.8,
        "reviews": 3100,
        "duration": "3-5 days",
        "badge": "Nature"
    },
]


@router.get("/random", response_model=DestinationsResponse)
def get_random_destinations(count: int = 9):
    """Get a random selection of destinations instantly."""
    
    # Randomly select destinations from the pool
    selected = random.sample(DESTINATION_POOL, min(count, len(DESTINATION_POOL)))
    
    # Add unique IDs
    destinations = []
    for i, dest in enumerate(selected):
        dest_with_id = {**dest, "id": i + 1, "price": f"${dest['priceValue']:,}"}
        destinations.append(dest_with_id)
    
    return DestinationsResponse(destinations=destinations, generated=False)


@router.get("/all")
def get_all_destinations():
    """Get all available destinations."""
    destinations = []
    for i, dest in enumerate(DESTINATION_POOL):
        dest_with_id = {**dest, "id": i + 1, "price": f"${dest['priceValue']:,}"}
        destinations.append(dest_with_id)
    
    return {"destinations": destinations, "total": len(destinations)}

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional

import httpx

from app.core.config import settings


@dataclass(frozen=True)
class IndiaCity:
    city: str
    state: str
    popularity: int
    image: str


INDIA_CITY_DATASET: List[IndiaCity] = [
    IndiaCity("Taj Mahal", "Uttar Pradesh", 100, "https://source.unsplash.com/1200x800/?taj%20mahal,india"),
    IndiaCity("Jaipur", "Rajasthan", 99, "https://source.unsplash.com/1200x800/?jaipur,india"),
    IndiaCity("Varanasi Ghats", "Uttar Pradesh", 98, "https://source.unsplash.com/1200x800/?varanasi,ghats,india"),
    IndiaCity("Goa Beaches", "Goa", 98, "https://source.unsplash.com/1200x800/?goa,beach,india"),
    IndiaCity("Kerala Backwaters", "Kerala", 97, "https://source.unsplash.com/1200x800/?kerala,backwaters,india"),
    IndiaCity("Mysore Palace", "Karnataka", 96, "https://source.unsplash.com/1200x800/?mysore,palace,india"),
    IndiaCity("Hampi", "Karnataka", 96, "https://source.unsplash.com/1200x800/?hampi,india"),
    IndiaCity("Udaipur", "Rajasthan", 95, "https://source.unsplash.com/1200x800/?udaipur,india"),
    IndiaCity("Rishikesh", "Uttarakhand", 95, "https://source.unsplash.com/1200x800/?rishikesh,india"),
    IndiaCity("Amritsar", "Punjab", 95, "https://source.unsplash.com/1200x800/?golden%20temple,amritsar"),
    IndiaCity("Leh", "Ladakh", 94, "https://source.unsplash.com/1200x800/?leh,ladakh,india"),
    IndiaCity("Manali", "Himachal Pradesh", 94, "https://source.unsplash.com/1200x800/?manali,india"),
    IndiaCity("Shimla", "Himachal Pradesh", 93, "https://source.unsplash.com/1200x800/?shimla,india"),
    IndiaCity("Darjeeling", "West Bengal", 93, "https://source.unsplash.com/1200x800/?darjeeling,india"),
    IndiaCity("Sikkim", "Sikkim", 92, "https://source.unsplash.com/1200x800/?sikkim,india"),
    IndiaCity("Andaman Islands", "Andaman and Nicobar", 92, "https://source.unsplash.com/1200x800/?andaman,islands,india"),
    IndiaCity("Lakshadweep", "Lakshadweep", 91, "https://source.unsplash.com/1200x800/?lakshadweep,india"),
    IndiaCity("Kashmir", "Jammu and Kashmir", 91, "https://source.unsplash.com/1200x800/?kashmir,india"),
    IndiaCity("Spiti Valley", "Himachal Pradesh", 90, "https://source.unsplash.com/1200x800/?spiti,valley,india"),
    IndiaCity("Ooty", "Tamil Nadu", 90, "https://source.unsplash.com/1200x800/?ooty,india"),
    IndiaCity("Kodaikanal", "Tamil Nadu", 89, "https://source.unsplash.com/1200x800/?kodaikanal,india"),
    IndiaCity("Coorg", "Karnataka", 89, "https://source.unsplash.com/1200x800/?coorg,india"),
    IndiaCity("Munnar", "Kerala", 89, "https://source.unsplash.com/1200x800/?munnar,india"),
    IndiaCity("Alleppey", "Kerala", 88, "https://source.unsplash.com/1200x800/?alleppey,india"),
    IndiaCity("Kochi", "Kerala", 88, "https://source.unsplash.com/1200x800/?kochi,india"),
    IndiaCity("Pondicherry", "Puducherry", 88, "https://source.unsplash.com/1200x800/?pondicherry,india"),
    IndiaCity("Mahabalipuram", "Tamil Nadu", 87, "https://source.unsplash.com/1200x800/?mahabalipuram,india"),
    IndiaCity("Havelock Island", "Andaman and Nicobar", 87, "https://source.unsplash.com/1200x800/?havelock,island,india"),
    IndiaCity("Konark Sun Temple", "Odisha", 87, "https://source.unsplash.com/1200x800/?konark,temple,india"),
    IndiaCity("Puri", "Odisha", 86, "https://source.unsplash.com/1200x800/?puri,odisha,india"),
    IndiaCity("Khajuraho", "Madhya Pradesh", 86, "https://source.unsplash.com/1200x800/?khajuraho,india"),
    IndiaCity("Sanchi", "Madhya Pradesh", 85, "https://source.unsplash.com/1200x800/?sanchi,stupa,india"),
    IndiaCity("Bhopal", "Madhya Pradesh", 84, "https://source.unsplash.com/1200x800/?bhopal,india"),
    IndiaCity("Mumbai", "Maharashtra", 84, "https://source.unsplash.com/1200x800/?mumbai,india"),
    IndiaCity("Delhi", "Delhi", 84, "https://source.unsplash.com/1200x800/?delhi,india"),
    IndiaCity("Bengaluru", "Karnataka", 83, "https://source.unsplash.com/1200x800/?bangalore,india"),
    IndiaCity("Hyderabad", "Telangana", 83, "https://source.unsplash.com/1200x800/?hyderabad,india"),
    IndiaCity("Chennai", "Tamil Nadu", 82, "https://source.unsplash.com/1200x800/?chennai,india"),
    IndiaCity("Kolkata", "West Bengal", 82, "https://source.unsplash.com/1200x800/?kolkata,india"),
    IndiaCity("Pune", "Maharashtra", 81, "https://source.unsplash.com/1200x800/?pune,india"),
    IndiaCity("Ahmedabad", "Gujarat", 81, "https://source.unsplash.com/1200x800/?ahmedabad,india"),
    IndiaCity("Gir National Park", "Gujarat", 80, "https://source.unsplash.com/1200x800/?gir,forest,india"),
    IndiaCity("Rann of Kutch", "Gujarat", 80, "https://source.unsplash.com/1200x800/?rann%20of%20kutch,india"),
    IndiaCity("Dwarka", "Gujarat", 79, "https://source.unsplash.com/1200x800/?dwarka,temple,india"),
    IndiaCity("Somnath", "Gujarat", 79, "https://source.unsplash.com/1200x800/?somnath,temple,india"),
    IndiaCity("Jaisalmer", "Rajasthan", 79, "https://source.unsplash.com/1200x800/?jaisalmer,india"),
    IndiaCity("Jodhpur", "Rajasthan", 78, "https://source.unsplash.com/1200x800/?jodhpur,india"),
    IndiaCity("Bikaner", "Rajasthan", 77, "https://source.unsplash.com/1200x800/?bikaner,india"),
    IndiaCity("Pushkar", "Rajasthan", 77, "https://source.unsplash.com/1200x800/?pushkar,india"),
    IndiaCity("Ranthambore", "Rajasthan", 77, "https://source.unsplash.com/1200x800/?ranthambore,india"),
    IndiaCity("Ajanta Caves", "Maharashtra", 76, "https://source.unsplash.com/1200x800/?ajanta,caves,india"),
    IndiaCity("Ellora Caves", "Maharashtra", 76, "https://source.unsplash.com/1200x800/?ellora,caves,india"),
    IndiaCity("Nashik", "Maharashtra", 75, "https://source.unsplash.com/1200x800/?nashik,india"),
    IndiaCity("Shirdi", "Maharashtra", 75, "https://source.unsplash.com/1200x800/?shirdi,india"),
    IndiaCity("Lonavala", "Maharashtra", 74, "https://source.unsplash.com/1200x800/?lonavala,india"),
    IndiaCity("Mahabaleshwar", "Maharashtra", 74, "https://source.unsplash.com/1200x800/?mahabaleshwar,india"),
    IndiaCity("Sundarbans", "West Bengal", 73, "https://source.unsplash.com/1200x800/?sundarbans,india"),
    IndiaCity("Gangtok", "Sikkim", 73, "https://source.unsplash.com/1200x800/?gangtok,india"),
    IndiaCity("Nainital", "Uttarakhand", 72, "https://source.unsplash.com/1200x800/?nainital,india"),
    IndiaCity("Mussoorie", "Uttarakhand", 72, "https://source.unsplash.com/1200x800/?mussoorie,india"),
    IndiaCity("Ranikhet", "Uttarakhand", 71, "https://source.unsplash.com/1200x800/?ranikhet,india"),
    IndiaCity("Haridwar", "Uttarakhand", 71, "https://source.unsplash.com/1200x800/?haridwar,india"),
    IndiaCity("Ayodhya", "Uttar Pradesh", 70, "https://source.unsplash.com/1200x800/?ayodhya,india"),
    IndiaCity("Lucknow", "Uttar Pradesh", 70, "https://source.unsplash.com/1200x800/?lucknow,india"),
    IndiaCity("Agra", "Uttar Pradesh", 70, "https://source.unsplash.com/1200x800/?agra,india"),
    IndiaCity("Mathura", "Uttar Pradesh", 69, "https://source.unsplash.com/1200x800/?mathura,india"),
    IndiaCity("Vrindavan", "Uttar Pradesh", 69, "https://source.unsplash.com/1200x800/?vrindavan,india"),
    IndiaCity("Bodh Gaya", "Bihar", 68, "https://source.unsplash.com/1200x800/?bodh%20gaya,india"),
    IndiaCity("Nalanda", "Bihar", 67, "https://source.unsplash.com/1200x800/?nalanda,india"),
    IndiaCity("Patna", "Bihar", 66, "https://source.unsplash.com/1200x800/?patna,india"),
    IndiaCity("Shillong", "Meghalaya", 66, "https://source.unsplash.com/1200x800/?shillong,india"),
    IndiaCity("Cherrapunji", "Meghalaya", 65, "https://source.unsplash.com/1200x800/?cherrapunji,india"),
    IndiaCity("Dawki", "Meghalaya", 64, "https://source.unsplash.com/1200x800/?dawki,meghalaya,india"),
    IndiaCity("Kaziranga", "Assam", 64, "https://source.unsplash.com/1200x800/?kaziranga,india"),
    IndiaCity("Majuli", "Assam", 63, "https://source.unsplash.com/1200x800/?majuli,assam,india"),
    IndiaCity("Tawang", "Arunachal Pradesh", 62, "https://source.unsplash.com/1200x800/?tawang,india"),
    IndiaCity("Ziro", "Arunachal Pradesh", 61, "https://source.unsplash.com/1200x800/?ziro,valley,india"),
    IndiaCity("Imphal", "Manipur", 60, "https://source.unsplash.com/1200x800/?imphal,india"),
    IndiaCity("Aizawl", "Mizoram", 59, "https://source.unsplash.com/1200x800/?aizawl,india"),
    IndiaCity("Kohima", "Nagaland", 58, "https://source.unsplash.com/1200x800/?kohima,india"),
    IndiaCity("Agartala", "Tripura", 57, "https://source.unsplash.com/1200x800/?agartala,india"),
    IndiaCity("Bhubaneswar", "Odisha", 57, "https://source.unsplash.com/1200x800/?bhubaneswar,india"),
    IndiaCity("Gokarna", "Karnataka", 57, "https://source.unsplash.com/1200x800/?gokarna,india"),
    IndiaCity("Dandeli", "Karnataka", 56, "https://source.unsplash.com/1200x800/?dandeli,india"),
    IndiaCity("Madurai", "Tamil Nadu", 56, "https://source.unsplash.com/1200x800/?madurai,india"),
    IndiaCity("Rameswaram", "Tamil Nadu", 56, "https://source.unsplash.com/1200x800/?rameswaram,india"),
    IndiaCity("Kanyakumari", "Tamil Nadu", 55, "https://source.unsplash.com/1200x800/?kanyakumari,india"),
    IndiaCity("Visakhapatnam", "Andhra Pradesh", 55, "https://source.unsplash.com/1200x800/?vizag,india"),
    IndiaCity("Araku Valley", "Andhra Pradesh", 54, "https://source.unsplash.com/1200x800/?araku,valley,india"),
    IndiaCity("Warangal", "Telangana", 53, "https://source.unsplash.com/1200x800/?warangal,india"),
    IndiaCity("Charminar", "Telangana", 53, "https://source.unsplash.com/1200x800/?charminar,hyderabad,india"),
]


def _fallback_image(place: str, state: Optional[str] = None) -> str:
    terms = [place, "india"]
    if state:
        terms.insert(1, state)
    query = ",".join([term for term in terms if term]).replace(" ", "%20")
    return f"https://source.unsplash.com/1200x800/?{query}"


def _to_location_payload(city: IndiaCity) -> Dict:
    return {
        "city": city.city,
        "state": city.state,
        "country": "India",
        "popularity": city.popularity,
        "image": city.image or _fallback_image(city.city, city.state),
    }


def get_popular_india_locations(limit: int = 6) -> List[Dict]:
    ranked = sorted(INDIA_CITY_DATASET, key=lambda item: item.popularity, reverse=True)
    return [_to_location_payload(item) for item in ranked[:max(1, limit)]]


def _local_search(query: str, limit: int = 10) -> List[Dict]:
    q = query.lower().strip()
    if not q:
        return []

    matched = [
        city
        for city in INDIA_CITY_DATASET
        if q in city.city.lower() or q in city.state.lower()
    ]
    ranked = sorted(matched, key=lambda item: item.popularity, reverse=True)
    return [_to_location_payload(item) for item in ranked[:max(1, limit)]]


async def search_india_locations(query: str, limit: int = 10) -> List[Dict]:
    q = query.strip()
    if not q:
        return []

    geodb_key = (settings.GEODB_API_KEY or "").strip()
    geodb_host = (settings.GEODB_HOST or "wft-geo-db.p.rapidapi.com").strip()

    if not geodb_key:
        return _local_search(q, limit)

    url = f"https://{geodb_host}/v1/geo/cities"
    headers = {
        "X-RapidAPI-Key": geodb_key,
        "X-RapidAPI-Host": geodb_host,
    }
    params = {
        "namePrefix": q,
        "countryIds": "IN",
        "sort": "-population",
        "limit": max(1, min(limit, 10)),
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            payload = response.json()

        results = []
        for item in payload.get("data", []):
            city = item.get("city")
            state = item.get("region") or "Unknown"
            country_code = item.get("countryCode")
            if not city or country_code != "IN":
                continue
            results.append(
                {
                    "city": city,
                    "state": state,
                    "country": "India",
                    "popularity": int(item.get("population") or 0),
                    "image": _fallback_image(city, state),
                }
            )

        if results:
            return results
        local_results = _local_search(q, limit)
        if local_results:
            return local_results

        return [
            {
                "city": q.title(),
                "state": "India",
                "country": "India",
                "popularity": 50,
                "image": _fallback_image(q, "India"),
            }
        ]
    except Exception:
        local_results = _local_search(q, limit)
        if local_results:
            return local_results

        return [
            {
                "city": q.title(),
                "state": "India",
                "country": "India",
                "popularity": 50,
                "image": _fallback_image(q, "India"),
            }
        ]

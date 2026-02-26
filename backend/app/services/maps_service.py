"""
Google Maps service utilities for attractions and travel-time matrices.

Production notes:
- Requires GOOGLE_MAPS_API_KEY in environment.
- Uses async httpx with explicit timeout.
- Returns structured, frontend-compatible dictionaries.
- Fails safely (empty results or haversine fallback) on external API errors.
"""

import logging
import math
import os
import asyncio
from typing import Any, Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger(__name__)

GOOGLE_PLACES_NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
GOOGLE_DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"
GOOGLE_MAPS_TIMEOUT_SECONDS = 12.0


LocationPoint = Tuple[float, float]


def _haversine_distance_km(origin: LocationPoint, destination: LocationPoint) -> float:
    """Compute great-circle distance for fallback routing when API is unavailable."""
    lat1, lon1 = origin
    lat2, lon2 = destination

    radius_earth_km = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_earth_km * c


def _maps_api_key() -> Optional[str]:
    return os.getenv("GOOGLE_MAPS_API_KEY")


async def get_nearby_attractions(
    location_name: str,
    lat: float,
    lon: float,
    radius_km: float,
    travel_type: str,
) -> List[Dict[str, Any]]:
    """
    Fetch nearby attractions using Google Places Nearby Search API.

    Returns list shape:
    [
      {
        "name": str,
        "rating": float,
        "latitude": float,
        "longitude": float,
        "price_level": int,
        "user_ratings_total": int,
        "place_type": "attraction"
      }
    ]
    """
    api_key = _maps_api_key()
    if not api_key:
        logger.warning("[MapsService] GOOGLE_MAPS_API_KEY not set; returning no nearby attractions")
        return []

    radius_meters = int(max(radius_km, 1.0) * 1000)
    params = {
        "location": f"{lat},{lon}",
        "radius": radius_meters,
        "type": "tourist_attraction",
        "keyword": travel_type,
        "key": api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=GOOGLE_MAPS_TIMEOUT_SECONDS) as client:
            response = await client.get(GOOGLE_PLACES_NEARBY_URL, params=params)
            response.raise_for_status()
            payload = response.json()

        status = payload.get("status")
        if status not in {"OK", "ZERO_RESULTS"}:
            logger.warning(
                "[MapsService] Nearby Search failed for %s (status=%s)",
                location_name,
                status,
            )
            return []

        attractions: List[Dict[str, Any]] = []
        for place in payload.get("results", []):
            geometry = place.get("geometry", {}).get("location", {})
            latitude = geometry.get("lat")
            longitude = geometry.get("lng")
            if latitude is None or longitude is None:
                continue

            attractions.append(
                {
                    "name": place.get("name", "Unknown Attraction"),
                    "rating": float(place.get("rating", 0.0) or 0.0),
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                    "price_level": int(place.get("price_level", 2) or 2),
                    "user_ratings_total": int(place.get("user_ratings_total", 0) or 0),
                    "place_type": "attraction",
                }
            )

        return attractions
    except Exception as exc:
        logger.warning("[MapsService] Nearby attractions request failed: %s", exc)
        return []


async def get_distance_matrix(
    origin: LocationPoint,
    destinations: List[LocationPoint],
) -> List[Dict[str, float]]:
    """
    Get travel distance/time from one origin to many destinations.

    Returns one dictionary per destination:
    [{"distance_km": float, "duration_minutes": float}, ...]
    """
    if not destinations:
        return []

    api_key = _maps_api_key()
    if not api_key:
        return [
            {
                "distance_km": round(_haversine_distance_km(origin, destination), 2),
                "duration_minutes": round(_haversine_distance_km(origin, destination) / 30 * 60, 2),
            }
            for destination in destinations
        ]

    params = {
        "origins": f"{origin[0]},{origin[1]}",
        "destinations": "|".join(f"{lat},{lon}" for lat, lon in destinations),
        "mode": "driving",
        "units": "metric",
        "key": api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=GOOGLE_MAPS_TIMEOUT_SECONDS) as client:
            response = await client.get(GOOGLE_DISTANCE_MATRIX_URL, params=params)
            response.raise_for_status()
            payload = response.json()

        status = payload.get("status")
        if status != "OK":
            logger.warning("[MapsService] Distance Matrix status=%s", status)
            raise ValueError(f"Distance Matrix status not OK: {status}")

        row = payload.get("rows", [{}])[0]
        elements = row.get("elements", [])

        results: List[Dict[str, float]] = []
        for idx, element in enumerate(elements):
            if element.get("status") == "OK":
                distance_km = (element.get("distance", {}).get("value", 0) or 0) / 1000
                duration_minutes = (element.get("duration", {}).get("value", 0) or 0) / 60
            else:
                distance_km = _haversine_distance_km(origin, destinations[idx])
                duration_minutes = (distance_km / 30) * 60

            results.append(
                {
                    "distance_km": round(distance_km, 2),
                    "duration_minutes": round(duration_minutes, 2),
                }
            )

        return results
    except Exception as exc:
        logger.warning("[MapsService] Distance Matrix request failed: %s", exc)
        return [
            {
                "distance_km": round(_haversine_distance_km(origin, destination), 2),
                "duration_minutes": round(_haversine_distance_km(origin, destination) / 30 * 60, 2),
            }
            for destination in destinations
        ]


async def get_travel_metrics_matrix(
    points: List[LocationPoint],
) -> Tuple[List[List[float]], List[List[float]]]:
    """
    Build full NxN distance and duration matrices.

    Returns:
    - distance_matrix_km[i][j]
    - duration_matrix_minutes[i][j]

    Uses Distance Matrix API row-by-row and falls back safely.
    """
    size = len(points)
    if size == 0:
        return [], []

    distance_matrix = [[0.0 for _ in range(size)] for _ in range(size)]
    duration_matrix = [[0.0 for _ in range(size)] for _ in range(size)]

    tasks = [
        get_distance_matrix(points[i], [points[j] for j in range(size)])
        for i in range(size)
    ]
    rows = await asyncio.gather(*tasks)

    for i in range(size):
        for j in range(size):
            metrics = rows[i][j]
            distance_matrix[i][j] = float(metrics.get("distance_km", 0.0))
            duration_matrix[i][j] = float(metrics.get("duration_minutes", 0.0))

    return distance_matrix, duration_matrix

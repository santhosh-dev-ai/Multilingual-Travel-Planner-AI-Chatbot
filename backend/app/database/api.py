"""
Database routes for wishlist & itinerary
USED AS A ROUTER (not a standalone server)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from dotenv import load_dotenv

from app.database.models import WishlistItemCreate, ItineraryCreate
from app.database.crud import WishlistCRUD, ItineraryCRUD

load_dotenv()

# ✅ ROUTER (NOT FastAPI)
router = APIRouter(prefix="/api", tags=["database"])


# ================== Health ==================

@router.get("/database/health")
def health_check():
    return {
        "status": "healthy",
        "database": "supabase"
    }


# ================== Wishlist ==================

@router.get("/wishlist/{user_id}")
def get_user_wishlist(user_id: str):
    result = WishlistCRUD.get_by_user(user_id)
    # Return empty wishlist gracefully on configuration or transient database issues
    if not result.get("success"):
        message = str(result.get("message", ""))
        if "not configured" in message.lower():
            return {"success": True, "message": "Database not configured, returning empty wishlist", "data": []}
        return {"success": True, "message": "Wishlist temporarily unavailable, returning empty list", "data": []}
    return result


@router.post("/wishlist")
def add_to_wishlist(item: WishlistItemCreate):
    result = WishlistCRUD.create(item)
    # Return graceful message if database not configured
    if not result["success"] and "not configured" in result["message"].lower():
        return {"success": False, "message": "Database not configured. Wishlist feature unavailable.", "data": None}
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@router.get("/wishlist/{user_id}/check/{destination_id}")
def check_wishlist(user_id: str, destination_id: int):
    result = WishlistCRUD.check_exists(user_id, destination_id)
    # Return false gracefully if database not configured
    if not result.get("success") and "not configured" in result.get("message", "").lower():
        return {"success": True, "data": {"exists": False}, "message": "Database not configured"}
    return result


@router.delete("/wishlist/{user_id}/destination/{destination_id}")
def remove_destination_from_wishlist(user_id: str, destination_id: int):
    result = WishlistCRUD.delete_by_destination(user_id, destination_id)
    # Return graceful message if database not configured
    if not result["success"] and "not configured" in result["message"].lower():
        return {"success": False, "message": "Database not configured. Wishlist feature unavailable.", "data": None}
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@router.delete("/wishlist/{user_id}/clear")
def clear_wishlist(user_id: str):
    result = WishlistCRUD.clear_user_wishlist(user_id)
    # Return graceful message if database not configured
    if not result.get("success") and "not configured" in result.get("message", "").lower():
        return {"success": False, "message": "Database not configured", "data": None}
    return result


# ================== Itinerary ==================

@router.get("/itinerary/{user_id}")
def get_user_itineraries(user_id: str, limit: int = Query(50)):
    result = ItineraryCRUD.get_by_user(user_id, limit)
    # Return empty list gracefully on configuration or transient database issues
    if not result.get("success"):
        message = str(result.get("message", ""))
        if "not configured" in message.lower():
            return {"success": True, "message": "Database not configured, returning empty itineraries", "data": []}
        return {"success": True, "message": "Itineraries temporarily unavailable, returning empty list", "data": []}
    return result


@router.post("/itinerary")
def save_itinerary(itinerary: ItineraryCreate):
    result = ItineraryCRUD.create(itinerary)
    # Return graceful message if database not configured
    if not result.get("success") and "not configured" in result.get("message", "").lower():
        return {"success": False, "message": "Database not configured. Itinerary saving unavailable.", "data": None}
    return result


@router.get("/itinerary/{user_id}/count")
def count_itineraries(user_id: str):
    result = ItineraryCRUD.count_by_user(user_id)
    # Return 0 gracefully on configuration or transient database issues
    if not result.get("success"):
        message = str(result.get("message", ""))
        if "not configured" in message.lower():
            return {"success": True, "message": "Database not configured", "data": {"count": 0}, "count": 0}
        return {"success": True, "message": "Itinerary count temporarily unavailable", "data": {"count": 0}, "count": 0}

    count = 0
    if isinstance(result.get("data"), dict):
        count = result["data"].get("count") or 0

    # Keep response backward compatible for frontend expecting response.count
    return {**result, "count": count}


@router.get("/itinerary/detail/{itinerary_id}")
def get_itinerary(itinerary_id: str):
    return ItineraryCRUD.get_by_id(itinerary_id)


@router.delete("/itinerary/{itinerary_id}")
def delete_itinerary(itinerary_id: str):
    return ItineraryCRUD.delete(itinerary_id)

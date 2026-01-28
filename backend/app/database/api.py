"""
Database routes for wishlist & itinerary
USED AS A ROUTER (not a standalone server)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from dotenv import load_dotenv

from database.models import WishlistItemCreate, ItineraryCreate
from database.crud import WishlistCRUD, ItineraryCRUD

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
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@router.post("/wishlist")
def add_to_wishlist(item: WishlistItemCreate):
    result = WishlistCRUD.create(item)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@router.get("/wishlist/{user_id}/check/{destination_id}")
def check_wishlist(user_id: str, destination_id: int):
    return WishlistCRUD.check_exists(user_id, destination_id)


@router.delete("/wishlist/{user_id}/destination/{destination_id}")
def remove_destination_from_wishlist(user_id: str, destination_id: int):
    result = WishlistCRUD.delete_by_destination(user_id, destination_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@router.delete("/wishlist/{user_id}/clear")
def clear_wishlist(user_id: str):
    return WishlistCRUD.clear_user_wishlist(user_id)


# ================== Itinerary ==================

@router.get("/itinerary/{user_id}")
def get_user_itineraries(user_id: str, limit: int = Query(50)):
    return ItineraryCRUD.get_by_user(user_id, limit)


@router.post("/itinerary")
def save_itinerary(itinerary: ItineraryCreate):
    return ItineraryCRUD.create(itinerary)


@router.get("/itinerary/{user_id}/count")
def count_itineraries(user_id: str):
    return ItineraryCRUD.count_by_user(user_id)


@router.get("/itinerary/detail/{itinerary_id}")
def get_itinerary(itinerary_id: str):
    return ItineraryCRUD.get_by_id(itinerary_id)


@router.delete("/itinerary/{itinerary_id}")
def delete_itinerary(itinerary_id: str):
    return ItineraryCRUD.delete(itinerary_id)

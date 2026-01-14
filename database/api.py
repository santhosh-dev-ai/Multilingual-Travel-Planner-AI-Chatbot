"""FastAPI server for database operations."""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
from dotenv import load_dotenv

from models import WishlistItemCreate, ItineraryCreate
from crud import WishlistCRUD, ItineraryCRUD

load_dotenv()

app = FastAPI(
    title="TravelGenie Database API",
    description="Database CRUD operations for wishlists and itineraries",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Health Check ==============

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "TravelGenie Database API"}


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "supabase",
        "endpoints": {
            "wishlist": "/api/wishlist",
            "itinerary": "/api/itinerary"
        }
    }


# ============== Wishlist Endpoints ==============

@app.get("/api/wishlist/{user_id}")
async def get_user_wishlist(user_id: str):
    """Get all wishlist items for a user."""
    result = WishlistCRUD.get_by_user(user_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@app.post("/api/wishlist")
async def add_to_wishlist(item: WishlistItemCreate):
    """Add a destination to wishlist."""
    result = WishlistCRUD.create(item)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@app.post("/api/wishlist/toggle")
async def toggle_wishlist(
    user_id: str = Query(..., description="User ID"),
    destination_id: int = Query(..., description="Destination ID"),
    destination_name: str = Query(..., description="Destination name"),
    destination_country: str = Query(..., description="Country"),
    destination_image: Optional[str] = Query(None, description="Image URL"),
    destination_price: Optional[str] = Query(None, description="Price"),
    destination_rating: Optional[float] = Query(None, description="Rating")
):
    """Toggle a destination in wishlist (add/remove)."""
    destination_data = {
        "destination_id": destination_id,
        "destination_name": destination_name,
        "destination_country": destination_country,
        "destination_image": destination_image,
        "destination_price": destination_price,
        "destination_rating": destination_rating
    }
    result = WishlistCRUD.toggle(user_id, destination_data)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@app.get("/api/wishlist/{user_id}/check/{destination_id}")
async def check_wishlist(user_id: str, destination_id: int):
    """Check if a destination is in user's wishlist."""
    result = WishlistCRUD.check_exists(user_id, destination_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@app.delete("/api/wishlist/{wishlist_id}")
async def remove_from_wishlist(wishlist_id: str):
    """Remove an item from wishlist by ID."""
    result = WishlistCRUD.delete(wishlist_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@app.delete("/api/wishlist/{user_id}/destination/{destination_id}")
async def remove_destination_from_wishlist(user_id: str, destination_id: int):
    """Remove a destination from user's wishlist."""
    result = WishlistCRUD.delete_by_destination(user_id, destination_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@app.delete("/api/wishlist/{user_id}/clear")
async def clear_wishlist(user_id: str):
    """Clear all items from user's wishlist."""
    result = WishlistCRUD.clear_user_wishlist(user_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


# ============== Itinerary Endpoints ==============

@app.get("/api/itinerary/{user_id}")
async def get_user_itineraries(user_id: str, limit: int = Query(50, ge=1, le=100)):
    """Get all itineraries for a user."""
    result = ItineraryCRUD.get_by_user(user_id, limit)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@app.get("/api/itinerary/detail/{itinerary_id}")
async def get_itinerary(itinerary_id: str):
    """Get a specific itinerary by ID."""
    result = ItineraryCRUD.get_by_id(itinerary_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@app.get("/api/itinerary/{user_id}/destination/{destination}")
async def get_itineraries_by_destination(user_id: str, destination: str):
    """Get itineraries for a specific destination."""
    result = ItineraryCRUD.get_by_destination(user_id, destination)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@app.post("/api/itinerary")
async def save_itinerary(itinerary: ItineraryCreate):
    """Save a new itinerary."""
    result = ItineraryCRUD.create(itinerary)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@app.put("/api/itinerary/{itinerary_id}")
async def update_itinerary(itinerary_id: str, update_data: dict):
    """Update an existing itinerary."""
    result = ItineraryCRUD.update(itinerary_id, update_data)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@app.delete("/api/itinerary/{itinerary_id}")
async def delete_itinerary(itinerary_id: str):
    """Delete an itinerary by ID."""
    result = ItineraryCRUD.delete(itinerary_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@app.delete("/api/itinerary/{user_id}/all")
async def delete_all_itineraries(user_id: str):
    """Delete all itineraries for a user."""
    result = ItineraryCRUD.delete_by_user(user_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@app.get("/api/itinerary/{user_id}/count")
async def count_itineraries(user_id: str):
    """Get count of itineraries for a user."""
    result = ItineraryCRUD.count_by_user(user_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("DATABASE_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

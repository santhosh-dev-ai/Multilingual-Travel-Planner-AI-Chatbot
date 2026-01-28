"""CRUD operations for Wishlist."""
from typing import List, Optional
from config import supabase
from models import WishlistItemCreate, WishlistItem


class WishlistCRUD:
    """CRUD operations for wishlist items."""
    
    TABLE_NAME = "wishlists"
    
    @staticmethod
    def create(item: WishlistItemCreate) -> dict:
        """Add a destination to user's wishlist."""
        try:
            data = item.model_dump()
            response = supabase.table(WishlistCRUD.TABLE_NAME).insert(data).execute()
            
            if response.data:
                return {"success": True, "message": "Added to wishlist", "data": response.data[0]}
            return {"success": False, "message": "Failed to add to wishlist", "data": None}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def get_by_user(user_id: str) -> dict:
        """Get all wishlist items for a user."""
        try:
            response = supabase.table(WishlistCRUD.TABLE_NAME)\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .execute()
            
            return {"success": True, "message": "Wishlist retrieved", "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def get_by_id(wishlist_id: str) -> dict:
        """Get a specific wishlist item by ID."""
        try:
            response = supabase.table(WishlistCRUD.TABLE_NAME)\
                .select("*")\
                .eq("id", wishlist_id)\
                .single()\
                .execute()
            
            return {"success": True, "message": "Item retrieved", "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def check_exists(user_id: str, destination_id: int) -> dict:
        """Check if a destination is already in user's wishlist."""
        try:
            response = supabase.table(WishlistCRUD.TABLE_NAME)\
                .select("id")\
                .eq("user_id", user_id)\
                .eq("destination_id", destination_id)\
                .execute()
            
            exists = len(response.data) > 0
            return {
                "success": True, 
                "message": "Check completed", 
                "data": {"exists": exists, "item": response.data[0] if exists else None}
            }
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def delete(wishlist_id: str) -> dict:
        """Remove an item from wishlist by ID."""
        try:
            response = supabase.table(WishlistCRUD.TABLE_NAME)\
                .delete()\
                .eq("id", wishlist_id)\
                .execute()
            
            return {"success": True, "message": "Removed from wishlist", "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def delete_by_destination(user_id: str, destination_id: int) -> dict:
        """Remove a destination from user's wishlist."""
        try:
            response = supabase.table(WishlistCRUD.TABLE_NAME)\
                .delete()\
                .eq("user_id", user_id)\
                .eq("destination_id", destination_id)\
                .execute()
            
            return {"success": True, "message": "Removed from wishlist", "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def clear_user_wishlist(user_id: str) -> dict:
        """Clear all wishlist items for a user."""
        try:
            response = supabase.table(WishlistCRUD.TABLE_NAME)\
                .delete()\
                .eq("user_id", user_id)\
                .execute()
            
            return {"success": True, "message": "Wishlist cleared", "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def toggle(user_id: str, destination_data: dict) -> dict:
        """Toggle a destination in wishlist (add if not exists, remove if exists)."""
        try:
            # Check if already exists
            check = WishlistCRUD.check_exists(user_id, destination_data.get("destination_id"))
            
            if check["success"] and check["data"]["exists"]:
                # Remove from wishlist
                return WishlistCRUD.delete(check["data"]["item"]["id"])
            else:
                # Add to wishlist
                item = WishlistItemCreate(
                    user_id=user_id,
                    destination_id=destination_data.get("destination_id"),
                    destination_name=destination_data.get("destination_name"),
                    destination_country=destination_data.get("destination_country"),
                    destination_image=destination_data.get("destination_image"),
                    destination_price=destination_data.get("destination_price"),
                    destination_rating=destination_data.get("destination_rating")
                )
                return WishlistCRUD.create(item)
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}

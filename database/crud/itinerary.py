"""CRUD operations for Itineraries."""
from typing import List, Optional
from datetime import datetime
from config import supabase
from models import ItineraryCreate, Itinerary


class ItineraryCRUD:
    """CRUD operations for itineraries."""
    
    TABLE_NAME = "itineraries"
    
    @staticmethod
    def create(itinerary: ItineraryCreate) -> dict:
        """Create a new itinerary."""
        try:
            data = itinerary.model_dump()
            # Convert days to JSON-serializable format
            data["days"] = [day.model_dump() if hasattr(day, 'model_dump') else day for day in data["days"]]
            
            response = supabase.table(ItineraryCRUD.TABLE_NAME).insert(data).execute()
            
            if response.data:
                return {"success": True, "message": "Itinerary saved", "data": response.data[0]}
            return {"success": False, "message": "Failed to save itinerary", "data": None}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def get_by_user(user_id: str, limit: int = 50) -> dict:
        """Get all itineraries for a user."""
        try:
            response = supabase.table(ItineraryCRUD.TABLE_NAME)\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return {"success": True, "message": "Itineraries retrieved", "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def get_by_id(itinerary_id: str) -> dict:
        """Get a specific itinerary by ID."""
        try:
            response = supabase.table(ItineraryCRUD.TABLE_NAME)\
                .select("*")\
                .eq("id", itinerary_id)\
                .single()\
                .execute()
            
            return {"success": True, "message": "Itinerary retrieved", "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def get_by_destination(user_id: str, destination: str) -> dict:
        """Get itineraries for a specific destination."""
        try:
            response = supabase.table(ItineraryCRUD.TABLE_NAME)\
                .select("*")\
                .eq("user_id", user_id)\
                .ilike("destination", f"%{destination}%")\
                .order("created_at", desc=True)\
                .execute()
            
            return {"success": True, "message": "Itineraries retrieved", "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def update(itinerary_id: str, update_data: dict) -> dict:
        """Update an existing itinerary."""
        try:
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Convert days if present
            if "days" in update_data:
                update_data["days"] = [
                    day.model_dump() if hasattr(day, 'model_dump') else day 
                    for day in update_data["days"]
                ]
            
            response = supabase.table(ItineraryCRUD.TABLE_NAME)\
                .update(update_data)\
                .eq("id", itinerary_id)\
                .execute()
            
            if response.data:
                return {"success": True, "message": "Itinerary updated", "data": response.data[0]}
            return {"success": False, "message": "Failed to update itinerary", "data": None}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def delete(itinerary_id: str) -> dict:
        """Delete an itinerary by ID."""
        try:
            response = supabase.table(ItineraryCRUD.TABLE_NAME)\
                .delete()\
                .eq("id", itinerary_id)\
                .execute()
            
            return {"success": True, "message": "Itinerary deleted", "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def delete_by_user(user_id: str) -> dict:
        """Delete all itineraries for a user."""
        try:
            response = supabase.table(ItineraryCRUD.TABLE_NAME)\
                .delete()\
                .eq("user_id", user_id)\
                .execute()
            
            return {"success": True, "message": "All itineraries deleted", "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def count_by_user(user_id: str) -> dict:
        """Count total itineraries for a user."""
        try:
            response = supabase.table(ItineraryCRUD.TABLE_NAME)\
                .select("id", count="exact")\
                .eq("user_id", user_id)\
                .execute()
            
            return {"success": True, "message": "Count retrieved", "data": {"count": response.count}}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}

"""CRUD operations for Itineraries."""
from typing import List, Optional
from datetime import datetime
from app.database import config as db_config
from app.database.models import ItineraryCreate, Itinerary


class ItineraryCRUD:
    """CRUD operations for itineraries."""
    
    TABLE_NAME = "itineraries"

    @staticmethod
    def _execute_with_retry(operation, retries: int = 0):
        """Execute a database operation with one retry after client reinitialization."""
        last_error = None

        for attempt in range(retries + 1):
            try:
                return operation()
            except Exception as error:
                last_error = error
                if attempt < retries:
                    db_config.reinitialize_supabase_client()

        raise last_error

    @staticmethod
    def _normalize_budget(value: str) -> str:
        """Normalize budget input to DB-accepted values."""
        if value is None:
            return "moderate"

        normalized = str(value).strip().lower()
        if normalized in {"budget", "moderate", "luxury"}:
            return normalized

        if normalized in {"ultra budget", "low", "cheap", "economy"}:
            return "budget"
        if normalized in {"mid", "mid-range", "standard", "medium"}:
            return "moderate"
        if normalized in {"premium", "high", "expensive"}:
            return "luxury"

        if "$" in normalized or normalized.replace(".", "", 1).isdigit():
            digits = "".join(ch for ch in normalized if ch.isdigit() or ch == ".")
            try:
                amount = float(digits)
                if amount <= 600:
                    return "budget"
                if amount <= 1200:
                    return "moderate"
                return "luxury"
            except Exception:
                return "moderate"

        return "moderate"

    @staticmethod
    def _normalize_travel_style(value: str) -> str:
        """Normalize travel style to DB-accepted values."""
        if value is None:
            return "balanced"

        normalized = str(value).strip().lower()
        if normalized in {"relaxed", "balanced", "packed"}:
            return normalized

        alias_map = {
            "slow": "relaxed",
            "chill": "relaxed",
            "easy": "relaxed",
            "normal": "balanced",
            "moderate": "balanced",
            "fast": "packed",
            "intense": "packed",
            "busy": "packed",
        }
        return alias_map.get(normalized, "balanced")
    
    @staticmethod
    def _check_db_available() -> Optional[dict]:
        """Check if database is available."""
        if not db_config.SUPABASE_ENABLED or db_config.supabase is None:
            return {
                "success": False, 
                "message": "Database not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env file.",
                "data": None
            }
        return None
    
    @staticmethod
    def create(itinerary: ItineraryCreate) -> dict:
        """Create a new itinerary."""
        if error := ItineraryCRUD._check_db_available():
            return error
        
        try:
            data = itinerary.model_dump()
            data["budget"] = ItineraryCRUD._normalize_budget(data.get("budget"))
            data["travel_style"] = ItineraryCRUD._normalize_travel_style(data.get("travel_style"))
            # Convert days to JSON-serializable format
            data["days"] = [day.model_dump() if hasattr(day, 'model_dump') else day for day in data["days"]]

            response = ItineraryCRUD._execute_with_retry(
                lambda: db_config.supabase.table(ItineraryCRUD.TABLE_NAME).insert(data).execute()
            )
            
            if response.data:
                return {"success": True, "message": "Itinerary saved", "data": response.data[0]}
            return {"success": False, "message": "Failed to save itinerary", "data": None}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def get_by_user(user_id: str, limit: int = 50) -> dict:
        """Get all itineraries for a user."""
        if error := ItineraryCRUD._check_db_available():
            return error
        
        try:
            response = ItineraryCRUD._execute_with_retry(
                lambda: db_config.supabase.table(ItineraryCRUD.TABLE_NAME)
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            
            return {"success": True, "message": "Itineraries retrieved", "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def get_by_id(itinerary_id: str) -> dict:
        """Get a specific itinerary by ID."""
        if error := ItineraryCRUD._check_db_available():
            return error
        
        try:
            response = ItineraryCRUD._execute_with_retry(
                lambda: db_config.supabase.table(ItineraryCRUD.TABLE_NAME)
                .select("*")
                .eq("id", itinerary_id)
                .single()
                .execute()
            )
            
            return {"success": True, "message": "Itinerary retrieved", "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def get_by_destination(user_id: str, destination: str) -> dict:
        """Get itineraries for a specific destination."""
        if error := ItineraryCRUD._check_db_available():
            return error
        
        try:
            response = ItineraryCRUD._execute_with_retry(
                lambda: db_config.supabase.table(ItineraryCRUD.TABLE_NAME)
                .select("*")
                .eq("user_id", user_id)
                .ilike("destination", f"%{destination}%")
                .order("created_at", desc=True)
                .execute()
            )
            
            return {"success": True, "message": "Itineraries retrieved", "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def update(itinerary_id: str, update_data: dict) -> dict:
        """Update an existing itinerary."""
        if error := ItineraryCRUD._check_db_available():
            return error
        
        try:
            # Add updated_at timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            if "budget" in update_data:
                update_data["budget"] = ItineraryCRUD._normalize_budget(update_data.get("budget"))
            if "travel_style" in update_data:
                update_data["travel_style"] = ItineraryCRUD._normalize_travel_style(update_data.get("travel_style"))
            
            # Convert days if present
            if "days" in update_data:
                update_data["days"] = [
                    day.model_dump() if hasattr(day, 'model_dump') else day 
                    for day in update_data["days"]
                ]
            
            response = ItineraryCRUD._execute_with_retry(
                lambda: db_config.supabase.table(ItineraryCRUD.TABLE_NAME)
                .update(update_data)
                .eq("id", itinerary_id)
                .execute()
            )
            
            if response.data:
                return {"success": True, "message": "Itinerary updated", "data": response.data[0]}
            return {"success": False, "message": "Failed to update itinerary", "data": None}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def delete(itinerary_id: str) -> dict:
        """Delete an itinerary by ID."""
        if error := ItineraryCRUD._check_db_available():
            return error
        
        try:
            response = ItineraryCRUD._execute_with_retry(
                lambda: db_config.supabase.table(ItineraryCRUD.TABLE_NAME)
                .delete()
                .eq("id", itinerary_id)
                .execute()
            )
            
            return {"success": True, "message": "Itinerary deleted", "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def delete_by_user(user_id: str) -> dict:
        """Delete all itineraries for a user."""
        if error := ItineraryCRUD._check_db_available():
            return error
        
        try:
            response = ItineraryCRUD._execute_with_retry(
                lambda: db_config.supabase.table(ItineraryCRUD.TABLE_NAME)
                .delete()
                .eq("user_id", user_id)
                .execute()
            )
            
            return {"success": True, "message": "All itineraries deleted", "data": response.data}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}
    
    @staticmethod
    def count_by_user(user_id: str) -> dict:
        """Count total itineraries for a user."""
        if error := ItineraryCRUD._check_db_available():
            return error
        
        try:
            response = ItineraryCRUD._execute_with_retry(
                lambda: db_config.supabase.table(ItineraryCRUD.TABLE_NAME)
                .select("id", count="exact")
                .eq("user_id", user_id)
                .execute()
            )
            
            return {"success": True, "message": "Count retrieved", "data": {"count": response.count}}
        except Exception as e:
            return {"success": False, "message": str(e), "data": None}

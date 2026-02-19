"""Supabase configuration and client initialization."""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Check if Supabase is configured
SUPABASE_ENABLED = bool(SUPABASE_URL and SUPABASE_ANON_KEY)

# Global client instance (will be None if not configured)
supabase: Optional[object] = None

if SUPABASE_ENABLED:
    try:
        from supabase import create_client, Client
        
        # Create Supabase client
        def get_supabase_client() -> Client:
            """Get Supabase client instance."""
            return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

        # Service role client for admin operations
        def get_supabase_admin_client() -> Client:
            """Get Supabase admin client with service role key."""
            if not SUPABASE_SERVICE_ROLE_KEY:
                raise ValueError("SUPABASE_SERVICE_ROLE_KEY is required for admin operations")
            return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

        # Initialize global client
        supabase = get_supabase_client()
        print("✅ Supabase database connected successfully")
    except Exception as e:
        print(f"⚠️ Failed to initialize Supabase: {e}")
        supabase = None
        SUPABASE_ENABLED = False
else:
    print("⚠️ Supabase not configured. Database features (wishlist, saved itineraries) will be disabled.")

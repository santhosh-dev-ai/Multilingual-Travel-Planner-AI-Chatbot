"""Supabase configuration and client initialization."""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Validate configuration
if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError(
        "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env file"
    )

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

# Global client instance
supabase: Client = get_supabase_client()

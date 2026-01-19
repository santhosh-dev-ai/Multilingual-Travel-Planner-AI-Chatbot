#!/usr/bin/env python3
"""Check if database setup is complete."""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("Database Setup Check")
print("=" * 50)

# Check environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_anon = os.getenv("SUPABASE_ANON_KEY")
supabase_service = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
database_port = os.getenv("DATABASE_PORT", "8001")

print(f"\n1. Environment Variables:")
print(f"   SUPABASE_URL: {'[OK] SET' if supabase_url else '[X] NOT SET'}")
print(f"   SUPABASE_ANON_KEY: {'[OK] SET' if supabase_anon else '[X] NOT SET'}")
print(f"   SUPABASE_SERVICE_ROLE_KEY: {'[OK] SET' if supabase_service else '[X] NOT SET'}")
print(f"   DATABASE_PORT: {database_port}")

# Check if .env file exists
env_exists = os.path.exists(".env")
print(f"\n2. .env file: {'[OK] EXISTS' if env_exists else '[X] NOT FOUND'}")

# Try to connect to Supabase if credentials exist
if supabase_url and supabase_anon:
    try:
        from supabase import create_client
        client = create_client(supabase_url, supabase_anon)
        print(f"\n3. Supabase Connection: [OK] SUCCESS")
        
        # Try to query wishlists table
        try:
            response = client.table("wishlists").select("id").limit(1).execute()
            print(f"4. Wishlists Table: [OK] ACCESSIBLE")
        except Exception as e:
            print(f"4. Wishlists Table: [X] ERROR - {str(e)}")
            print("   -> Make sure you've run schema.sql in Supabase SQL Editor")
    except Exception as e:
        print(f"\n3. Supabase Connection: [X] FAILED - {str(e)}")
else:
    print(f"\n3. Supabase Connection: [X] SKIPPED (missing credentials)")

print("\n" + "=" * 50)
print("Next Steps:")
if not env_exists:
    print("1. Create a .env file in the database/ folder")
    print("2. Add your Supabase credentials:")
    print("   SUPABASE_URL=https://your-project.supabase.co")
    print("   SUPABASE_ANON_KEY=your-anon-key")
    print("   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key")
    print("   DATABASE_PORT=8001")
if not (supabase_url and supabase_anon):
    print("3. Get your credentials from: https://supabase.com/dashboard")
    print("   → Settings → API")
print("4. Run schema.sql in Supabase SQL Editor to create tables")
print("5. Start the server: python api.py")
print("=" * 50)


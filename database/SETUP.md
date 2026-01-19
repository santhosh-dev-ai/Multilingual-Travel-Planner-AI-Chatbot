# Quick Setup Guide

## Step 1: Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Wait for project creation (2-3 minutes)

## Step 2: Get Your API Keys

1. In Supabase dashboard, go to **Settings** → **API**
2. Copy these values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon public** key
   - **service_role** key

## Step 3: Create Database Tables

1. In Supabase dashboard, go to **SQL Editor**
2. Open `schema.sql` from this folder
3. Copy all SQL code and paste into SQL Editor
4. Click "Run" to create tables

## Step 4: Create .env File

Create a file named `.env` in this folder with:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
DATABASE_PORT=8001
```

Replace the placeholder values with your actual Supabase credentials.

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 6: Start the Server

**Windows:**
```bash
start_server.bat
```

**Or manually:**
```bash
python api.py
```

The server will start on http://localhost:8001

## Verify It's Working

Open http://localhost:8001/health in your browser. You should see:
```json
{
  "status": "healthy",
  "database": "supabase",
  "endpoints": {
    "wishlist": "/api/wishlist",
    "itinerary": "/api/itinerary"
  }
}
```


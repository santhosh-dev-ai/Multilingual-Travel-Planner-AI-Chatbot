# Quick Start Guide - Fix Wishlist Not Working

## The Problem
Your wishlist isn't working because the **Database API Server** (port 8001) is not running. Even though Supabase is configured, you need this server running to connect the frontend to Supabase.

## Architecture
```
Frontend (port 3000) 
    ↓
Database API Server (port 8001) ← YOU NEED THIS RUNNING
    ↓
Supabase Database
```

## Quick Fix (3 Steps)

### Step 1: Create .env file in `database/` folder

Create a file named `.env` in the `database/` folder with your Supabase credentials:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
DATABASE_PORT=8001
```

**Where to get these:**
1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **Settings** → **API**
4. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_ANON_KEY`
   - **service_role** key → `SUPABASE_SERVICE_ROLE_KEY`

### Step 2: Make sure database tables exist

1. In Supabase dashboard, go to **SQL Editor**
2. Open `database/schema.sql` file
3. Copy all the SQL code
4. Paste into Supabase SQL Editor
5. Click **Run**

This creates the `wishlists` and `itineraries` tables.

### Step 3: Start the Database API Server

**Windows:**
```bash
cd database
python api.py
```

**Or use the batch file:**
```bash
database\start_server.bat
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8001
```

## Verify It's Working

1. Open http://localhost:8001/health in your browser
2. You should see: `{"status": "healthy", "database": "supabase", ...}`
3. Your frontend wishlist should now work!

## Troubleshooting

### "Missing Supabase credentials" error
→ Make sure `.env` file exists in `database/` folder with correct values

### "Table doesn't exist" error
→ Run `schema.sql` in Supabase SQL Editor

### Port 8001 already in use
→ Change `DATABASE_PORT=8002` in `.env` and update frontend `.env`:
  ```
  NEXT_PUBLIC_DATABASE_URL=http://localhost:8002/api
  ```

### Still not working?
Run the check script:
```bash
python database/check_setup.py
```

This will tell you exactly what's missing.


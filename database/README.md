# TravelGenie Database Service

A standalone database service using Supabase for storing wishlists and itineraries.

## Setup

### 1. Create a Supabase Project

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Click "New Project"
3. Fill in the project details and wait for it to be created

### 2. Create Database Tables

1. In your Supabase dashboard, go to **SQL Editor**
2. Copy the contents of `schema.sql`
3. Paste and run in the SQL Editor
4. This will create the `wishlists` and `itineraries` tables

### 3. Get Your API Keys

1. Go to **Settings** → **API** in your Supabase dashboard
2. Copy:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon public** key
   - **service_role** key (for admin operations)

### 4. Configure Environment

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your Supabase credentials:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
   DATABASE_PORT=8001
   ```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Server

```bash
python api.py
# or
uvicorn api:app --reload --port 8001
```

## API Endpoints

### Wishlist

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/wishlist/{user_id}` | Get user's wishlist |
| POST | `/api/wishlist` | Add to wishlist |
| POST | `/api/wishlist/toggle` | Toggle wishlist item |
| GET | `/api/wishlist/{user_id}/check/{destination_id}` | Check if in wishlist |
| DELETE | `/api/wishlist/{wishlist_id}` | Remove by ID |
| DELETE | `/api/wishlist/{user_id}/destination/{destination_id}` | Remove by destination |
| DELETE | `/api/wishlist/{user_id}/clear` | Clear all |

### Itinerary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/itinerary/{user_id}` | Get user's itineraries |
| GET | `/api/itinerary/detail/{itinerary_id}` | Get single itinerary |
| GET | `/api/itinerary/{user_id}/destination/{destination}` | Get by destination |
| POST | `/api/itinerary` | Save new itinerary |
| PUT | `/api/itinerary/{itinerary_id}` | Update itinerary |
| DELETE | `/api/itinerary/{itinerary_id}` | Delete itinerary |
| DELETE | `/api/itinerary/{user_id}/all` | Delete all |
| GET | `/api/itinerary/{user_id}/count` | Get count |

## Project Structure

```
database/
├── api.py              # FastAPI server
├── config.py           # Supabase configuration
├── models.py           # Pydantic models
├── schema.sql          # Database schema
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
├── README.md           # This file
└── crud/
    ├── __init__.py
    ├── wishlist.py     # Wishlist CRUD operations
    └── itinerary.py    # Itinerary CRUD operations
```

## Usage Examples

### Add to Wishlist

```bash
curl -X POST "http://localhost:8001/api/wishlist" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "destination_id": 1,
    "destination_name": "Santorini",
    "destination_country": "Greece",
    "destination_image": "https://example.com/image.jpg",
    "destination_price": "$1,299",
    "destination_rating": 4.9
  }'
```

### Save Itinerary

```bash
curl -X POST "http://localhost:8001/api/itinerary" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "destination": "Tokyo",
    "destination_country": "Japan",
    "duration": 3,
    "travel_style": "balanced",
    "budget": "moderate",
    "summary": "Amazing 3 days in Tokyo!",
    "days": [{"day": 1, "title": "Day 1", "activities": []}]
  }'
```

## Notes

- The database uses UUIDs for primary keys
- Row Level Security (RLS) is enabled but currently allows all operations
- For production, update RLS policies to use actual authentication
- The service runs on port 8001 by default (separate from backend on 8000)

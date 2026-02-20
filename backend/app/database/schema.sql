-- =============================================
-- TravelGenie Database Schema for Supabase
-- =============================================
-- Run this SQL in your Supabase SQL Editor to create the tables
-- Dashboard: https://supabase.com/dashboard -> SQL Editor


-- =============================================
-- WISHLISTS TABLE
-- =============================================

CREATE TABLE IF NOT EXISTS wishlists (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    destination_id INTEGER NOT NULL,
    destination_name TEXT NOT NULL,
    destination_country TEXT NOT NULL,
    destination_image TEXT,
    destination_price TEXT,
    destination_rating DECIMAL(2,1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, destination_id)
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_wishlists_user_id ON wishlists(user_id);
CREATE INDEX IF NOT EXISTS idx_wishlists_destination_id ON wishlists(destination_id);
CREATE INDEX IF NOT EXISTS idx_wishlists_created_at ON wishlists(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE wishlists ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own wishlist items
CREATE POLICY "Users can view own wishlist" ON wishlists
    FOR SELECT USING (true);  -- For now, allow all reads (no auth)

-- Policy: Users can insert their own wishlist items
CREATE POLICY "Users can insert own wishlist" ON wishlists
    FOR INSERT WITH CHECK (true);  -- For now, allow all inserts

-- Policy: Users can delete their own wishlist items
CREATE POLICY "Users can delete own wishlist" ON wishlists
    FOR DELETE USING (true);  -- For now, allow all deletes


-- =============================================
-- ITINERARIES TABLE
-- =============================================

CREATE TABLE IF NOT EXISTS itineraries (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    destination TEXT NOT NULL,
    destination_country TEXT,
    duration INTEGER NOT NULL CHECK (duration > 0 AND duration <= 30),
    travel_style TEXT DEFAULT 'balanced' CHECK (travel_style IN ('relaxed', 'balanced', 'packed')),
    budget TEXT DEFAULT 'moderate' CHECK (budget IN ('budget', 'moderate', 'luxury')),
    summary TEXT,
    days JSONB NOT NULL,  -- Store daily itinerary as JSON
    budget_estimate TEXT,
    packing_tips TEXT[],  -- Array of packing tips
    local_phrases JSONB,  -- Store phrases as JSON
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_itineraries_user_id ON itineraries(user_id);
CREATE INDEX IF NOT EXISTS idx_itineraries_destination ON itineraries(destination);
CREATE INDEX IF NOT EXISTS idx_itineraries_created_at ON itineraries(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE itineraries ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view itineraries (open for now)
CREATE POLICY "Users can view itineraries" ON itineraries
    FOR SELECT USING (true);

-- Policy: Users can insert itineraries
CREATE POLICY "Users can insert itineraries" ON itineraries
    FOR INSERT WITH CHECK (true);

-- Policy: Users can update itineraries
CREATE POLICY "Users can update itineraries" ON itineraries
    FOR UPDATE USING (true);

-- Policy: Users can delete itineraries
CREATE POLICY "Users can delete itineraries" ON itineraries
    FOR DELETE USING (true);


-- =============================================
-- USER PROFILES TABLE (AUTH)
-- =============================================

CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id UUID UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone_number TEXT NOT NULL,
    is_email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_username ON user_profiles(username);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);

-- Enable Row Level Security (RLS)
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Policies (open for current app architecture)
CREATE POLICY "Users can view profiles" ON user_profiles
    FOR SELECT USING (true);

CREATE POLICY "Users can insert profiles" ON user_profiles
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can update profiles" ON user_profiles
    FOR UPDATE USING (true);


-- =============================================
-- HELPFUL VIEWS (Optional)
-- =============================================

-- View: User wishlist summary
CREATE OR REPLACE VIEW user_wishlist_summary AS
SELECT 
    user_id,
    COUNT(*) as total_items,
    ARRAY_AGG(destination_name) as destinations,
    MAX(created_at) as last_added
FROM wishlists
GROUP BY user_id;

-- View: User itinerary summary
CREATE OR REPLACE VIEW user_itinerary_summary AS
SELECT 
    user_id,
    COUNT(*) as total_itineraries,
    SUM(duration) as total_days_planned,
    ARRAY_AGG(DISTINCT destination) as destinations,
    MAX(created_at) as last_created
FROM itineraries
GROUP BY user_id;


-- =============================================
-- SAMPLE DATA (Optional - for testing)
-- =============================================

-- Uncomment to insert sample data:
/*
INSERT INTO wishlists (user_id, destination_id, destination_name, destination_country, destination_image, destination_price, destination_rating)
VALUES 
    ('user_123', 1, 'Santorini', 'Greece', 'https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e', '$1,299', 4.9),
    ('user_123', 2, 'Kyoto', 'Japan', 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e', '$1,499', 4.8);

INSERT INTO itineraries (user_id, destination, destination_country, duration, travel_style, budget, summary, days, budget_estimate, packing_tips)
VALUES (
    'user_123',
    'Tokyo',
    'Japan',
    3,
    'balanced',
    'moderate',
    'Experience 3 amazing days in Tokyo!',
    '[{"day": 1, "title": "Classic Tokyo Icons", "activities": []}]'::jsonb,
    '$1,500 - $2,000',
    ARRAY['Comfortable walking shoes', 'Universal adapter']
);
*/

-- =============================================
-- Fix Row Level Security for TravelGenie
-- =============================================
-- Run this in your Supabase SQL Editor to enable public access
-- (For production, you'd want proper authentication)

-- Option 1: Disable RLS completely (simplest for development)
ALTER TABLE wishlists DISABLE ROW LEVEL SECURITY;
ALTER TABLE itineraries DISABLE ROW LEVEL SECURITY;

-- OR Option 2: Keep RLS but allow all operations (better for later adding auth)
-- Uncomment below if you prefer this approach:
/*
-- Drop existing policies first
DROP POLICY IF EXISTS "Users can view own wishlist" ON wishlists;
DROP POLICY IF EXISTS "Users can insert own wishlist" ON wishlists;
DROP POLICY IF EXISTS "Users can delete own wishlist" ON wishlists;
DROP POLICY IF EXISTS "Users can view itineraries" ON itineraries;
DROP POLICY IF EXISTS "Users can insert itineraries" ON itineraries;
DROP POLICY IF EXISTS "Users can update itineraries" ON itineraries;
DROP POLICY IF EXISTS "Users can delete itineraries" ON itineraries;

-- Create permissive policies that allow all operations
CREATE POLICY "Allow all operations on wishlists" ON wishlists
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on itineraries" ON itineraries
    FOR ALL USING (true) WITH CHECK (true);
*/

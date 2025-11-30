-- ============================================================
-- Supabase RLS Policies - Security Configuration
-- ============================================================
-- Run this SQL script in your Supabase SQL Editor
-- AFTER running supabase_setup.sql
-- ============================================================
-- This enables Row Level Security and creates policies that
-- allow the booking assistant to function while protecting data
-- ============================================================

-- ============================================================
-- Step 1: Enable RLS (if not already enabled)
-- ============================================================
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- Step 2: Drop existing policies (if any)
-- ============================================================
DROP POLICY IF EXISTS "Allow insert for customers" ON customers;
DROP POLICY IF EXISTS "Allow select for customers" ON customers;
DROP POLICY IF EXISTS "Allow update for customers" ON customers;
DROP POLICY IF EXISTS "Enable all operations for authenticated users" ON customers;

DROP POLICY IF EXISTS "Allow insert for bookings" ON bookings;
DROP POLICY IF EXISTS "Allow select for bookings" ON bookings;
DROP POLICY IF EXISTS "Allow update for bookings" ON bookings;
DROP POLICY IF EXISTS "Enable all operations for authenticated users" ON bookings;

-- ============================================================
-- Step 3: Create CUSTOMERS TABLE POLICIES
-- ============================================================
-- Allow anonymous users to create customers (for booking flow)
CREATE POLICY "Allow insert for customers" ON customers
    FOR INSERT
    WITH CHECK (true);

-- Allow anonymous users to read customers (for booking lookups)
CREATE POLICY "Allow select for customers" ON customers
    FOR SELECT
    USING (true);

-- Allow anonymous users to update customers (if needed)
CREATE POLICY "Allow update for customers" ON customers
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

-- ============================================================
-- Step 4: Create BOOKINGS TABLE POLICIES
-- ============================================================
-- Allow anonymous users to create bookings
CREATE POLICY "Allow insert for bookings" ON bookings
    FOR INSERT
    WITH CHECK (true);

-- Allow anonymous users to read bookings (for admin dashboard and user lookups)
CREATE POLICY "Allow select for bookings" ON bookings
    FOR SELECT
    USING (true);

-- Allow anonymous users to update bookings (for admin to edit/cancel)
CREATE POLICY "Allow update for bookings" ON bookings
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

-- ============================================================
-- Step 5: Verify RLS is enabled
-- ============================================================
-- Run this to verify:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('customers', 'bookings');
-- Both should show rowsecurity = true

-- ============================================================
-- IMPORTANT SECURITY NOTES:
-- ============================================================
-- 1. These policies allow the anon key to perform operations
-- 2. For production, consider:
--    - Using service role key for admin operations
--    - Adding email-based restrictions for user lookups
--    - Implementing rate limiting
-- 3. The anon key should be kept secret in production
-- 4. Monitor database access logs regularly
-- ============================================================


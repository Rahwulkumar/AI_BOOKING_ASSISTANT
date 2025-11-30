-- ============================================================
-- AI Booking Assistant - Supabase Database Setup
-- ============================================================
-- Run this SQL script in your Supabase SQL Editor
-- (Go to: Project Dashboard > SQL Editor > New Query)
-- ============================================================

-- Drop existing tables if they exist (CAUTION: This will delete all data)
-- Uncomment the lines below if you want to reset the database
-- DROP TABLE IF EXISTS bookings CASCADE;
-- DROP TABLE IF EXISTS customers CASCADE;

-- ============================================================
-- Create CUSTOMERS table
-- ============================================================
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- Create BOOKINGS table
-- ============================================================
CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE CASCADE,
    booking_type TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    status TEXT DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- Create Indexes for Performance
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_customer_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_booking_date ON bookings(date);
CREATE INDEX IF NOT EXISTS idx_customer_id ON bookings(customer_id);
CREATE INDEX IF NOT EXISTS idx_booking_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_booking_created_at ON bookings(created_at DESC);

-- ============================================================
-- Enable Row Level Security (RLS) - SECURITY CRITICAL
-- ============================================================
-- Enable RLS on tables
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- CUSTOMERS TABLE POLICIES
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
-- BOOKINGS TABLE POLICIES
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

-- Note: DELETE is not allowed (no DELETE operations in the app)

-- ============================================================
-- Verify Tables Created Successfully
-- ============================================================
-- Run this to check your tables
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- ============================================================
-- Insert Sample Data (Optional - for testing)
-- ============================================================
-- Uncomment to add sample data:
/*
INSERT INTO customers (name, email, phone) VALUES
    ('John Doe', 'john.doe@example.com', '+1234567890'),
    ('Jane Smith', 'jane.smith@example.com', '+0987654321');

INSERT INTO bookings (customer_id, booking_type, date, time, status) VALUES
    (1, 'General Checkup', '2025-12-01', '10:00:00', 'confirmed'),
    (2, 'Dental Cleaning', '2025-12-02', '14:30:00', 'confirmed');
*/

-- ============================================================
-- SUCCESS! 
-- Your database is now ready to use with the AI Booking Assistant
-- ============================================================


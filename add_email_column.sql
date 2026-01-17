-- Migration: Add email column to users table
-- Run this in your PostgreSQL database

-- Add email column if it doesn't exist
ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(150);

-- Make email unique (after populating data)
-- ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email);

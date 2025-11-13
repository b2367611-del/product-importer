-- Create database if it doesn't exist
-- This script runs when PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set default configuration
ALTER DATABASE product_importer SET timezone TO 'UTC';
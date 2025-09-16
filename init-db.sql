-- Database initialization script for Agent Builder
-- This script will be run automatically when the PostgreSQL container starts

-- Create database if it doesn't exist (handled by POSTGRES_DB env var)

-- Set up extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE agent_builder TO postgres;

-- Create indexes for better performance (will be added by Alembic migrations)
-- These are just placeholders - actual indexes are managed by Alembic

-- Log the initialization
DO $$
BEGIN
    RAISE NOTICE 'Agent Builder database initialized successfully';
END $$;
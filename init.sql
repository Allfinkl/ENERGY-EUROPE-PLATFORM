-- init.sql
-- Creates the database schemas
-- Runs automatically when PostgreSQL container starts for the first time

CREATE SCHEMA IF NOT EXISTS raw;    -- stores data exactly as received from APIs
CREATE SCHEMA IF NOT EXISTS staging; -- stores lightly cleaned data
CREATE SCHEMA IF NOT EXISTS marts;   -- stores final analytical tables
CREATE SCHEMA IF NOT EXISTS ml;      -- stores ML predictions

-- Grant permissions to our user
GRANT ALL PRIVILEGES ON SCHEMA raw     TO energy_user;
GRANT ALL PRIVILEGES ON SCHEMA staging TO energy_user;
GRANT ALL PRIVILEGES ON SCHEMA marts   TO energy_user;
GRANT ALL PRIVILEGES ON SCHEMA ml      TO energy_user;


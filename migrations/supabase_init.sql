-- Urban-Infra Supabase Database Setup
-- PostGIS Extension and SF Neighborhoods Schema

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA extensions;

-- Create our main schema
CREATE SCHEMA IF NOT EXISTS urban_infra;

-- Set search path to include our schema and extensions
SET search_path TO urban_infra, extensions, public;

-- Main neighborhoods table with spatial data
CREATE TABLE IF NOT EXISTS urban_infra.sf_neighborhoods (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    area_type VARCHAR(50) NOT NULL,
    data JSONB,
    
    -- Spatial columns for boundaries
    boundary GEOMETRY(POLYGON, 4326),
    centroid GEOMETRY(POINT, 4326),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create spatial indexes for performance
CREATE INDEX IF NOT EXISTS idx_sf_neighborhoods_boundary 
ON urban_infra.sf_neighborhoods USING GIST (boundary);

CREATE INDEX IF NOT EXISTS idx_sf_neighborhoods_centroid 
ON urban_infra.sf_neighborhoods USING GIST (centroid);

-- Create index on area_type for filtering
CREATE INDEX IF NOT EXISTS idx_sf_neighborhoods_area_type 
ON urban_infra.sf_neighborhoods (area_type);

-- Create GIN index on JSONB data for fast queries
CREATE INDEX IF NOT EXISTS idx_sf_neighborhoods_data 
ON urban_infra.sf_neighborhoods USING GIN (data);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION urban_infra.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_sf_neighborhoods_updated_at 
    BEFORE UPDATE ON urban_infra.sf_neighborhoods 
    FOR EACH ROW EXECUTE FUNCTION urban_infra.update_updated_at_column();

-- Insert sample SF neighborhood data
INSERT INTO urban_infra.sf_neighborhoods (name, area_type, data, centroid) VALUES
(
    'Marina District',
    'marina',
    '{
        "characteristics": ["low_density", "waterfront", "affluent"],
        "zoning": "RH-1",
        "zoning_details": {
            "max_far": 0.8,
            "max_height_ft": 40,
            "min_parking": 1.0,
            "setback_front_ft": 15,
            "setback_side_ft": 4,
            "inclusionary_pct": 0.12
        },
        "transit_access": "limited",
        "flood_risk": "high",
        "constraints": ["flood_zone", "height_limit", "historic_overlay"]
    }'::jsonb,
    ST_SetSRID(ST_MakePoint(-122.4364, 37.8041), 4326)
),
(
    'Hayes Valley',
    'hayes_valley', 
    '{
        "characteristics": ["mixed_use", "transit_rich", "gentrifying"],
        "zoning": "NCT-3",
        "zoning_details": {
            "max_far": 3.0,
            "max_height_ft": 55,
            "min_parking": 0.5,
            "ground_floor_commercial": true,
            "inclusionary_pct": 0.20
        },
        "transit_access": "excellent",
        "displacement_risk": "high",
        "constraints": ["historic_preservation", "displacement_pressure"]
    }'::jsonb,
    ST_SetSRID(ST_MakePoint(-122.4241, 37.7749), 4326)
),
(
    'Mission District',
    'mission',
    '{
        "characteristics": ["dense", "diverse", "cultural"],
        "zoning": "NCT-4", 
        "zoning_details": {
            "max_far": 4.0,
            "max_height_ft": 85,
            "min_parking": 0.25,
            "ground_floor_commercial": true,
            "inclusionary_pct": 0.25
        },
        "transit_access": "good",
        "cultural_assets": "high",
        "constraints": ["displacement_risk", "cultural_preservation", "seismic_zone"]
    }'::jsonb,
    ST_SetSRID(ST_MakePoint(-122.4194, 37.7599), 4326)
);

-- Create RLS (Row Level Security) policies if needed
-- ALTER TABLE urban_infra.sf_neighborhoods ENABLE ROW LEVEL SECURITY;

-- Verify the data was inserted
SELECT 
    name,
    area_type,
    data->>'zoning' as zoning,
    ST_AsText(centroid) as location
FROM urban_infra.sf_neighborhoods
ORDER BY name;
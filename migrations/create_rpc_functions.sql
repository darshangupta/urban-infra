-- Create RPC functions to access urban_infra schema via Supabase REST API
-- Run this SQL in your Supabase SQL Editor

-- Function to get all SF neighborhoods
CREATE OR REPLACE FUNCTION public.get_sf_neighborhoods()
RETURNS TABLE (
    id integer,
    name varchar,
    area_type varchar,
    data jsonb,
    centroid text,
    created_at timestamptz,
    updated_at timestamptz
) 
LANGUAGE sql
SECURITY definer
AS $$
    SELECT 
        id,
        name,
        area_type,
        data,
        ST_AsText(centroid) as centroid,
        created_at,
        updated_at
    FROM urban_infra.sf_neighborhoods
    ORDER BY name;
$$;

-- Function to get specific neighborhood by name
CREATE OR REPLACE FUNCTION public.get_neighborhood_by_name(neighborhood_name text)
RETURNS TABLE (
    id integer,
    name varchar,
    area_type varchar,
    data jsonb,
    centroid text,
    created_at timestamptz,
    updated_at timestamptz
)
LANGUAGE sql 
SECURITY definer
AS $$
    SELECT 
        id,
        name,
        area_type,
        data,
        ST_AsText(centroid) as centroid,
        created_at,
        updated_at
    FROM urban_infra.sf_neighborhoods
    WHERE LOWER(REPLACE(name, ' ', '_')) = LOWER(neighborhood_name)
       OR LOWER(name) = LOWER(neighborhood_name)
    LIMIT 1;
$$;

-- Function to search neighborhoods by area type
CREATE OR REPLACE FUNCTION public.get_neighborhoods_by_type(type_filter text)
RETURNS TABLE (
    id integer,
    name varchar,
    area_type varchar,
    data jsonb,
    centroid text
)
LANGUAGE sql
SECURITY definer  
AS $$
    SELECT 
        id,
        name,
        area_type, 
        data,
        ST_AsText(centroid) as centroid
    FROM urban_infra.sf_neighborhoods
    WHERE area_type = type_filter
    ORDER BY name;
$$;

-- Grant execute permissions to authenticated and anonymous users
GRANT EXECUTE ON FUNCTION public.get_sf_neighborhoods() TO anon, authenticated;
GRANT EXECUTE ON FUNCTION public.get_neighborhood_by_name(text) TO anon, authenticated;  
GRANT EXECUTE ON FUNCTION public.get_neighborhoods_by_type(text) TO anon, authenticated;
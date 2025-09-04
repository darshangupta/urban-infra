#!/usr/bin/env python3
"""
Load real San Francisco data for urban planning analysis.
Data sources:
- SF Open Data Portal
- SF Planning Department
- Census Bureau
"""

import requests
import json
import geopandas as gpd
from pathlib import Path
import psycopg2
from sqlalchemy import create_engine
import os

# SF Open Data endpoints
SF_DATA_ENDPOINTS = {
    "zoning": "https://data.sfgov.org/api/geospatial/8br2-hhp3?method=export&format=GeoJSON",
    "parcels": "https://data.sfgov.org/api/geospatial/acdm-wktn?method=export&format=GeoJSON", 
    "neighborhoods": "https://data.sfgov.org/api/geospatial/p5b7-5n3h?method=export&format=GeoJSON",
    "transit_stops": "https://data.sfgov.org/api/geospatial/2rqv-u8qf?method=export&format=GeoJSON"
}

# Neighborhood boundaries we care about
TARGET_NEIGHBORHOODS = {
    "marina": ["Marina", "Cow Hollow"],
    "hayes_valley": ["Hayes Valley", "Lower Haight"],
    "mission": ["Mission", "Mission Bay", "Potrero Hill"]
}

def download_sf_data(endpoint_name: str, url: str, force_refresh: bool = False) -> dict:
    """Download SF data and cache locally"""
    cache_file = Path(f"data/{endpoint_name}.geojson")
    cache_file.parent.mkdir(exist_ok=True)
    
    if cache_file.exists() and not force_refresh:
        print(f"Loading cached {endpoint_name} data...")
        with open(cache_file) as f:
            return json.load(f)
    
    print(f"Downloading {endpoint_name} data from SF Open Data...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Cache the data
        with open(cache_file, 'w') as f:
            json.dump(data, f)
            
        print(f"✓ Downloaded {len(data.get('features', []))} features for {endpoint_name}")
        return data
        
    except Exception as e:
        print(f"✗ Failed to download {endpoint_name}: {e}")
        return {"type": "FeatureCollection", "features": []}

def filter_neighborhood_data(geojson_data: dict, target_neighborhoods: list) -> dict:
    """Filter data to our target neighborhoods"""
    filtered_features = []
    
    for feature in geojson_data.get("features", []):
        props = feature.get("properties", {})
        
        # Check various name fields
        name_fields = ["name", "neighborhood", "nhood", "district"]
        feature_name = None
        
        for field in name_fields:
            if field in props and props[field]:
                feature_name = props[field].lower()
                break
        
        if feature_name:
            for target in target_neighborhoods:
                if target.lower() in feature_name or feature_name in target.lower():
                    filtered_features.append(feature)
                    break
    
    return {
        "type": "FeatureCollection",
        "features": filtered_features
    }

def load_to_database(geojson_data: dict, table_name: str, engine):
    """Load GeoJSON data into PostGIS database"""
    if not geojson_data.get("features"):
        print(f"No features to load for {table_name}")
        return
    
    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
    
    # Ensure we have a geometry column
    if gdf.empty or 'geometry' not in gdf.columns:
        print(f"No valid geometry in {table_name}")
        return
    
    # Set CRS to WGS84 (EPSG:4326) - standard for SF Open Data
    gdf.crs = "EPSG:4326"
    
    # Load to database
    try:
        gdf.to_postgis(table_name, engine, if_exists="replace", index=False)
        print(f"✓ Loaded {len(gdf)} features to {table_name} table")
    except Exception as e:
        print(f"✗ Failed to load {table_name}: {e}")

def main():
    """Main data loading pipeline"""
    print("🏙️  Loading San Francisco data for urban-infra...")
    
    # Database connection
    db_url = "postgresql://postgres:password@localhost:5432/urban_infra"
    engine = create_engine(db_url)
    
    # Test database connection
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT PostGIS_Version();")
            version = result.fetchone()
            print(f"✓ Connected to PostGIS: {version[0]}")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return
    
    # Download and process each dataset
    all_neighborhoods = []
    
    for name, url in SF_DATA_ENDPOINTS.items():
        print(f"\n--- Processing {name} ---")
        
        # Download data
        data = download_sf_data(name, url)
        
        if name == "neighborhoods":
            # Filter to our target neighborhoods
            for area, neighborhoods in TARGET_NEIGHBORHOODS.items():
                filtered_data = filter_neighborhood_data(data, neighborhoods)
                if filtered_data["features"]:
                    load_to_database(filtered_data, f"neighborhoods_{area}", engine)
                    all_neighborhoods.extend(filtered_data["features"])
        else:
            # Load full dataset (we'll filter spatially later)
            load_to_database(data, name, engine)
    
    # Create a combined neighborhoods table
    if all_neighborhoods:
        combined_data = {"type": "FeatureCollection", "features": all_neighborhoods}
        load_to_database(combined_data, "target_neighborhoods", engine)
    
    print(f"\n🎉 SF data loading complete!")
    print(f"Next steps:")
    print(f"  1. docker exec postgres psql -U postgres -d urban_infra")
    print(f"  2. \\dt  -- to see loaded tables")
    print(f"  3. SELECT count(*) FROM target_neighborhoods;")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Simple test to load basic SF neighborhood data without heavy dependencies
"""

import requests
import json
import psycopg2
from pathlib import Path

def test_database_connection():
    """Test connection to PostGIS database"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5434,
            database="urban_infra", 
            user="postgres",
            password="password"
        )
        
        with conn.cursor() as cur:
            cur.execute("SELECT PostGIS_Version();")
            version = cur.fetchone()
            print(f"✓ PostGIS connection successful: {version[0]}")
            
            # Create a simple test table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sf_neighborhoods (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    area_type VARCHAR(50),
                    data JSONB
                );
            """)
            conn.commit()
            print("✓ Created test table")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def load_sample_neighborhoods():
    """Load sample neighborhood data"""
    neighborhoods = [
        {
            "name": "Marina District",
            "area_type": "marina", 
            "data": {
                "characteristics": ["low_density", "waterfront", "affluent"],
                "zoning": "RH-1", 
                "transit_access": "limited",
                "flood_risk": "high"
            }
        },
        {
            "name": "Hayes Valley",
            "area_type": "hayes_valley",
            "data": {
                "characteristics": ["mixed_use", "transit_rich", "gentrifying"],
                "zoning": "NCT-3",
                "transit_access": "excellent", 
                "displacement_risk": "high"
            }
        },
        {
            "name": "Mission District", 
            "area_type": "mission",
            "data": {
                "characteristics": ["dense", "diverse", "cultural"],
                "zoning": "RM-2",
                "transit_access": "good",
                "cultural_assets": "high"
            }
        }
    ]
    
    try:
        conn = psycopg2.connect(
            host="localhost", port=5434, database="urban_infra",
            user="postgres", password="password"
        )
        
        with conn.cursor() as cur:
            # Clear existing data
            cur.execute("DELETE FROM sf_neighborhoods;")
            
            # Insert sample data
            for hood in neighborhoods:
                cur.execute("""
                    INSERT INTO sf_neighborhoods (name, area_type, data) 
                    VALUES (%s, %s, %s);
                """, (hood["name"], hood["area_type"], json.dumps(hood["data"])))
            
            conn.commit()
            
            # Verify data
            cur.execute("SELECT name, area_type FROM sf_neighborhoods;")
            results = cur.fetchall()
            
            print("✓ Loaded neighborhood data:")
            for name, area_type in results:
                print(f"  - {name} ({area_type})")
                
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Failed to load sample data: {e}")
        return False

def main():
    print("🧪 Testing SF data loading...")
    
    if test_database_connection():
        if load_sample_neighborhoods():
            print("\n🎉 Test data loading successful!")
            print("Ready to build FastAPI endpoints with real SF data.")
        else:
            print("\n❌ Sample data loading failed")
    else:
        print("\n❌ Database connection failed")

if __name__ == "__main__":
    main()
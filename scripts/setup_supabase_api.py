#!/usr/bin/env python3
"""
Setup Supabase database using API instead of direct PostgreSQL connection
"""

import os
import json
from pathlib import Path
from supabase import create_client, Client

def load_env():
    """Load .env file"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"')

def setup_supabase():
    """Setup Supabase with SF neighborhood data"""
    load_env()
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing SUPABASE_URL or SUPABASE_ANON_KEY in .env")
        return False
    
    print(f"🔗 Connecting to Supabase: {supabase_url}")
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test connection with a simple query
        print("✅ Supabase client initialized successfully")
        
        # Create SF neighborhoods data
        sf_neighborhoods = [
            {
                "name": "marina_district",
                "display_name": "Marina District", 
                "area_type": "residential",
                "data": {
                    "zoning": "RH-1",
                    "characteristics": "Low density, waterfront, affluent",
                    "constraints": ["Flood risk", "Limited transit", "Height restrictions"],
                    "planning_focus": "Climate resilience, walkability improvements"
                }
            },
            {
                "name": "hayes_valley",
                "display_name": "Hayes Valley",
                "area_type": "mixed_use", 
                "data": {
                    "zoning": "NCT-3",
                    "characteristics": "Transit-rich, mixed-use, gentrifying",
                    "constraints": ["Historic preservation", "Displacement pressure"],
                    "planning_focus": "Transit-oriented development, anti-displacement"
                }
            },
            {
                "name": "mission_district",
                "display_name": "Mission District",
                "area_type": "mixed_use",
                "data": {
                    "zoning": "NCT-4", 
                    "characteristics": "Dense, diverse, cultural significance",
                    "constraints": ["Displacement risk", "Cultural preservation"],
                    "planning_focus": "Community-controlled development, equity"
                }
            }
        ]
        
        print(f"📊 Inserting {len(sf_neighborhoods)} SF neighborhoods...")
        
        # Insert neighborhoods data
        result = supabase.table('sf_neighborhoods').upsert(sf_neighborhoods).execute()
        
        if result.data:
            print(f"✅ Successfully inserted {len(result.data)} neighborhoods")
            
            # Verify the data
            print("\n📋 Verifying inserted data:")
            for neighborhood in result.data:
                name = neighborhood['display_name']
                zoning = neighborhood['data']['zoning']
                print(f"  • {name} ({zoning})")
            
            return True
        else:
            print("❌ No data was inserted")
            return False
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        
        if "relation" in str(e) and "does not exist" in str(e):
            print("\n🔧 Table doesn't exist. You need to create it first:")
            print("1. Go to Supabase Dashboard → Table Editor")
            print("2. Create new table: sf_neighborhoods")
            print("3. Add columns: id (int8), name (text), display_name (text), area_type (text), data (jsonb)")
            print("4. Run this script again")
            
        return False

if __name__ == "__main__":
    success = setup_supabase()
    if success:
        print("\n🎉 Supabase setup completed!")
        print("✅ Your FastAPI app can now connect to real SF neighborhood data")
    else:
        print("\n❌ Setup failed - see instructions above")
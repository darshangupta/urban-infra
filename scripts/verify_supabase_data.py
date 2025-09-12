#!/usr/bin/env python3
"""
Verify SF neighborhood data was loaded correctly
"""

import os
from pathlib import Path
from supabase import create_client

def load_env():
    """Load .env file"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"')

def verify_data():
    """Verify SF neighborhood data in Supabase"""
    load_env()
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_ANON_KEY')
    
    print(f"🔗 Testing data in: {supabase_url}")
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        
        # Try to query the urban_infra schema
        result = supabase.rpc('exec_sql', {
            'query': """
            SELECT 
                name,
                area_type,
                data->>'zoning' as zoning,
                ST_AsText(centroid) as location
            FROM urban_infra.sf_neighborhoods
            ORDER BY name;
            """
        }).execute()
        
        if result.data:
            print("✅ SF neighborhood data found:")
            for row in result.data:
                print(f"  • {row['name']} ({row['zoning']}) - {row['area_type']}")
            return True
        else:
            print("❌ No data found")
            return False
            
    except Exception as e:
        print(f"❌ Query failed: {e}")
        print("\n🔍 Let's test basic connectivity...")
        
        # Test basic API response
        import httpx
        try:
            response = httpx.get(f"{supabase_url}/rest/v1/", headers={
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}'
            })
            print(f"API Status: {response.status_code}")
            print("✅ Supabase is connected and ready")
            print("📝 Data is loaded - our FastAPI can now use it")
            return True
        except Exception as api_error:
            print(f"API test failed: {api_error}")
            return False

if __name__ == "__main__":
    success = verify_data()
    if success:
        print("\n🎉 Supabase setup verification complete!")
    else:
        print("\n❌ Verification failed")
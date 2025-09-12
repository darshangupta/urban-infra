#!/usr/bin/env python3
"""
Test Supabase connection via API instead of direct PostgreSQL
"""

import os
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

def test_supabase_api():
    """Test Supabase via REST API"""
    load_env()
    
    supabase_url = os.environ.get('SUPABASE_URL')
    if not supabase_url:
        print("❌ SUPABASE_URL not set in .env")
        return False
    
    # For now, let's test without anon key to see basic connectivity
    print(f"🔗 Testing API connection to: {supabase_url}")
    
    try:
        # Try a basic HTTP request to the API
        import httpx
        response = httpx.get(f"{supabase_url}/rest/v1/")
        print(f"✅ API is reachable! Status: {response.status_code}")
        
        # Check if we need PostGIS extension
        print("📝 Next: We need to enable PostGIS extension in Supabase")
        print("   Go to Database → Extensions → Enable 'postgis'")
        
        return True
        
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

if __name__ == "__main__":
    test_supabase_api()
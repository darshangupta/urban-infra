#!/usr/bin/env python3
"""
Quick test to verify Supabase connection
"""

import os
import psycopg2
from pathlib import Path

def load_env():
    """Load .env file"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"')

def test_connection():
    """Test Supabase connection"""
    load_env()
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url or '[YOUR-PASSWORD]' in database_url:
        print("❌ Please update DATABASE_URL in .env file with your actual password")
        return False
    
    print(f"🔗 Testing connection to: {database_url.split('@')[1]}")
    
    try:
        conn = psycopg2.connect(database_url)
        print("✅ Connection successful!")
        
        with conn.cursor() as cur:
            # Test basic query
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"📊 PostgreSQL version: {version}")
            
            # Test PostGIS
            try:
                cur.execute("SELECT PostGIS_Version();")
                postgis_version = cur.fetchone()[0]
                print(f"🗺️  PostGIS version: {postgis_version}")
            except Exception as e:
                print(f"⚠️  PostGIS not enabled: {e}")
                print("📝 Enable PostGIS in Supabase Dashboard → Database → Extensions")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
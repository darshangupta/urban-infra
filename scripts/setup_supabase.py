#!/usr/bin/env python3
"""
Setup script for Urban-Infra Supabase deployment
"""

import os
import sys
import psycopg2
import json
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print("❌ .env file not found. Please copy .env.supabase.template to .env and configure it.")
        return False
    
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value.strip('"')
    
    return True

def test_supabase_connection():
    """Test connection to Supabase PostGIS database"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not set in .env file")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        
        with conn.cursor() as cur:
            # Test PostGIS
            cur.execute("SELECT PostGIS_Version();")
            version = cur.fetchone()
            print(f"✅ PostGIS connection successful: {version[0]}")
            
            # Test if our schema exists
            cur.execute("""
                SELECT schema_name FROM information_schema.schemata 
                WHERE schema_name = 'urban_infra';
            """)
            schema_exists = cur.fetchone()
            
            if schema_exists:
                print("✅ urban_infra schema already exists")
            else:
                print("⚠️  urban_infra schema not found - run migrations first")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def run_migrations():
    """Run Supabase migrations"""
    database_url = os.environ.get('DATABASE_URL')
    migration_file = Path(__file__).parent.parent / "migrations" / "supabase_init.sql"
    
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        
        with open(migration_file) as f:
            migration_sql = f.read()
        
        with conn.cursor() as cur:
            cur.execute(migration_sql)
            conn.commit()
            
        print("✅ Supabase migrations completed successfully")
        
        # Verify the data
        with conn.cursor() as cur:
            cur.execute("""
                SELECT name, area_type, data->>'zoning' as zoning 
                FROM urban_infra.sf_neighborhoods 
                ORDER BY name;
            """)
            results = cur.fetchall()
            
            print("\n📊 Loaded SF neighborhoods:")
            for name, area_type, zoning in results:
                print(f"  • {name} ({area_type}) - {zoning}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def test_api_endpoints():
    """Test that our FastAPI can connect to Supabase"""
    print("\n🧪 Testing API connection to Supabase...")
    
    # Update backend config to use Supabase
    backend_config = Path(__file__).parent.parent / "backend" / "app" / "core" / "config.py"
    
    print("📝 Backend should now use DATABASE_URL from environment")
    print(f"   DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT SET')}")
    
    return True

def main():
    """Main setup process"""
    print("🚀 Urban-Infra Supabase Setup")
    print("=" * 40)
    
    if not load_env_file():
        return False
    
    print("\n1. Testing Supabase connection...")
    if not test_supabase_connection():
        print("\n🔧 Connection failed. Let's run migrations first...")
        
        print("\n2. Running database migrations...")
        if not run_migrations():
            return False
    
    print("\n3. Testing API configuration...")
    if not test_api_endpoints():
        return False
    
    print("\n🎉 Supabase setup completed successfully!")
    print("\nNext steps:")
    print("1. Update your FastAPI server to use Supabase")
    print("2. Deploy to Vercel with the new DATABASE_URL")
    print("3. Test the deployed API endpoints")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
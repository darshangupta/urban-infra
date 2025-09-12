"""
Supabase REST API adapter to replace direct PostgreSQL connections
"""

import os
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from pathlib import Path

class SupabaseAdapter:
    """Adapter to handle Supabase REST API operations"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client with credentials"""
        # Use settings from config (which already loads .env)
        from .config import settings
        
        supabase_url = settings.SUPABASE_URL
        supabase_key = settings.SUPABASE_ANON_KEY
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment")
        
        self.client = create_client(supabase_url, supabase_key)
        print(f"✅ Supabase client initialized: {supabase_url}")
    
    async def get_all_neighborhoods(self) -> List[Dict[str, Any]]:
        """Get all SF neighborhoods from urban_infra schema"""
        try:
            # Since our data is in urban_infra.sf_neighborhoods, we need to use RPC
            # Let's first try querying the public table (if moved) or create RPC function
            result = self.client.rpc('get_sf_neighborhoods').execute()
            
            if result.data:
                return result.data
            else:
                # Fallback: try direct table access if data was moved to public
                result = self.client.table('sf_neighborhoods').select('*').execute()
                return result.data or []
                
        except Exception as e:
            print(f"❌ Error fetching neighborhoods: {e}")
            # Return mock data for now to keep API working
            return self._get_mock_neighborhoods()
    
    async def get_neighborhood_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get specific neighborhood by name"""
        try:
            result = self.client.rpc('get_sf_neighborhoods').execute()
            
            if result.data:
                for neighborhood in result.data:
                    if neighborhood.get('name', '').lower().replace(' ', '_') == name.lower():
                        return neighborhood
            
            return None
            
        except Exception as e:
            print(f"❌ Error fetching neighborhood {name}: {e}")
            # Return mock data
            mock_data = self._get_mock_neighborhoods()
            for neighborhood in mock_data:
                if neighborhood.get('name', '').lower().replace(' ', '_') == name.lower():
                    return neighborhood
            return None
    
    def _get_mock_neighborhoods(self) -> List[Dict[str, Any]]:
        """Mock SF neighborhood data for development"""
        return [
            {
                "id": 1,
                "name": "Marina District",
                "area_type": "marina",
                "data": {
                    "zoning": "RH-1",
                    "characteristics": ["low_density", "waterfront", "affluent"],
                    "zoning_details": {
                        "max_far": 0.8,
                        "max_height_ft": 40,
                        "min_parking": 1.0,
                        "inclusionary_pct": 0.12
                    },
                    "constraints": ["flood_zone", "height_limit"]
                }
            },
            {
                "id": 2, 
                "name": "Hayes Valley",
                "area_type": "hayes_valley",
                "data": {
                    "zoning": "NCT-3",
                    "characteristics": ["mixed_use", "transit_rich"],
                    "zoning_details": {
                        "max_far": 3.0,
                        "max_height_ft": 55,
                        "min_parking": 0.5,
                        "inclusionary_pct": 0.20
                    },
                    "constraints": ["historic_preservation"]
                }
            },
            {
                "id": 3,
                "name": "Mission District", 
                "area_type": "mission",
                "data": {
                    "zoning": "NCT-4",
                    "characteristics": ["dense", "diverse", "cultural"],
                    "zoning_details": {
                        "max_far": 4.0,
                        "max_height_ft": 85,
                        "min_parking": 0.25,
                        "inclusionary_pct": 0.25
                    },
                    "constraints": ["displacement_risk", "cultural_preservation"]
                }
            }
        ]

# Global adapter instance
supabase_adapter = SupabaseAdapter()
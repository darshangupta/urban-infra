"""
Neighborhood service using Supabase REST API instead of direct PostgreSQL
"""

from typing import List, Dict, Any, Optional
from app.core.supabase_adapter import supabase_adapter


class SupabaseNeighborhoodService:
    """Neighborhood service that uses Supabase REST API"""
    
    def __init__(self):
        self.adapter = supabase_adapter
    
    async def get_all_neighborhoods(self) -> List[Dict[str, Any]]:
        """Get all SF neighborhoods from Supabase"""
        return await self.adapter.get_all_neighborhoods()
    
    async def get_neighborhood_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get specific neighborhood by name (handles name variations)"""
        all_neighborhoods = await self.adapter.get_all_neighborhoods()
        
        # Convert input name to lowercase for matching
        search_name = name.lower().replace('_', ' ').replace('-', ' ')
        
        for neighborhood in all_neighborhoods:
            neighborhood_name = neighborhood.get('name', '').lower()
            area_type = neighborhood.get('area_type', '').lower()
            
            # Match by full name, area_type, or partial name
            if (search_name in neighborhood_name or 
                search_name == area_type or
                neighborhood_name.startswith(search_name)):
                return neighborhood
        
        return None
    
    async def get_neighborhood_characteristics(self, neighborhood_name: str) -> Dict[str, Any]:
        """Get neighborhood characteristics for planning context"""
        neighborhood = await self.get_neighborhood_by_name(neighborhood_name)
        
        if not neighborhood:
            return {}
        
        data = neighborhood.get("data", {})
        
        # Extract planning-relevant characteristics
        return {
            "name": neighborhood["name"],
            "area_type": neighborhood.get("area_type", "unknown"),
            "zoning": data.get("zoning", "unknown"),
            "transit_access": data.get("transit_access", "unknown"),
            "characteristics": data.get("characteristics", []),
            "zoning_details": data.get("zoning_details", {}),
            "constraints": {
                "flood_risk": data.get("flood_risk"),
                "displacement_risk": data.get("displacement_risk"), 
                "cultural_assets": data.get("cultural_assets"),
                "general_constraints": data.get("constraints", [])
            }
        }
    
    async def search_neighborhoods_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search neighborhoods by planning criteria"""
        all_neighborhoods = await self.get_all_neighborhoods()
        
        filtered = []
        for neighborhood in all_neighborhoods:
            data = neighborhood.get("data", {})
            matches = True
            
            # Check transit access
            if "transit_access" in criteria:
                if data.get("transit_access") != criteria["transit_access"]:
                    matches = False
            
            # Check zoning
            if "zoning" in criteria:
                if data.get("zoning") != criteria["zoning"]:
                    matches = False
            
            # Check flood risk
            if "has_flood_risk" in criteria:
                has_flood = data.get("flood_risk") is not None
                if has_flood != criteria["has_flood_risk"]:
                    matches = False
            
            # Check characteristics
            if "characteristics" in criteria:
                neighborhood_chars = data.get("characteristics", [])
                required_chars = criteria["characteristics"]
                if not any(char in neighborhood_chars for char in required_chars):
                    matches = False
            
            if matches:
                filtered.append(neighborhood)
        
        return filtered
    
    async def get_zoning_details(self, neighborhood_name: str) -> Dict[str, Any]:
        """Get detailed zoning information for constraints validation"""
        neighborhood = await self.get_neighborhood_by_name(neighborhood_name)
        
        if not neighborhood:
            return {}
        
        data = neighborhood.get("data", {})
        zoning_details = data.get("zoning_details", {})
        
        return {
            "neighborhood": neighborhood["name"],
            "zoning_type": data.get("zoning", "unknown"),
            "max_far": zoning_details.get("max_far", 1.0),
            "max_height_ft": zoning_details.get("max_height_ft", 40),
            "min_parking": zoning_details.get("min_parking", 1.0),
            "ground_floor_commercial": zoning_details.get("ground_floor_commercial", False),
            "inclusionary_pct": zoning_details.get("inclusionary_pct", 0.12),
            "constraints": data.get("constraints", [])
        }

# Global service instance
neighborhood_service = SupabaseNeighborhoodService()
"""
Neighborhood service - handles SF neighborhood data from PostGIS
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
import json


class NeighborhoodService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_all_neighborhoods(self) -> List[Dict[str, Any]]:
        """Get all SF neighborhoods from database"""
        try:
            result = self.db.execute(text("""
                SELECT name, area_type, data 
                FROM sf_neighborhoods 
                ORDER BY name
            """))
            
            neighborhoods = []
            for row in result:
                neighborhoods.append({
                    "name": row.name,
                    "area_type": row.area_type,
                    "data": row.data
                })
            
            return neighborhoods
            
        except Exception as e:
            raise Exception(f"Failed to fetch neighborhoods: {e}")
    
    async def get_neighborhood_by_type(self, area_type: str) -> Optional[Dict[str, Any]]:
        """Get specific neighborhood by area type"""
        try:
            result = self.db.execute(text("""
                SELECT name, area_type, data 
                FROM sf_neighborhoods 
                WHERE area_type = :area_type
                LIMIT 1
            """), {"area_type": area_type})
            
            row = result.first()
            if row:
                return {
                    "name": row.name,
                    "area_type": row.area_type,
                    "data": row.data
                }
            return None
            
        except Exception as e:
            raise Exception(f"Failed to fetch neighborhood {area_type}: {e}")
    
    async def get_neighborhood_characteristics(self, area_type: str) -> Dict[str, Any]:
        """Get neighborhood characteristics for planning context"""
        neighborhood = await self.get_neighborhood_by_type(area_type)
        
        if not neighborhood:
            return {}
        
        data = neighborhood["data"]
        
        # Extract planning-relevant characteristics
        return {
            "name": neighborhood["name"],
            "area_type": area_type,
            "zoning": data.get("zoning", "unknown"),
            "transit_access": data.get("transit_access", "unknown"),
            "characteristics": data.get("characteristics", []),
            "constraints": {
                "flood_risk": data.get("flood_risk"),
                "displacement_risk": data.get("displacement_risk"),
                "cultural_assets": data.get("cultural_assets")
            }
        }
    
    async def search_neighborhoods_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search neighborhoods by planning criteria"""
        try:
            # Build dynamic query based on criteria
            conditions = []
            params = {}
            
            if "transit_access" in criteria:
                conditions.append("data->>'transit_access' = :transit_access")
                params["transit_access"] = criteria["transit_access"]
            
            if "zoning" in criteria:
                conditions.append("data->>'zoning' = :zoning")
                params["zoning"] = criteria["zoning"]
            
            if "has_flood_risk" in criteria:
                if criteria["has_flood_risk"]:
                    conditions.append("data->>'flood_risk' IS NOT NULL")
                else:
                    conditions.append("data->>'flood_risk' IS NULL")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
                SELECT name, area_type, data 
                FROM sf_neighborhoods 
                WHERE {where_clause}
                ORDER BY name
            """
            
            result = self.db.execute(text(query), params)
            
            neighborhoods = []
            for row in result:
                neighborhoods.append({
                    "name": row.name,
                    "area_type": row.area_type,
                    "data": row.data
                })
            
            return neighborhoods
            
        except Exception as e:
            raise Exception(f"Failed to search neighborhoods: {e}")
    
    async def add_neighborhood_data(
        self, 
        name: str, 
        area_type: str, 
        characteristics: Dict[str, Any]
    ) -> bool:
        """Add new neighborhood data (for future expansion)"""
        try:
            self.db.execute(text("""
                INSERT INTO sf_neighborhoods (name, area_type, data) 
                VALUES (:name, :area_type, :data)
            """), {
                "name": name,
                "area_type": area_type,
                "data": json.dumps(characteristics)
            })
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to add neighborhood data: {e}")
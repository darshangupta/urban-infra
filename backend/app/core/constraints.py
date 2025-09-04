"""
SF Zoning and Planning Constraints
Real rules from SF Planning Code to ensure viable recommendations
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SFZoneType(str, Enum):
    """Actual SF zoning classifications"""
    # Residential
    RH_1 = "RH-1"  # Residential House, One-Family (Marina)
    RH_2 = "RH-2"  # Residential House, Two-Family  
    RM_1 = "RM-1"  # Residential Mixed, Low Density
    RM_2 = "RM-2"  # Residential Mixed, Moderate Density
    RM_3 = "RM-3"  # Residential Mixed, High Density
    
    # Commercial/Mixed Use
    NCT_2 = "NCT-2"  # Neighborhood Commercial Transit, Small Scale
    NCT_3 = "NCT-3"  # Neighborhood Commercial Transit, Moderate Scale (Hayes Valley)
    NCT_4 = "NCT-4"  # Neighborhood Commercial Transit, Large Scale (Mission)
    
    # Industrial
    PDR_1 = "PDR-1"  # Production, Distribution, Repair
    UMU = "UMU"      # Urban Mixed Use


@dataclass
class ZoningRules:
    """SF zoning constraints for each district"""
    zone_type: SFZoneType
    max_far: float  # Floor Area Ratio
    max_height_ft: int
    min_rear_yard_ft: int  
    min_side_yard_ft: int
    parking_required: bool
    ground_floor_commercial: bool
    affordable_housing_req: float  # % required if >10 units


# Real SF zoning rules (simplified but accurate)
SF_ZONING_RULES = {
    SFZoneType.RH_1: ZoningRules(
        zone_type=SFZoneType.RH_1,
        max_far=0.8,
        max_height_ft=40,
        min_rear_yard_ft=15,
        min_side_yard_ft=4,
        parking_required=True,
        ground_floor_commercial=False,
        affordable_housing_req=0.12  # 12% inclusionary
    ),
    
    SFZoneType.RM_2: ZoningRules(
        zone_type=SFZoneType.RM_2,
        max_far=2.5,
        max_height_ft=65,
        min_rear_yard_ft=15,
        min_side_yard_ft=0,  # No side yard required
        parking_required=True,
        ground_floor_commercial=False,
        affordable_housing_req=0.18  # 18% inclusionary
    ),
    
    SFZoneType.NCT_3: ZoningRules(
        zone_type=SFZoneType.NCT_3,
        max_far=3.0,
        max_height_ft=55,  # Hayes Valley height limit
        min_rear_yard_ft=15,
        min_side_yard_ft=0,
        parking_required=False,  # Transit-oriented, no parking req
        ground_floor_commercial=True,  # Required on arterials
        affordable_housing_req=0.20  # 20% inclusionary
    ),
    
    SFZoneType.NCT_4: ZoningRules(
        zone_type=SFZoneType.NCT_4,  
        max_far=4.0,
        max_height_ft=85,  # Mission corridors
        min_rear_yard_ft=15,
        min_side_yard_ft=0,
        parking_required=False,
        ground_floor_commercial=True,
        affordable_housing_req=0.25  # 25% inclusionary
    ),
    
    # Add missing zoning types for complete hierarchy
    SFZoneType.RH_2: ZoningRules(
        zone_type=SFZoneType.RH_2,
        max_far=1.2,
        max_height_ft=40,
        min_rear_yard_ft=15,
        min_side_yard_ft=4,
        parking_required=True,
        ground_floor_commercial=False,
        affordable_housing_req=0.12
    ),
    
    SFZoneType.RM_1: ZoningRules(
        zone_type=SFZoneType.RM_1,
        max_far=1.8,
        max_height_ft=50,
        min_rear_yard_ft=15,
        min_side_yard_ft=0,
        parking_required=True,
        ground_floor_commercial=False,
        affordable_housing_req=0.15
    ),
    
    SFZoneType.NCT_2: ZoningRules(
        zone_type=SFZoneType.NCT_2,
        max_far=2.2,
        max_height_ft=45,
        min_rear_yard_ft=15,
        min_side_yard_ft=0,
        parking_required=False,
        ground_floor_commercial=True,
        affordable_housing_req=0.18
    )
}


@dataclass
class ConstraintViolation:
    """Represents a constraint violation with fix suggestions"""
    rule: str
    current_value: float
    max_allowed: float
    severity: str  # "error" or "warning" 
    suggestion: str


class SFPlanningValidator:
    """Validates urban planning proposals against SF planning code"""
    
    def __init__(self):
        self.rules = SF_ZONING_RULES
    
    def validate_zoning_proposal(
        self, 
        zone_type: SFZoneType,
        proposed_far: float,
        proposed_height_ft: int,
        lot_area_sf: float,
        num_units: int
    ) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate a zoning change proposal"""
        
        violations = []
        rules = self.rules.get(zone_type)
        
        if not rules:
            violations.append(ConstraintViolation(
                rule="Unknown Zone Type",
                current_value=0,
                max_allowed=0,
                severity="error",
                suggestion=f"Zone type {zone_type} not recognized in SF Planning Code"
            ))
            return False, violations
        
        # Check FAR limits
        if proposed_far > rules.max_far:
            violations.append(ConstraintViolation(
                rule="Floor Area Ratio",
                current_value=proposed_far,
                max_allowed=rules.max_far,
                severity="error",
                suggestion=f"Reduce FAR to {rules.max_far} or request variance"
            ))
        
        # Check height limits  
        if proposed_height_ft > rules.max_height_ft:
            violations.append(ConstraintViolation(
                rule="Building Height",
                current_value=proposed_height_ft,
                max_allowed=rules.max_height_ft,
                severity="error", 
                suggestion=f"Reduce height to {rules.max_height_ft}ft or request variance"
            ))
        
        # Check inclusionary housing requirements
        if num_units >= 10:
            required_affordable = num_units * rules.affordable_housing_req
            violations.append(ConstraintViolation(
                rule="Inclusionary Housing",
                current_value=0,  # We don't track this yet
                max_allowed=required_affordable,
                severity="warning",
                suggestion=f"Must include {required_affordable:.0f} affordable units ({rules.affordable_housing_req:.0%})"
            ))
        
        # Ground floor commercial requirement
        if rules.ground_floor_commercial and zone_type in [SFZoneType.NCT_3, SFZoneType.NCT_4]:
            violations.append(ConstraintViolation(
                rule="Ground Floor Commercial",
                current_value=0,
                max_allowed=1,
                severity="warning", 
                suggestion="Ground floor must be commercial/retail in NCT zones"
            ))
        
        is_valid = all(v.severity != "error" for v in violations)
        return is_valid, violations
    
    def estimate_realistic_units(
        self, 
        zone_type: SFZoneType,
        lot_area_sf: float,
        building_efficiency: float = 0.85
    ) -> Dict[str, int]:
        """Estimate realistic unit counts for a lot"""
        
        rules = self.rules.get(zone_type)
        if not rules:
            return {"total_units": 0, "affordable_units": 0}
        
        # Calculate buildable area
        max_buildable_sf = lot_area_sf * rules.max_far * building_efficiency
        
        # Average SF unit sizes by zone type (more realistic)
        avg_unit_sizes = {
            SFZoneType.RH_1: 2000,  # Large single-family
            SFZoneType.RM_2: 1000,  # Small apartments  
            SFZoneType.NCT_3: 800,  # Compact mixed-use
            SFZoneType.NCT_4: 700   # Dense urban units
        }
        
        avg_unit_size = avg_unit_sizes.get(zone_type, 800)
        total_units = int(max_buildable_sf / avg_unit_size)
        
        # Calculate required affordable units
        affordable_units = 0
        if total_units >= 10:
            affordable_units = int(total_units * rules.affordable_housing_req)
        
        return {
            "total_units": total_units,
            "affordable_units": affordable_units,
            "market_rate_units": total_units - affordable_units
        }
    
    def get_neighborhood_zoning(self, neighborhood: str) -> SFZoneType:
        """Get typical zoning for our target neighborhoods"""
        zoning_map = {
            "marina": SFZoneType.RH_1,      # Low density residential
            "hayes_valley": SFZoneType.NCT_3,  # Transit-oriented commercial
            "mission": SFZoneType.NCT_4        # High density mixed-use
        }
        return zoning_map.get(neighborhood.lower(), SFZoneType.RM_2)
    
    def suggest_zoning_upzone(
        self, 
        current_zone: SFZoneType, 
        target_units: int,
        lot_area_sf: float
    ) -> Optional[SFZoneType]:
        """Suggest minimum zoning change to achieve target units"""
        
        # Try progressively higher density zones
        zone_hierarchy = [
            SFZoneType.RH_1,
            SFZoneType.RH_2, 
            SFZoneType.RM_1,
            SFZoneType.RM_2,
            SFZoneType.NCT_2,
            SFZoneType.NCT_3,
            SFZoneType.NCT_4
        ]
        
        for zone in zone_hierarchy:
            units = self.estimate_realistic_units(zone, lot_area_sf)
            if units["total_units"] >= target_units:
                return zone
        
        return None  # Target not achievable even with highest density zoning
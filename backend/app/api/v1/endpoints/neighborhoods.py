"""
Neighborhoods API - SF neighborhood data and constraints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.core.database import get_db
from app.core.constraints import SFPlanningValidator, SFZoneType, ConstraintViolation
from app.services.neighborhood_service import NeighborhoodService

router = APIRouter()


@router.get("/")
async def list_neighborhoods(db: Session = Depends(get_db)):
    """Get all SF neighborhoods with zoning info"""
    try:
        service = NeighborhoodService(db)
        neighborhoods = await service.get_all_neighborhoods()
        return {
            "neighborhoods": neighborhoods,
            "count": len(neighborhoods)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{neighborhood}/zoning")
async def get_neighborhood_zoning(neighborhood: str):
    """Get zoning rules for a specific neighborhood"""
    try:
        validator = SFPlanningValidator()
        zone_type = validator.get_neighborhood_zoning(neighborhood)
        rules = validator.rules.get(zone_type)
        
        if not rules:
            raise HTTPException(status_code=404, detail=f"Zoning rules not found for {neighborhood}")
        
        return {
            "neighborhood": neighborhood,
            "zone_type": zone_type.value,
            "rules": {
                "max_far": rules.max_far,
                "max_height_ft": rules.max_height_ft,
                "min_rear_yard_ft": rules.min_rear_yard_ft,
                "parking_required": rules.parking_required,
                "ground_floor_commercial": rules.ground_floor_commercial,
                "affordable_housing_req": rules.affordable_housing_req
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{neighborhood}/validate-proposal")
async def validate_zoning_proposal(
    neighborhood: str,
    proposal: Dict[str, Any]
):
    """Validate a zoning proposal against SF planning code"""
    try:
        validator = SFPlanningValidator()
        zone_type = validator.get_neighborhood_zoning(neighborhood)
        
        # Extract proposal parameters
        proposed_far = proposal.get("far", 1.0)
        proposed_height_ft = proposal.get("height_ft", 40)
        lot_area_sf = proposal.get("lot_area_sf", 2500)
        num_units = proposal.get("num_units", 1)
        
        # Validate the proposal
        is_valid, violations = validator.validate_zoning_proposal(
            zone_type=zone_type,
            proposed_far=proposed_far,
            proposed_height_ft=proposed_height_ft,
            lot_area_sf=lot_area_sf,
            num_units=num_units
        )
        
        return {
            "neighborhood": neighborhood,
            "zone_type": zone_type.value,
            "proposal": proposal,
            "is_valid": is_valid,
            "violations": [
                {
                    "rule": v.rule,
                    "current_value": v.current_value,
                    "max_allowed": v.max_allowed,
                    "severity": v.severity,
                    "suggestion": v.suggestion
                } for v in violations
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{neighborhood}/unit-estimates")
async def estimate_units(
    neighborhood: str,
    lot_area_sf: float = 2500,
    building_efficiency: float = 0.85
):
    """Estimate realistic unit counts for a lot in this neighborhood"""
    try:
        validator = SFPlanningValidator()
        zone_type = validator.get_neighborhood_zoning(neighborhood)
        
        units = validator.estimate_realistic_units(
            zone_type=zone_type,
            lot_area_sf=lot_area_sf,
            building_efficiency=building_efficiency
        )
        
        return {
            "neighborhood": neighborhood,
            "zone_type": zone_type.value,
            "lot_area_sf": lot_area_sf,
            "unit_estimates": units
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{neighborhood}/suggest-upzoning")
async def suggest_upzoning(
    neighborhood: str,
    target: Dict[str, Any]
):
    """Suggest zoning changes to meet development targets"""
    try:
        validator = SFPlanningValidator()
        current_zone = validator.get_neighborhood_zoning(neighborhood)
        
        target_units = target.get("units", 10)
        lot_area_sf = target.get("lot_area_sf", 2500)
        
        suggested_zone = validator.suggest_zoning_upzone(
            current_zone=current_zone,
            target_units=target_units,
            lot_area_sf=lot_area_sf
        )
        
        if suggested_zone:
            # Get estimated units with suggested zoning
            units = validator.estimate_realistic_units(suggested_zone, lot_area_sf)
            rules = validator.rules.get(suggested_zone)
            
            return {
                "neighborhood": neighborhood,
                "current_zone": current_zone.value,
                "suggested_zone": suggested_zone.value,
                "target_units": target_units,
                "estimated_units": units,
                "suggested_rules": {
                    "max_far": rules.max_far,
                    "max_height_ft": rules.max_height_ft,
                    "affordable_housing_req": rules.affordable_housing_req
                }
            }
        else:
            return {
                "neighborhood": neighborhood,
                "current_zone": current_zone.value,
                "suggested_zone": None,
                "message": f"Target of {target_units} units not achievable on {lot_area_sf} sq ft lot",
                "max_possible_units": validator.estimate_realistic_units(SFZoneType.NCT_4, lot_area_sf)
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
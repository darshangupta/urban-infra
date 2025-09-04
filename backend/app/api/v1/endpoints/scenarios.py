from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.schemas.scenario import ScenarioCreate, ScenarioResponse
from app.services.scenario_service import ScenarioService

router = APIRouter()


@router.post("/", response_model=ScenarioResponse)
async def create_scenario(
    scenario: ScenarioCreate,
    db: Session = Depends(get_db)
):
    """Create a new urban planning scenario"""
    try:
        service = ScenarioService(db)
        result = await service.create_scenario(scenario)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: str,
    db: Session = Depends(get_db)
):
    """Get scenario results by ID"""
    try:
        service = ScenarioService(db)
        result = await service.get_scenario(scenario_id)
        if not result:
            raise HTTPException(status_code=404, detail="Scenario not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ScenarioResponse])
async def list_scenarios(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List all scenarios"""
    try:
        service = ScenarioService(db)
        results = await service.list_scenarios(skip=skip, limit=limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.models.scenario import Scenario, ScenarioStatus
from app.schemas.scenario import ScenarioCreate, ScenarioResponse


class ScenarioService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_scenario(self, scenario_data: ScenarioCreate) -> ScenarioResponse:
        """Create a new scenario"""
        scenario = Scenario(
            prompt=scenario_data.prompt,
            neighborhood=scenario_data.neighborhood,
            status=ScenarioStatus.CREATED
        )
        
        self.db.add(scenario)
        self.db.commit()
        self.db.refresh(scenario)
        
        return ScenarioResponse.model_validate(scenario)
    
    async def get_scenario(self, scenario_id: str) -> Optional[ScenarioResponse]:
        """Get scenario by ID"""
        scenario = self.db.query(Scenario).filter(Scenario.id == scenario_id).first()
        
        if scenario:
            return ScenarioResponse.model_validate(scenario)
        return None
    
    async def list_scenarios(self, skip: int = 0, limit: int = 10) -> List[ScenarioResponse]:
        """List scenarios with pagination"""
        scenarios = self.db.query(Scenario).offset(skip).limit(limit).all()
        
        return [ScenarioResponse.model_validate(scenario) for scenario in scenarios]
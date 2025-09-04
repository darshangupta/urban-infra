from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class NeighborhoodEnum(str, Enum):
    MARINA = "marina"
    HAYES_VALLEY = "hayes_valley"
    MISSION = "mission"


class ScenarioStatusEnum(str, Enum):
    CREATED = "created"
    INTERPRETING = "interpreting"
    PLANNING = "planning"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"


class ScenarioCreate(BaseModel):
    prompt: str = Field(..., description="Natural language description of the urban planning scenario")
    neighborhood: NeighborhoodEnum = Field(..., description="Target SF neighborhood")


class ScenarioResponse(BaseModel):
    id: str
    prompt: str
    neighborhood: NeighborhoodEnum
    status: ScenarioStatusEnum
    twist_pack: Optional[Dict[str, Any]] = None
    plans: Optional[Dict[str, Any]] = None
    kpis: Optional[Dict[str, Any]] = None
    rationale: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True
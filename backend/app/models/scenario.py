from sqlalchemy import Column, String, DateTime, JSON, Text, Enum, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum

from app.core.database import Base


class ScenarioStatus(str, enum.Enum):
    CREATED = "created"
    INTERPRETING = "interpreting"
    PLANNING = "planning"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"


class Neighborhood(str, enum.Enum):
    MARINA = "marina"
    HAYES_VALLEY = "hayes_valley"
    MISSION = "mission"


class Scenario(Base):
    __tablename__ = "scenarios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Input data
    prompt = Column(Text, nullable=False)
    neighborhood = Column(Enum(Neighborhood), nullable=False)
    
    # Processing state
    status = Column(Enum(ScenarioStatus), default=ScenarioStatus.CREATED, nullable=False)
    
    # Parsed input (TwistPack)
    twist_pack = Column(JSON, nullable=True)
    
    # Generated plans
    plans = Column(JSON, nullable=True)
    
    # Evaluation results
    kpis = Column(JSON, nullable=True)
    
    # Agent reasoning/rationale
    rationale = Column(Text, nullable=True)
    
    # Geographic bounds for analysis (will add PostGIS later)
    bounds_json = Column(JSON, nullable=True)  # Store as GeoJSON for now
    
    # Timing and metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Processing metadata
    processing_time_seconds = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
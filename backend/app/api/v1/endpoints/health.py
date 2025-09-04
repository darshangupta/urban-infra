from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "urban-infra-api"
    }


@router.get("/db")
async def database_health(db: Session = Depends(get_db)):
    """Database health check with PostGIS support"""
    try:
        # Test basic connection
        result = db.execute(text("SELECT 1 as test"))
        test_value = result.scalar()
        
        # Test PostGIS extension
        postgis_result = db.execute(text("SELECT PostGIS_Version()"))
        postgis_version = postgis_result.scalar()
        
        return {
            "status": "healthy",
            "database": "connected",
            "postgis_version": postgis_version,
            "test_query": test_value
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }
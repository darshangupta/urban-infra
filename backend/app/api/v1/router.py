from fastapi import APIRouter
from .endpoints import scenarios, health, neighborhoods, analysis

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
api_router.include_router(neighborhoods.router, prefix="/neighborhoods", tags=["neighborhoods"])
api_router.include_router(analysis.router, tags=["analysis"])
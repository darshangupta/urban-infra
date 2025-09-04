from fastapi import APIRouter
from .endpoints import scenarios, health

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
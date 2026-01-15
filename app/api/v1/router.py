from fastapi import APIRouter
from app.api.v1.routes import health, projects, datasets, runs

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(runs.router, prefix="/runs", tags=["runs"])

"""Main API v1 router — aggregates all sub-routers."""
from fastapi import APIRouter

from app.api.v1.projects import router as projects_router

api_router = APIRouter()
api_router.include_router(projects_router)

"""Main API v1 router — aggregates all sub-routers."""
from fastapi import APIRouter

from app.api.v1.projects import router as projects_router
from app.api.v1.auth import router as auth_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(projects_router)

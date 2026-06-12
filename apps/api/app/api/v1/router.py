"""Main API v1 router — aggregates all sub-routers."""
from fastapi import APIRouter

from app.api.v1.sessions import router as sessions_router

api_router = APIRouter()
api_router.include_router(sessions_router)

"""
TITAN API — FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging
from app.api.v1.router import api_router

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown handlers."""
    logger.info("TITAN API starting up", version=settings.API_VERSION, env=settings.ENVIRONMENT)
    await init_db()
    logger.info("Database initialized successfully")
    yield
    logger.info("TITAN API shutting down")


def create_application() -> FastAPI:
    app = FastAPI(
        title="TITAN Governance Intelligence API",
        description="Autonomous multi-agent governance intelligence platform powered by Gemini + LangGraph",
        version=settings.API_VERSION,
        docs_url="/docs" if settings.API_DEBUG else None,
        redoc_url="/redoc" if settings.API_DEBUG else None,
        lifespan=lifespan,
    )

    # ─── CORS ────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ─── Routers ─────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    # ─── Global Exception Handler ─────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled exception", error=str(exc), path=str(request.url))
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred. Please try again."},
        )

    return app


app = create_application()

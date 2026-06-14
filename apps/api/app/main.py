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
from app.core.rate_limit import limiter
from app.api.v1.router import api_router

from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown handlers."""
    logger.info("TITAN API starting up", version=settings.API_VERSION, env=settings.ENVIRONMENT)
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning("Database initialization failed - API will run in read-only mode", error=str(e))
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

    # ─── Rate Limiter ────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ─── Server Timing Middleware ────────────────────────────
    import time
    class ServerTimingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            start_time = time.monotonic()
            response = await call_next(request)
            process_time = time.monotonic() - start_time
            response.headers["Server-Timing"] = f"total;dur={process_time * 1000:.2f}"
            return response
            
    app.add_middleware(ServerTimingMiddleware)

    # ─── Request ID Middleware ───────────────────────────────
    class RequestIdMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
            structlog.contextvars.bind_contextvars(request_id=req_id)
            response = await call_next(request)
            response.headers["X-Request-ID"] = req_id
            return response
            
    app.add_middleware(RequestIdMiddleware)

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

    # ─── Health Check ────────────────────────────────────────
    # Note: Health check is also available at /api/v1/health via projects router
    # This root endpoint is kept for monitoring tools
    @app.get("/health")
    async def root_health_check():
        from datetime import datetime, timezone
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    # ─── Prometheus Metrics ──────────────────────────────────
    Instrumentator().instrument(app).expose(app, tags=["system"])

    return app


app = create_application()

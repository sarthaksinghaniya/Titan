"""Sessions API router — all session-related endpoints."""
import asyncio
import json
from typing import AsyncGenerator
from uuid import UUID

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.config import settings
from app.models.session import Session, MinisterAnalysis, DebateRound, Vote, SimulationResult, FinalPolicy
from app.models.session import SessionStatus
from app.schemas.session import (
    CreateSessionRequest,
    CreateSessionResponse,
    SessionSchema,
    PaginatedResponse,
    SessionReportSchema,
    MinisterAnalysisSchema,
    DebateRoundSchema,
    VoteSchema,
    SimulationResultSchema,
    FinalPolicySchema,
    HealthResponse,
)
from app.services.session_service import SessionService
from app.services.event_bus import EventBus

logger = structlog.get_logger(__name__)
router = APIRouter()
event_bus = EventBus()


# ─── Health Check ─────────────────────────────────────────────
@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Health check endpoint for monitoring."""
    try:
        await db.execute(select(func.now()))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        version=settings.API_VERSION,
        environment=settings.ENVIRONMENT,
        database=db_status,
        gemini_configured=settings.has_gemini_key,
    )


# ─── Create Session ───────────────────────────────────────────
@router.post("/sessions", response_model=CreateSessionResponse, status_code=201, tags=["sessions"])
async def create_session(
    request: CreateSessionRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> CreateSessionResponse:
    """
    Create a new governance session and start the agent graph in the background.
    Returns the session ID immediately — stream updates via SSE.
    """
    service = SessionService(db, event_bus)
    session = await service.create_session(request.problem, request.context)

    # Run the agent graph asynchronously
    background_tasks.add_task(service.run_agent_graph, str(session.id))

    logger.info("Session created", session_id=str(session.id))
    return CreateSessionResponse(
        session_id=str(session.id),
        status=SessionSchema.model_validate(session).status,
        message="Cabinet session initiated. Ministers are assembling...",
    )


# ─── List Sessions ────────────────────────────────────────────
@router.get("/sessions", tags=["sessions"])
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    """List all sessions with pagination, ordered by creation date (newest first)."""
    offset = (page - 1) * page_size

    count_result = await db.execute(select(func.count(Session.id)))
    total = count_result.scalar_one()

    result = await db.execute(
        select(Session).order_by(Session.created_at.desc()).offset(offset).limit(page_size)
    )
    sessions = result.scalars().all()

    return PaginatedResponse(
        items=[SessionSchema.model_validate(s) for s in sessions],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(offset + page_size) < total,
    )


# ─── Get Session ──────────────────────────────────────────────
@router.get("/sessions/{session_id}", response_model=SessionSchema, tags=["sessions"])
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> SessionSchema:
    """Get a single session by ID."""
    result = await db.execute(select(Session).where(Session.id == UUID(session_id)))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return SessionSchema.model_validate(session)


# ─── Get Session Report ───────────────────────────────────────
@router.get("/sessions/{session_id}/report", response_model=SessionReportSchema, tags=["sessions"])
async def get_session_report(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> SessionReportSchema:
    """Get the full report for a session including all agent outputs."""
    session_result = await db.execute(select(Session).where(Session.id == UUID(session_id)))
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    analyses_result = await db.execute(
        select(MinisterAnalysis).where(MinisterAnalysis.session_id == UUID(session_id))
    )
    debates_result = await db.execute(
        select(DebateRound).where(DebateRound.session_id == UUID(session_id)).order_by(DebateRound.round_number)
    )
    votes_result = await db.execute(
        select(Vote).where(Vote.session_id == UUID(session_id))
    )
    sims_result = await db.execute(
        select(SimulationResult).where(SimulationResult.session_id == UUID(session_id))
    )
    policy_result = await db.execute(
        select(FinalPolicy).where(FinalPolicy.session_id == UUID(session_id))
    )

    return SessionReportSchema(
        session=SessionSchema.model_validate(session),
        analyses=[MinisterAnalysisSchema.model_validate(a) for a in analyses_result.scalars().all()],
        debate_rounds=[DebateRoundSchema.model_validate(d) for d in debates_result.scalars().all()],
        votes=[VoteSchema.model_validate(v) for v in votes_result.scalars().all()],
        simulation_results=[SimulationResultSchema.model_validate(s) for s in sims_result.scalars().all()],
        final_policy=FinalPolicySchema.model_validate(policy_result.scalar_one_or_none())
        if policy_result.scalar_one_or_none()
        else None,
    )


# ─── SSE Stream ───────────────────────────────────────────────
@router.get("/sessions/{session_id}/stream", tags=["sessions"])
async def stream_session(session_id: str) -> StreamingResponse:
    """
    Server-Sent Events stream for real-time agent activity.
    Connect from the frontend to receive live updates.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        # Send heartbeat immediately on connect
        yield f"data: {json.dumps({'event': 'heartbeat', 'data': {'session_id': session_id}, 'timestamp': ''})}\n\n"

        async for event in event_bus.subscribe(session_id):
            yield f"data: {json.dumps(event)}\n\n"
            if event.get("event") in ("session_complete", "error"):
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )

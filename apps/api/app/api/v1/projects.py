"""Projects API router — all project-related endpoints."""
import json
from typing import AsyncGenerator, List
from uuid import UUID

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.models.session import ProjectStatus
from app.schemas.session import (
    CreateProjectRequest,
    CreateProjectResponse,
    ProjectSchema,
    PaginatedResponse,
    ProjectReportSchema,
    AgentSchema,
    DebateSchema,
    VoteSchema,
    SimulationSchema,
    FinalReportSchema,
    HealthResponse,
)
from app.services.session_service import SessionService
from app.services.event_bus import EventBus
from app.repositories.project import project_repo

logger = structlog.get_logger(__name__)
router = APIRouter()
event_bus = EventBus()


# ─── Health Check ─────────────────────────────────────────────
@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Health check endpoint for monitoring."""
    try:
        from sqlalchemy import select, func
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


# ─── Create Project ───────────────────────────────────────────
@router.post("/sessions", response_model=CreateProjectResponse, status_code=201, tags=["projects"])
async def create_project(
    request: CreateProjectRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> CreateProjectResponse:
    """
    Create a new governance project and start the agent graph in the background.
    Returns the project ID immediately — stream updates via SSE.
    """
    service = SessionService(db, event_bus)
    project = await service.create_project(request.problem, request.context)

    # Run the agent graph asynchronously
    background_tasks.add_task(service.run_agent_graph, str(project.id))

    logger.info("Project created", project_id=str(project.id))
    return CreateProjectResponse(
        session_id=str(project.id),  # Frontend expects session_id
        project_id=str(project.id),
        status=project.status,
        message="Cabinet session initiated. Ministers are assembling...",
    )


# ─── List Projects ────────────────────────────────────────────
@router.get("/sessions", response_model=PaginatedResponse, tags=["projects"])
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    """List all projects with pagination, ordered by creation date (newest first)."""
    items, total = await project_repo.get_multi_paginated(db, page=page, page_size=page_size)

    return PaginatedResponse(
        items=[ProjectSchema.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )


# ─── Get Project ──────────────────────────────────────────────
@router.get("/sessions/{project_id}", response_model=ProjectSchema, tags=["projects"])
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> ProjectSchema:
    """Get a single project by ID."""
    project = await project_repo.get(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return ProjectSchema.model_validate(project)


# ─── Get Project Report ───────────────────────────────────────
@router.get("/sessions/{project_id}/report", response_model=ProjectReportSchema, tags=["projects"])
async def get_project_report(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> ProjectReportSchema:
    """Get the full report for a project including all agent outputs."""
    project = await project_repo.get_with_relations(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    return ProjectReportSchema(
        project=ProjectSchema.model_validate(project),
        agents=[AgentSchema.model_validate(a) for a in project.agents],
        debates=[DebateSchema.model_validate(d) for d in project.debates],
        votes=[VoteSchema.model_validate(v) for v in project.votes],
        simulations=[SimulationSchema.model_validate(s) for s in project.simulations],
        final_report=FinalReportSchema.model_validate(project.final_report) if project.final_report else None,
    )


# ─── SSE Stream ────────────────────────────────────────────────
@router.get("/sessions/{project_id}/stream", tags=["projects"])
async def stream_project(project_id: str) -> StreamingResponse:
    """
    Server-Sent Events stream for real-time agent activity.
    Connect from the frontend to receive live updates.

    Connection lifecycle:
    1. Browser connects → immediately receives an initial heartbeat.
    2. Events are forwarded as they arrive from the event_bus queue.
    3. The stream exits cleanly when the server sends a sentinel via
       close_session() (after session_complete or error event).
    4. If the browser disconnects early, asyncio.CancelledError propagates
       through event_bus.subscribe(), which cleans up the queue.
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        # Immediate heartbeat confirms connection to the browser.
        yield (
            f"data: {json.dumps({'event': 'heartbeat', 'data': {'project_id': project_id}, 'timestamp': ''})}\n\n"
        )
        try:
            async for event in event_bus.subscribe(project_id):
                yield f"data: {json.dumps(event)}\n\n"
                # Do NOT break on session_complete/error here.
                # close_session() sends the sentinel which causes
                # event_bus.subscribe() to return naturally, ending this loop.
        except GeneratorExit:
            # Browser closed the connection mid-stream.
            # asyncio.CancelledError is already handled inside subscribe().
            logger.info("SSE client disconnected", project_id=project_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",      # Disable nginx buffering
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream; charset=utf-8",
        },
    )


# ─── Get Debate History ───────────────────────────────────────
@router.get("/sessions/{project_id}/debate-history", response_model=List[DebateSchema], tags=["projects"])
async def get_debate_history(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> List[DebateSchema]:
    """
    Get the chronological debate history for replayability.
    Ordered by created_at.
    """
    from sqlalchemy import select
    from app.models.session import Debate
    
    stmt = select(Debate).where(Debate.project_id == UUID(project_id)).order_by(Debate.created_at.asc())
    result = await db.execute(stmt)
    debates = list(result.scalars().all())
    
    return [DebateSchema.model_validate(d) for d in debates]

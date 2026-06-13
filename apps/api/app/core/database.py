"""
Async SQLAlchemy database engine and session factory.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

import socket
import urllib.parse
import os
import structlog

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = structlog.get_logger(__name__)

def is_port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False

# ─── Resolve Connection ──────────────────────────────────────
db_url = settings.DATABASE_URL
engine_args = {
    "echo": settings.DATABASE_ECHO,
}

if db_url.startswith("postgresql"):
    parsed = urllib.parse.urlparse(db_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    if not is_port_open(host, port):
        sqlite_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "titan_local.db"))
        db_url = f"sqlite+aiosqlite:///{sqlite_path}"
        logger.warning("PostgreSQL server not reachable. Falling back to local SQLite", sqlite_path=sqlite_path)
        engine_args["connect_args"] = {"check_same_thread": False}
    else:
        engine_args.update({
            "pool_pre_ping": True,
            "pool_size": 10,
            "max_overflow": 20,
        })
else:
    engine_args["connect_args"] = {"check_same_thread": False}

# ─── Engine ──────────────────────────────────────────────────
engine = create_async_engine(
    db_url,
    **engine_args
)

# ─── Session Factory ─────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ─── Base Model ───────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ─── Dependency ───────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ─── Init DB ──────────────────────────────────────────────────
async def init_db() -> None:
    """Create all tables on startup."""
    from app.models import session as _session_models  # noqa: F401 — register models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

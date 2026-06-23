"""
backend/app/db/database.py
Async SQLAlchemy engine, session factory, and FastAPI dependency.
"""
from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from ..config import get_settings
from .base import Base

logger = logging.getLogger(__name__)


def _build_engine() -> AsyncEngine:
    """Create and return the async SQLAlchemy engine."""
    settings = get_settings()
    return create_async_engine(
        settings.DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=False,
        future=True,
    )


engine: AsyncEngine = _build_engine()

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Backwards-compatible alias used by older job code.
SessionLocal = AsyncSessionLocal


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


async def init_db() -> None:
    """Create all tables and verify database connectivity."""
    import app.models  # noqa: F401

    try:
        async with engine.begin() as conn:
            logger.info("Running init_db(): creating tables if they do not exist …")
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            value = result.scalar_one()
            assert value == 1, f"Unexpected ping result: {value}"

        logger.info("init_db() completed successfully.")
    except Exception as exc:
        logger.error("init_db() failed: %s", exc, exc_info=True)
        raise

"""
backend/app/routers/health.py
Health-check endpoint — used by Docker HEALTHCHECK and monitoring tools.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Liveness + DB connectivity probe",
    response_description="Service health status",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> dict:
    """Return service version and database reachability status.

    Parameters
    ----------
    db:
        Injected async database session.

    Returns
    -------
    dict
        ``status``: always ``"ok"``
        ``version``: current API version string
        ``db``: ``"connected"`` or ``"disconnected"``
    """
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        logger.warning("Health check: DB ping failed – %s", exc)
        db_status = "disconnected"

    return {
        "status": "ok",
        "version": "0.1.0",
        "db": db_status,
    }

import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.jobs.run_all import run_all_ingestion_jobs
from app.models import EquityPrice, MemoryQuote, RefreshJob
from app.schemas import RefreshHealthResponse, RefreshHealthSection, RefreshStatus
from app.services.refresh_service import build_refresh_health, get_latest_refresh_job

router = APIRouter(tags=["refresh"])


@router.post("/refresh", status_code=202)
async def start_refresh(
    db: AsyncSession = Depends(get_db),
    x_finmind_token: str | None = Header(default=None),
) -> dict:
    """Kick off the full ingestion pipeline.

    An optional ``X-FinMind-Token`` request header (sent by the UI from the
    user's localStorage) is forwarded to the TW/US FinMind ingestion so users
    can supply their own FinMind API key without server-side configuration.
    """
    running = await db.scalar(select(RefreshJob).where(RefreshJob.lock_key == "daily_ingestion", RefreshJob.status == "running"))
    if running:
        raise HTTPException(status_code=409, detail={"error": "job_already_running", "job_id": running.id})
    token = (x_finmind_token or "").strip() or None
    task = asyncio.create_task(run_all_ingestion_jobs(trigger="manual", finmind_token=token))
    await asyncio.sleep(0)
    return {"job_id": task.get_name() or "manual-refresh", "status": "started", "trigger": "manual", "finmind_token_used": bool(token)}


@router.get("/refresh/status")
async def refresh_status(db: AsyncSession = Depends(get_db)) -> RefreshStatus:
    return await get_latest_refresh_job(db)


@router.get("/refresh/status/{job_id}")
async def refresh_status_detail(job_id: str, db: AsyncSession = Depends(get_db)) -> RefreshStatus:
    job = await db.get(RefreshJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")
    return RefreshStatus(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        started_at=job.started_at,
        finished_at=job.finished_at,
        error_msg=job.error_msg,
    )


@router.get("/refresh/health")
async def refresh_health(db: AsyncSession = Depends(get_db)) -> RefreshHealthResponse:
    return await build_refresh_health(db)

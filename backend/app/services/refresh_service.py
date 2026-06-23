from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import EquityPrice, MemoryQuote, RefreshJob
from app.schemas import RefreshHealthResponse, RefreshHealthSection, RefreshStatus

settings = get_settings()


async def get_latest_refresh_job(db: AsyncSession) -> RefreshStatus:
    job = await db.scalar(select(RefreshJob).order_by(RefreshJob.started_at.desc()).limit(1))
    if not job:
        return RefreshStatus(status="idle")
    return RefreshStatus(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        started_at=job.started_at,
        finished_at=job.finished_at,
        error_msg=job.error_msg,
    )


def _build_section(last_updated: datetime | None, threshold: int) -> RefreshHealthSection:
    if not last_updated:
        return RefreshHealthSection(last_updated=None, hours_since_update=None, is_stale=True, threshold_hours=threshold)
    hours = (datetime.now(timezone.utc) - last_updated.astimezone(timezone.utc)).total_seconds() / 3600
    return RefreshHealthSection(
        last_updated=last_updated,
        hours_since_update=round(hours, 2),
        is_stale=hours > threshold,
        threshold_hours=threshold,
    )


async def build_refresh_health(db: AsyncSession) -> RefreshHealthResponse:
    last_price = await db.scalar(select(EquityPrice.created_at).order_by(EquityPrice.created_at.desc()).limit(1))
    last_quote = await db.scalar(select(MemoryQuote.fetched_at).order_by(MemoryQuote.fetched_at.desc()).limit(1))
    price_section = _build_section(last_price, settings.DATA_FRESHNESS_THRESHOLD_HOURS_STOCK)
    quote_section = _build_section(last_quote, settings.DATA_FRESHNESS_THRESHOLD_HOURS_QUOTE)
    overall = "fresh"
    if price_section.is_stale or quote_section.is_stale:
        overall = "stale"
    if (
        price_section.hours_since_update
        and price_section.hours_since_update > settings.DATA_FRESHNESS_THRESHOLD_HOURS_STOCK * 2
    ) or (
        quote_section.hours_since_update
        and quote_section.hours_since_update > settings.DATA_FRESHNESS_THRESHOLD_HOURS_QUOTE * 2
    ):
        overall = "critical"
    latest_job = await db.scalar(select(RefreshJob).order_by(RefreshJob.started_at.desc()).limit(1))
    scheduler_state = None
    if latest_job:
        scheduler_state = {"started_at": latest_job.started_at, "status": latest_job.status, "job_id": latest_job.id}
    return RefreshHealthResponse(
        overall_status=overall,
        equity_prices=price_section,
        memory_quotes=quote_section,
        last_scheduler_run=scheduler_state,
    )

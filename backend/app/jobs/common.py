import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EquityPrice, Instrument, MemoryQuote, RefreshJob, SourceRun


async def create_source_run(db: AsyncSession, source_name: str, trigger: str) -> SourceRun:
    run = SourceRun(source_name=source_name, trigger=trigger, status="running", progress={})
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


async def finish_source_run(
    db: AsyncSession,
    run: SourceRun,
    status: str,
    row_count: int,
    success_count: int,
    fail_count: int,
    error_msg: str | None = None,
    progress: dict | None = None,
) -> None:
    run.status = status
    run.row_count = row_count
    run.success_count = success_count
    run.fail_count = fail_count
    run.error_msg = error_msg
    run.progress = progress or run.progress
    run.finished_at = datetime.now(timezone.utc)
    await db.commit()


async def get_instruments_by_market(db: AsyncSession, market: str) -> list[Instrument]:
    result = await db.scalars(select(Instrument).where(Instrument.market == market, Instrument.is_active.is_(True)))
    return result.all()


async def get_last_trade_date(db: AsyncSession, instrument_id: int) -> date | None:
    row = await db.scalar(
        select(EquityPrice.trade_date).where(EquityPrice.instrument_id == instrument_id).order_by(EquityPrice.trade_date.desc()).limit(1)
    )
    return row


async def upsert_equity_prices(db: AsyncSession, instrument_id: int, source: str, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    payload = []
    for row in rows:
        payload.append(
            {
                "instrument_id": instrument_id,
                "trade_date": row["trade_date"],
                "open": row.get("open"),
                "high": row.get("high"),
                "low": row.get("low"),
                "close": row.get("close"),
                "volume": row.get("volume"),
                "source": source,
            }
        )
    stmt = insert(EquityPrice).values(payload)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_equity_price_instrument_trade_date",
        set_={
            "open": stmt.excluded.open,
            "high": stmt.excluded.high,
            "low": stmt.excluded.low,
            "close": stmt.excluded.close,
            "volume": stmt.excluded.volume,
            "source": stmt.excluded.source,
        },
    )
    await db.execute(stmt)
    await db.commit()
    return len(payload)


async def upsert_memory_quotes(db: AsyncSession, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    stmt = insert(MemoryQuote).values(rows)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_memory_quote_product_type_date",
        set_={
            "category": stmt.excluded.category,
            "price_high": stmt.excluded.price_high,
            "price_low": stmt.excluded.price_low,
            "price_avg": stmt.excluded.price_avg,
            "change_pct": stmt.excluded.change_pct,
            "currency": stmt.excluded.currency,
            "unit": stmt.excluded.unit,
            "source": stmt.excluded.source,
            "fetched_at": stmt.excluded.fetched_at,
        },
    )
    await db.execute(stmt)
    await db.commit()
    return len(rows)


def normalize_ohlcv_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for row in rows:
        trade_date = row.get("date") or row.get("Date")
        if not trade_date:
            continue
        normalized.append(
            {
                "trade_date": date.fromisoformat(str(trade_date)[:10]),
                "open": _to_decimal(row.get("open") or row.get("Open")),
                "high": _to_decimal(row.get("high") or row.get("High")),
                "low": _to_decimal(row.get("low") or row.get("Low")),
                "close": _to_decimal(row.get("close") or row.get("Close")),
                "volume": int(float(row.get("volume") or row.get("Volume") or 0)) if row.get("volume") or row.get("Volume") else None,
            }
        )
    return normalized


def _to_decimal(value: Any) -> Decimal | None:
    if value in (None, "", "None", "null"):
        return None
    return Decimal(str(value))


async def acquire_refresh_lock(db: AsyncSession, lock_key: str, trigger: str) -> RefreshJob | None:
    running = await db.scalar(select(RefreshJob).where(RefreshJob.lock_key == lock_key, RefreshJob.status == "running"))
    if running:
        return None
    job = RefreshJob(id=uuid.uuid4().hex, lock_key=lock_key, trigger=trigger, status="running", progress={})
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def update_refresh_job(
    db: AsyncSession,
    job: RefreshJob,
    status: str | None = None,
    progress: dict | None = None,
    error_msg: str | None = None,
) -> None:
    if status:
        job.status = status
    if progress is not None:
        job.progress = progress
    if error_msg is not None:
        job.error_msg = error_msg
    if status in {"success", "fail", "partial"}:
        job.finished_at = datetime.now(timezone.utc)
    await db.commit()

"""
backend/app/jobs/evaluate_alerts.py
=====================================
Evaluate all active alert rules and dispatch notifications.

Supported metrics
-----------------
* total_score              – latest MarketScore.total_score
* dram_spot_1d_change      – latest MemoryQuote change_pct (category=DRAM)
* nand_wafer_1d_change     – latest MemoryQuote change_pct (category=NAND)
* stock_1d_change.<TICKER> – latest TrendMetric change_pct for 1D period

Supported conditions
--------------------
* gt          – metric_value > threshold
* lt          – metric_value < threshold
* cross_up    – yesterday < threshold AND today >= threshold
* cross_down  – yesterday >= threshold AND today < threshold

For cross_up/cross_down the previous value is fetched from the second-latest
snapshot of the same metric.
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert_event import AlertEvent
from app.models.alert_rule import AlertRule
from app.models.instrument import Instrument
from app.models.market_score import MarketScore
from app.models.memory_quote import MemoryQuote
from app.models.trend_metric import TrendMetric
from app.services.email_notifier import send_email
from app.services.line_notifier import send_line
from app.services.telegram_notifier import send_telegram

logger = logging.getLogger(__name__)


async def evaluate_alerts(db: AsyncSession) -> dict[str, Any]:
    """Evaluate all active alert rules and fire notifications when triggered.

    Parameters
    ----------
    db:
        An active async SQLAlchemy session.

    Returns
    -------
    dict
        ``{"status": "success", "event_count": N}``
    """
    rules = list(
        (
            await db.scalars(
                select(AlertRule).where(AlertRule.is_active.is_(True))
            )
        ).all()
    )

    if not rules:
        return {"status": "success", "event_count": 0}

    # ------------------------------------------------------------------ #
    # Pre-fetch the data we need
    # ------------------------------------------------------------------ #
    latest_score: MarketScore | None = await db.scalar(
        select(MarketScore).order_by(MarketScore.score_date.desc()).limit(1)
    )
    prev_score: MarketScore | None = await db.scalar(
        select(MarketScore).order_by(MarketScore.score_date.desc()).offset(1).limit(1)
    )

    dram_latest = await db.scalar(
        select(MemoryQuote)
        .where(MemoryQuote.category == "DRAM")
        .order_by(MemoryQuote.snapshot_date.desc())
        .limit(1)
    )
    dram_prev = await db.scalar(
        select(MemoryQuote)
        .where(MemoryQuote.category == "DRAM")
        .order_by(MemoryQuote.snapshot_date.desc())
        .offset(1)
        .limit(1)
    )

    nand_latest = await db.scalar(
        select(MemoryQuote)
        .where(MemoryQuote.category == "NAND")
        .order_by(MemoryQuote.snapshot_date.desc())
        .limit(1)
    )
    nand_prev = await db.scalar(
        select(MemoryQuote)
        .where(MemoryQuote.category == "NAND")
        .order_by(MemoryQuote.snapshot_date.desc())
        .offset(1)
        .limit(1)
    )

    # Instrument lookup (for stock_ metric)
    instruments: dict[str, Instrument] = {
        inst.ticker: inst
        for inst in (
            await db.scalars(select(Instrument).where(Instrument.is_active.is_(True)))
        ).all()
    }

    event_count = 0

    for rule in rules:
        try:
            current_val, prev_val = await _resolve_metric(
                db=db,
                metric=rule.metric,
                latest_score=latest_score,
                prev_score=prev_score,
                dram_latest=dram_latest,
                dram_prev=dram_prev,
                nand_latest=nand_latest,
                nand_prev=nand_prev,
                instruments=instruments,
            )
        except Exception as exc:
            logger.warning("evaluate_alerts – could not resolve metric '%s': %s", rule.metric, exc)
            continue

        triggered = _check_condition(
            condition=rule.condition,
            threshold=rule.threshold,
            current=current_val,
            previous=prev_val,
        )
        if not triggered:
            continue

        # Build notification message
        message = _format_message(rule, current_val)

        # Dispatch
        notify_status = await _dispatch(rule.channel, message)

        # Record event
        event = AlertEvent(
            rule_id=rule.id,
            metric_value=current_val,
            notify_status=notify_status,
            message=message,
        )
        db.add(event)
        event_count += 1
        logger.info(
            "evaluate_alerts – rule '%s' triggered (value=%s, status=%s)",
            rule.rule_name,
            current_val,
            notify_status,
        )

    await db.commit()
    return {"status": "success", "event_count": event_count}


# ---------------------------------------------------------------------------
# Metric resolution
# ---------------------------------------------------------------------------


async def _resolve_metric(
    *,
    db: AsyncSession,
    metric: str,
    latest_score: MarketScore | None,
    prev_score: MarketScore | None,
    dram_latest: MemoryQuote | None,
    dram_prev: MemoryQuote | None,
    nand_latest: MemoryQuote | None,
    nand_prev: MemoryQuote | None,
    instruments: dict[str, Instrument],
) -> tuple[Decimal, Decimal | None]:
    """Return (current_value, previous_value) for *metric*.

    previous_value may be None if not available or not needed.
    """
    if metric == "total_score":
        cur = latest_score.total_score if latest_score else Decimal("50")
        prv = prev_score.total_score if prev_score else None
        return cur or Decimal("0"), prv

    if metric == "dram_spot_1d_change":
        cur = dram_latest.change_pct if dram_latest else Decimal("0")
        prv = dram_prev.change_pct if dram_prev else None
        return cur or Decimal("0"), prv

    if metric == "nand_wafer_1d_change":
        cur = nand_latest.change_pct if nand_latest else Decimal("0")
        prv = nand_prev.change_pct if nand_prev else None
        return cur or Decimal("0"), prv

    if metric.startswith("stock_1d_change."):
        ticker = metric.split(".", 1)[1].upper()
        instrument = instruments.get(ticker)
        if not instrument:
            return Decimal("0"), None

        rows = list(
            (
                await db.scalars(
                    select(TrendMetric)
                    .where(
                        TrendMetric.instrument_id == instrument.id,
                        TrendMetric.period == "1D",
                    )
                    .order_by(TrendMetric.as_of_date.desc())
                    .limit(2)
                )
            ).all()
        )
        cur = rows[0].change_pct if rows else Decimal("0")
        prv = rows[1].change_pct if len(rows) > 1 else None
        return cur or Decimal("0"), prv

    # Unknown metric – return zeros
    logger.debug("evaluate_alerts – unknown metric '%s', returning 0", metric)
    return Decimal("0"), None


# ---------------------------------------------------------------------------
# Condition evaluation
# ---------------------------------------------------------------------------


def _check_condition(
    condition: str,
    threshold: Decimal,
    current: Decimal,
    previous: Decimal | None,
) -> bool:
    """Return True if the alert condition is satisfied."""
    if condition == "gt":
        return current > threshold
    if condition == "lt":
        return current < threshold
    if condition == "cross_up":
        return previous is not None and previous < threshold <= current
    if condition == "cross_down":
        return previous is not None and previous >= threshold > current
    return False


# ---------------------------------------------------------------------------
# Notification dispatch
# ---------------------------------------------------------------------------


async def _dispatch(channel: str, message: str) -> str:
    """Send *message* via *channel* and return 'sent' or 'failed'."""
    try:
        if channel == "telegram":
            ok = await send_telegram(message)
        elif channel == "line":
            ok = await send_line(message)
        elif channel == "email":
            ok = await send_email(
                subject="記憶體儀錶板告警",
                plain_text=message,
                html_text=f"<pre>{message}</pre>",
            )
        else:
            logger.warning("evaluate_alerts – unknown channel '%s'", channel)
            return "failed"
    except Exception as exc:
        logger.error("evaluate_alerts – dispatch error on channel '%s': %s", channel, exc)
        return "failed"
    return "sent" if ok else "failed"


# ---------------------------------------------------------------------------
# Message formatting
# ---------------------------------------------------------------------------


def _format_message(rule: AlertRule, value: Decimal) -> str:
    return (
        f"🚨 *記憶體儀錶板告警*\n"
        f"規則：{rule.rule_name}\n"
        f"指標：{rule.metric}\n"
        f"條件：{rule.condition} {rule.threshold}\n"
        f"當前值：{value}\n"
    )

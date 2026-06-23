"""
backend/app/jobs/compute_trend_metrics.py
=========================================
Full trend-metrics calculation engine.

For every active instrument that has equity_prices data, compute per-period
statistics (1D / 1W / 1M / 3M / 6M / 1Y) and upsert to the trend_metrics
table.  Memory-quote instruments share the same table via *instrument_id*,
so they benefit automatically once prices are stored in equity_prices.

Processing is batched in groups of 50 to avoid holding huge query result-sets
in RAM.  Missing / insufficient history for a period is skipped gracefully.
"""
from __future__ import annotations

import logging
import math
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.equity_price import EquityPrice
from app.models.instrument import Instrument
from app.models.trend_metric import TrendMetric

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PERIODS: dict[str, int] = {
    "1D": 1,
    "1W": 5,
    "1M": 21,
    "3M": 63,
    "6M": 126,
    "1Y": 252,
}

BATCH_SIZE = 50
UPSERT_CONSTRAINT = "uq_trend_metric_instrument_date_period"

# ---------------------------------------------------------------------------
# Public entry-point
# ---------------------------------------------------------------------------


async def compute_trend_metrics(db: AsyncSession) -> dict[str, Any]:
    """Compute and upsert trend metrics for all active instruments.

    Parameters
    ----------
    db:
        An active async SQLAlchemy session.

    Returns
    -------
    dict
        ``{"status": "success", "instruments_processed": N, "row_count": M}``
    """
    # Fetch all active instruments
    instruments = list(
        (
            await db.scalars(
                select(Instrument)
                .where(Instrument.is_active.is_(True))
                .order_by(Instrument.id)
            )
        ).all()
    )

    total_rows = 0
    processed = 0

    for batch_start in range(0, len(instruments), BATCH_SIZE):
        batch = instruments[batch_start : batch_start + BATCH_SIZE]
        for instrument in batch:
            rows_written = await _process_instrument(db, instrument)
            total_rows += rows_written
            processed += 1

        # Commit after each batch
        await db.commit()
        logger.info(
            "compute_trend_metrics – batch %d/%d done, cumulative rows=%d",
            batch_start + len(batch),
            len(instruments),
            total_rows,
        )

    return {
        "status": "success",
        "instruments_processed": processed,
        "row_count": total_rows,
    }


# ---------------------------------------------------------------------------
# Per-instrument processing
# ---------------------------------------------------------------------------


async def _process_instrument(db: AsyncSession, instrument: Instrument) -> int:
    """Compute all period metrics for a single instrument and upsert them.

    Returns the number of rows written (0–6).
    """
    price_rows = list(
        (
            await db.scalars(
                select(EquityPrice)
                .where(EquityPrice.instrument_id == instrument.id)
                .order_by(EquityPrice.trade_date)
            )
        ).all()
    )

    # Build a clean (date, close) list, discarding null closes
    pairs: list[tuple[date, float]] = [
        (row.trade_date, float(row.close))
        for row in price_rows
        if row.close is not None
    ]

    if len(pairs) < 2:
        return 0

    dates = [p[0] for p in pairs]
    closes = [p[1] for p in pairs]
    latest_close = closes[-1]
    latest_date = dates[-1]

    # Pre-compute structures used across all periods
    daily_returns = _daily_returns(closes)
    ma_state = _compute_ma_state(closes)
    streak = _compute_streak(closes)
    hi_lo_flags = _compute_hi_lo_flags(closes)
    ma_above = _ma_above_count(ma_state)

    # 1M change needed for momentum formula
    change_1m = _lookback_pct(closes, 21)
    change_3m = _lookback_pct(closes, 63)

    # Normalised index is always anchored to 1Y (252 bars) ago
    normalized_index = (
        (latest_close / closes[max(0, len(closes) - 252)]) * 100
        if len(closes) >= 252
        else 100.0
    )

    rows_written = 0
    for period, lookback in PERIODS.items():
        if len(closes) <= lookback:
            # Insufficient history – skip this period gracefully
            continue

        base = closes[-(lookback + 1)]
        if base == 0:
            continue

        change_pct = ((latest_close - base) / base) * 100
        change_abs = latest_close - base
        direction = (
            "up" if change_pct > 0.5 else "down" if change_pct < -0.5 else "flat"
        )

        period_returns = daily_returns[-lookback:]
        volatility = _annualised_volatility(period_returns)

        # momentum = 1M*0.5 + 3M*0.3 + (ma_above_ratio * 100)*0.2
        momentum = (
            change_1m * 0.5
            + change_3m * 0.3
            + (ma_above / 4.0 * 100) * 0.2
        )

        # Acceleration: current period change vs prior period of same length
        prior_change = (
            _lookback_pct(closes, lookback * 2)
            if len(closes) > lookback * 2
            else change_pct
        )
        acceleration = change_pct - prior_change

        payload: dict[str, Any] = {
            "instrument_id": instrument.id,
            "as_of_date": latest_date,
            "period": period,
            "change_pct": _d4(change_pct),
            "change_abs": _d6(change_abs),
            "direction": direction,
            "momentum": _d4(momentum),
            "ma_state": ma_state,
            "volatility": _d4(volatility),
            "hi_lo_flag": hi_lo_flags,
            "streak": streak,
            "acceleration": _d4(acceleration),
            "normalized_index": _d4(normalized_index),
            "narrative": (
                f"{instrument.ticker} {period} {direction} "
                f"{change_pct:.2f}%"
            ),
        }

        stmt = insert(TrendMetric).values(payload)
        stmt = stmt.on_conflict_do_update(
            constraint=UPSERT_CONSTRAINT,
            set_={
                k: getattr(stmt.excluded, k)
                for k in payload
                if k not in {"instrument_id", "as_of_date", "period"}
            },
        )
        await db.execute(stmt)
        rows_written += 1

    return rows_written


# ---------------------------------------------------------------------------
# Calculation helpers
# ---------------------------------------------------------------------------


def _daily_returns(closes: list[float]) -> list[float]:
    """Compute simple daily percentage returns as decimals (not %)."""
    out: list[float] = []
    for i in range(1, len(closes)):
        prev = closes[i - 1]
        if prev:
            out.append((closes[i] - prev) / prev)
        else:
            out.append(0.0)
    return out


def _lookback_pct(closes: list[float], lookback: int) -> float:
    """% change from ``lookback`` bars ago to the latest bar."""
    if len(closes) <= lookback:
        return 0.0
    base = closes[-(lookback + 1)]
    return ((closes[-1] - base) / base * 100) if base else 0.0


def _compute_ma_state(closes: list[float]) -> dict[str, str]:
    """Return above/below string for each standard moving average."""
    latest = closes[-1]
    state: dict[str, str] = {}
    for days in (20, 60, 120, 240):
        if len(closes) >= days:
            ma = sum(closes[-days:]) / days
            state[f"ma{days}"] = "above" if latest >= ma else "below"
    return state


def _ma_above_count(ma_state: dict[str, str]) -> int:
    return sum(1 for v in ma_state.values() if v == "above")


def _compute_hi_lo_flags(closes: list[float]) -> dict[str, bool]:
    """Is the latest close at a 1M / 3M / 6M / 1Y high or low?"""
    latest = closes[-1]
    flags: dict[str, bool] = {}
    for label, days in {"1M": 21, "3M": 63, "6M": 126, "1Y": 252}.items():
        if len(closes) >= days:
            window = closes[-days:]
            flags[f"{label}_high"] = latest >= max(window)
            flags[f"{label}_low"] = latest <= min(window)
    return flags


def _compute_streak(closes: list[float]) -> int:
    """Consecutive up/down days.  Positive = consecutive up days."""
    streak = 0
    for i in range(len(closes) - 1, 0, -1):
        diff = closes[i] - closes[i - 1]
        if diff > 0 and streak >= 0:
            streak += 1
        elif diff < 0 and streak <= 0:
            streak -= 1
        else:
            break
    return streak


def _annualised_volatility(daily_returns: list[float]) -> float:
    """Annualised standard deviation of daily returns, expressed as %."""
    n = len(daily_returns)
    if n < 2:
        return 0.0
    mean = sum(daily_returns) / n
    variance = sum((r - mean) ** 2 for r in daily_returns) / n
    return math.sqrt(variance) * math.sqrt(252) * 100


def _d4(value: float) -> Decimal:
    """Round to 4 decimal places and return a Decimal."""
    return Decimal(f"{value:.4f}")


def _d6(value: float) -> Decimal:
    """Round to 6 decimal places and return a Decimal."""
    return Decimal(f"{value:.6f}")

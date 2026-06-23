"""
backend/app/jobs/compute_market_score.py
=========================================
Full market-score (bull/bear 0-100) calculation engine.

Score formula
-------------
score = 50
      + quote_momentum_score  * 0.40   (DRAM + NAND price momentum)
      + equity_momentum_score * 0.25   (Tier-A stocks only)
      + breadth_score         * 0.10   (% Tier-A/B above 20D / 60D MA)
      + risk_score_adj        * 0.15   (negative: volatility + drawdown penalty)
      + relative_strength_score * 0.10 (vs Nasdaq / TAIEX / KOSPI)

Each component is clamped before mixing so no single factor dominates.
Final score is clamped to [0, 100].

Status mapping
--------------
0–20  → strong-bear
21–40 → bear
41–60 → neutral
61–80 → bull
81–100 → strong-bull
"""
from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.instrument import Instrument
from app.models.market_score import MarketScore
from app.models.memory_quote import MemoryQuote
from app.models.trend_metric import TrendMetric

logger = logging.getLogger(__name__)

UPSERT_CONSTRAINT = "uq_market_score_date"

# Tags associated with memory-pricing / quote products
MEMORY_TAGS = {"memory-maker", "module-brand", "nand-controller", "dram-ip", "hbm"}

# Benchmark tickers used for relative-strength calculation
BENCHMARK_TICKERS = {"QQQ", "0050", "^KOSPI"}


async def compute_market_score(db: AsyncSession) -> dict[str, Any]:
    """Compute and upsert today's bull/bear market score.

    Returns
    -------
    dict
        ``{"status": "success"|"no_data", "score": float, "status_label": str}``
    """
    # ------------------------------------------------------------------ #
    # 1. Fetch the latest trend_metrics snapshot (1M period)
    # ------------------------------------------------------------------ #
    latest_date: date | None = await db.scalar(
        select(TrendMetric.as_of_date)
        .where(TrendMetric.period == "1M")
        .order_by(TrendMetric.as_of_date.desc())
        .limit(1)
    )
    if latest_date is None:
        logger.warning("compute_market_score – no trend_metrics found; returning defaults")
        return await _upsert_default(db)

    # All 1M metrics on the latest date
    metrics_1m = list(
        (
            await db.scalars(
                select(TrendMetric)
                .where(
                    TrendMetric.period == "1M",
                    TrendMetric.as_of_date == latest_date,
                )
            )
        ).all()
    )

    # 3M metrics for the same date (used for momentum cross-check)
    metrics_3m_map: dict[int, TrendMetric] = {
        row.instrument_id: row
        for row in (
            await db.scalars(
                select(TrendMetric)
                .where(
                    TrendMetric.period == "3M",
                    TrendMetric.as_of_date == latest_date,
                )
            )
        ).all()
    }

    instruments: dict[int, Instrument] = {
        inst.id: inst
        for inst in (
            await db.scalars(
                select(Instrument).where(Instrument.is_active.is_(True))
            )
        ).all()
    }

    # ------------------------------------------------------------------ #
    # 2. Segment by tier
    # ------------------------------------------------------------------ #
    tier_a: list[TrendMetric] = [
        m for m in metrics_1m
        if m.instrument_id in instruments
        and instruments[m.instrument_id].tier == "A"
    ]
    tier_ab: list[TrendMetric] = [
        m for m in metrics_1m
        if m.instrument_id in instruments
        and instruments[m.instrument_id].tier in {"A", "B"}
    ]
    memory_metrics: list[TrendMetric] = [
        m for m in metrics_1m
        if m.instrument_id in instruments
        and (instruments[m.instrument_id].supply_chain_tag or "") in MEMORY_TAGS
    ]
    benchmark_metrics: list[TrendMetric] = [
        m for m in metrics_1m
        if m.instrument_id in instruments
        and instruments[m.instrument_id].ticker in BENCHMARK_TICKERS
    ]

    # ------------------------------------------------------------------ #
    # 3. Memory quote momentum from MemoryQuote table (last 1M change)
    # ------------------------------------------------------------------ #
    quote_change_pcts: list[float] = await _fetch_quote_momentum(db, latest_date)

    # ------------------------------------------------------------------ #
    # 4. Component calculations
    # ------------------------------------------------------------------ #
    # --- Quote momentum (±50 range, scaled to contribution domain) ---
    raw_quote = _avg(quote_change_pcts) if quote_change_pcts else _avg(
        [float(m.change_pct or 0) for m in memory_metrics]
    )
    quote_score = _clamp(raw_quote, -50.0, 50.0)

    # --- Equity momentum: Tier A 1M momentum ---
    raw_equity = _avg([float(m.momentum or 0) for m in tier_a])
    equity_score = _clamp(raw_equity, -50.0, 50.0)

    # --- Breadth: % of Tier A/B above MA20 (40pts) + MA60 (60pts) ---
    breadth_items: list[float] = []
    for m in tier_ab:
        ma_st = m.ma_state or {}
        item = (40.0 if ma_st.get("ma20") == "above" else 0.0) + (
            60.0 if ma_st.get("ma60") == "above" else 0.0
        )
        breadth_items.append(item)
    raw_breadth = _avg(breadth_items) / 2.0  # normalise to 0–50
    breadth_score = _clamp(raw_breadth, 0.0, 50.0)

    # --- Risk: negative for high vol + deep drawdown ---
    vol_penalty = -_avg([float(m.volatility or 0) for m in tier_a]) / 5.0
    # Use 3M momentum vs 1M as a drawdown proxy
    drawdown_penalty: list[float] = []
    for m in tier_a:
        m3 = metrics_3m_map.get(m.instrument_id)
        if m3:
            drawdown_penalty.append(
                float(m.change_pct or 0) - float(m3.change_pct or 0)
            )
    ddp = _avg(drawdown_penalty) / 10.0 if drawdown_penalty else 0.0
    risk_raw = vol_penalty + ddp
    risk_score = _clamp(risk_raw, -30.0, 0.0)

    # --- Relative strength: Tier-A basket vs benchmarks ---
    basket_mom = _avg([float(m.change_pct or 0) for m in tier_a])
    bench_mom = _avg([float(m.change_pct or 0) for m in benchmark_metrics])
    relative_raw = _clamp((basket_mom - bench_mom) / 4.0, -25.0, 25.0)
    relative_score = relative_raw

    # ------------------------------------------------------------------ #
    # 5. Combine
    # ------------------------------------------------------------------ #
    total = (
        50.0
        + quote_score   * 0.40
        + equity_score  * 0.25
        + breadth_score * 0.10
        + risk_score    * 0.15
        + relative_score * 0.10
    )
    total = _clamp(total, 0.0, 100.0)
    status = _status(total)

    # ------------------------------------------------------------------ #
    # 6. Narrative (Traditional Chinese)
    # ------------------------------------------------------------------ #
    top_drivers = _top_drivers(
        quote=quote_score, equity=equity_score, breadth=raw_breadth
    )
    breadth_pct = (
        int(100 * sum(1 for m in tier_ab if (m.ma_state or {}).get("ma60") == "above") / len(tier_ab))
        if tier_ab else 0
    )
    narrative: dict[str, str] = {
        "summary": (
            f"記憶體市場{_status_label(status)}（{total:.0f}分），"
            f"主要動能來自：{top_drivers}"
        ),
        "quote": (
            f"報價月漲跌 {raw_quote:+.1f}%"
            if quote_change_pcts
            else f"報價動能分數 {quote_score:.1f}"
        ),
        "equity": f"Tier A/B 股票 {breadth_pct}% 站上60日均線",
        "risk": (
            f"月波動率{'偏低' if vol_penalty > -3 else '偏高'}"
            f"（波動調整 {risk_score:.1f}）"
        ),
        "relative": (
            f"記憶體籃子1M超額指數基準 {basket_mom - bench_mom:+.1f}%"
        ),
    }

    # ------------------------------------------------------------------ #
    # 7. Upsert
    # ------------------------------------------------------------------ #
    payload: dict[str, Any] = {
        "score_date": latest_date,
        "total_score": Decimal(f"{total:.3f}"),
        "quote_momentum_score": Decimal(f"{quote_score:.3f}"),
        "equity_momentum_score": Decimal(f"{equity_score:.3f}"),
        "breadth_score": Decimal(f"{breadth_score:.3f}"),
        "risk_score": Decimal(f"{risk_score:.3f}"),
        "relative_strength_score": Decimal(f"{relative_score:.3f}"),
        "status": status,
        "narrative": narrative,
    }
    stmt = insert(MarketScore).values(payload)
    stmt = stmt.on_conflict_do_update(
        constraint=UPSERT_CONSTRAINT,
        set_={k: getattr(stmt.excluded, k) for k in payload if k != "score_date"},
    )
    await db.execute(stmt)
    await db.commit()

    logger.info(
        "compute_market_score – date=%s score=%.1f status=%s",
        latest_date,
        total,
        status,
    )
    return {"status": "success", "score": total, "status_label": status}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _upsert_default(db: AsyncSession) -> dict[str, Any]:
    """Upsert a neutral default score when no data is available."""
    from datetime import date as _date

    today = _date.today()
    payload: dict[str, Any] = {
        "score_date": today,
        "total_score": Decimal("50"),
        "quote_momentum_score": Decimal("0"),
        "equity_momentum_score": Decimal("0"),
        "breadth_score": Decimal("0"),
        "risk_score": Decimal("0"),
        "relative_strength_score": Decimal("0"),
        "status": "neutral",
        "narrative": {
            "summary": "資料不足，預設中性（50分）。",
            "quote": "N/A",
            "equity": "N/A",
            "risk": "N/A",
            "relative": "N/A",
        },
    }
    stmt = insert(MarketScore).values(payload)
    stmt = stmt.on_conflict_do_update(
        constraint=UPSERT_CONSTRAINT,
        set_={k: getattr(stmt.excluded, k) for k in payload if k != "score_date"},
    )
    await db.execute(stmt)
    await db.commit()
    return {"status": "no_data", "score": 50.0, "status_label": "neutral"}


async def _fetch_quote_momentum(
    db: AsyncSession, as_of: date
) -> list[float]:
    """Return 1M change-pct values from memory_quotes for DRAM/NAND products."""
    try:
        rows = list(
            (
                await db.scalars(
                    select(MemoryQuote)
                    .where(
                        MemoryQuote.snapshot_date <= as_of,
                        MemoryQuote.category.in_(["DRAM", "NAND"]),
                    )
                    .order_by(MemoryQuote.snapshot_date.desc())
                    .limit(50)
                )
            ).all()
        )
        return [float(r.change_pct) for r in rows if r.change_pct is not None]
    except Exception:
        return []


def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _status(score: float) -> str:
    if score <= 20:
        return "strong-bear"
    if score <= 40:
        return "bear"
    if score <= 60:
        return "neutral"
    if score <= 80:
        return "bull"
    return "strong-bull"


def _status_label(status: str) -> str:
    return {
        "strong-bear": "強熊",
        "bear": "偏熊",
        "neutral": "中性",
        "bull": "偏牛",
        "strong-bull": "強牛",
    }[status]


def _top_drivers(quote: float, equity: float, breadth: float) -> str:
    drivers: list[tuple[float, str]] = [
        (abs(quote), "報價動能"),
        (abs(equity), "核心股票動能"),
        (abs(breadth), "市場廣度"),
    ]
    drivers.sort(key=lambda x: x[0], reverse=True)
    return "、".join(d[1] for d in drivers[:2])

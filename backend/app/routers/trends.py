from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import EquityPrice, Instrument, MarketEvent, MemoryQuote

router = APIRouter(tags=["trends"])

# How far back the chart looks, per period selector.
PERIOD_DAYS = {"1W": 7, "1M": 31, "3M": 93, "6M": 186, "1Y": 366}


@router.get("/trends/chart")
async def trend_chart(period: str = Query(default="1M"), db: AsyncSession = Depends(get_db)) -> dict:
    """Return a normalised daily trend series (base = 100) with a real date axis.

    - ``stock``: an equal-weight basket index of the core memory instruments,
      built from real daily closes (each instrument normalised to its own first
      close in the window, then averaged per trading day).
    - ``dram`` / ``nand``: normalised average memory-quote price per snapshot
      date (populates as daily snapshots accumulate).
    The x-axis is the sorted union of real trading dates and quote snapshot
    dates within the selected period.
    """
    window = PERIOD_DAYS.get(period, 366)
    start = date.today() - timedelta(days=window)

    # ---- core memory basket (instruments that drive the score) ----
    core_ids = (
        await db.scalars(
            select(Instrument.id).where(Instrument.score_weight > 0, Instrument.is_active.is_(True))
        )
    ).all()
    if not core_ids:
        core_ids = (await db.scalars(select(Instrument.id).where(Instrument.is_active.is_(True)))).all()

    price_rows = (
        await db.execute(
            select(EquityPrice.instrument_id, EquityPrice.trade_date, EquityPrice.close)
            .where(EquityPrice.trade_date >= start, EquityPrice.instrument_id.in_(core_ids))
            .order_by(EquityPrice.trade_date.asc())
        )
    ).all()

    # Per-instrument first close = normalisation base.
    base_close: dict[int, float] = {}
    basket_sum: dict[date, float] = defaultdict(float)
    basket_cnt: dict[date, int] = defaultdict(int)
    for iid, trade_date, close in price_rows:
        if close is None:
            continue
        c = float(close)
        if iid not in base_close:
            base_close[iid] = c or 1.0
        basket_sum[trade_date] += c / (base_close[iid] or 1.0) * 100
        basket_cnt[trade_date] += 1
    basket = {d: round(basket_sum[d] / basket_cnt[d], 2) for d in basket_sum if basket_cnt[d]}

    # ---- DRAM / NAND normalised quote indices ----
    quote_rows = (
        await db.scalars(
            select(MemoryQuote).where(MemoryQuote.snapshot_date >= start).order_by(MemoryQuote.snapshot_date.asc())
        )
    ).all()

    def _category_index(category: str) -> dict[date, float]:
        per_date_sum: dict[date, float] = defaultdict(float)
        per_date_cnt: dict[date, int] = defaultdict(int)
        for row in quote_rows:
            if row.category != category or row.price_avg is None:
                continue
            per_date_sum[row.snapshot_date] += float(row.price_avg)
            per_date_cnt[row.snapshot_date] += 1
        avgs = {d: per_date_sum[d] / per_date_cnt[d] for d in per_date_sum if per_date_cnt[d]}
        if not avgs:
            return {}
        base = avgs[min(avgs)] or 1.0
        return {d: round(v / base * 100, 2) for d, v in avgs.items()}

    dram_index = _category_index("DRAM")
    nand_index = _category_index("NAND")

    # ---- unified, sorted date axis ----
    axis_dates = sorted(set(basket) | set(dram_index) | set(nand_index))

    points = [
        {
            "date": d.isoformat(),
            "dram": dram_index.get(d),
            "nand": nand_index.get(d),
            "stock": basket.get(d),
        }
        for d in axis_dates
    ]

    # 20-day moving average of the basket index.
    ma: list[dict] = []
    basket_series = [basket.get(d) for d in axis_dates]
    for idx, d in enumerate(axis_dates):
        window_vals = [v for v in basket_series[max(0, idx - 19): idx + 1] if v is not None]
        ma.append(
            {
                "date": d.isoformat(),
                "ma20": round(sum(window_vals) / len(window_vals), 2) if window_vals else None,
                "ma60": None,
                "ma120": None,
            }
        )

    event_rows = (
        await db.scalars(
            select(MarketEvent).where(MarketEvent.event_date >= start).order_by(MarketEvent.event_date.asc())
        )
    ).all()
    events = [
        {"date": row.event_date.isoformat(), "label": row.title, "description": row.description or "", "type": row.category}
        for row in event_rows
    ]
    return {"period": period, "points": points, "ma": ma, "events": events}

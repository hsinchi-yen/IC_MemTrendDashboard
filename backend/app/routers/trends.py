from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import EquityPrice, MarketEvent, MemoryQuote

router = APIRouter(tags=["trends"])


@router.get("/trends/chart")
async def trend_chart(period: str = Query(default="1M"), db: AsyncSession = Depends(get_db)) -> dict:
    quote_rows = (await db.scalars(select(MemoryQuote).order_by(MemoryQuote.snapshot_date.asc()))).all()
    price_rows = (await db.scalars(select(EquityPrice).order_by(EquityPrice.trade_date.asc()))).all()
    event_rows = (await db.scalars(select(MarketEvent).order_by(MarketEvent.event_date.asc()))).all()

    def _series(values: list[float]) -> list[float]:
        if not values:
            return []
        base = values[0] or 1
        return [round((value / base) * 100, 2) for value in values]

    dates = [row.snapshot_date.isoformat() for row in quote_rows[:180]] or [row.trade_date.isoformat() for row in price_rows[:180]]
    dram_values = [float(row.price_avg or 0) for row in quote_rows if row.category == "DRAM"][:180]
    nand_values = [float(row.price_avg or 0) for row in quote_rows if row.category == "NAND"][:180]
    stock_values = [float(row.close or 0) for row in price_rows[:180]]

    points = [
        {"date": d, "dram": dram_values[i] if i < len(dram_values) else None, "nand": nand_values[i] if i < len(nand_values) else None, "stock": stock_values[i] if i < len(stock_values) else None}
        for i, d in enumerate(dates)
    ]
    ma = []
    for idx, d in enumerate(dates):
        slice_values = stock_values[max(0, idx - 19): idx + 1]
        ma.append({"date": d, "ma20": round(sum(slice_values) / len(slice_values), 2) if slice_values else None, "ma60": None, "ma120": None})

    events = [
        {"date": row.event_date.isoformat(), "label": row.title, "description": row.description or "", "type": row.category}
        for row in event_rows
    ]
    return {"period": period, "points": points, "ma": ma, "events": events}
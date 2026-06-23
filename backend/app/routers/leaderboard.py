from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import EquityPrice, Instrument, MemoryQuote

router = APIRouter(tags=["leaderboard"])


@router.get("/leaderboard")
async def leaderboard(period: str = Query(default="1M"), db: AsyncSession = Depends(get_db)) -> dict:
    quote_rows = (await db.scalars(select(MemoryQuote).order_by(MemoryQuote.snapshot_date.desc()).limit(20))).all()
    price_rows = (await db.scalars(select(EquityPrice).order_by(EquityPrice.trade_date.desc()).limit(50))).all()
    instruments = (await db.scalars(select(Instrument).order_by(Instrument.id.asc()).limit(20))).all()

    quote_top = [
        {"id": str(row.id), "label": row.product, "change_pct": float(row.change_pct or 0), "spark": [float(row.price_avg or 0)], "category": "quote"}
        for row in quote_rows[:5]
    ]
    quote_bottom = list(reversed(quote_top[-5:]))
    stock_top = [
        {"id": str(row.id), "label": instrument.ticker, "ticker": instrument.ticker, "change_pct": float(row.close or 0), "spark": [float(row.close or 0)], "category": "stock"}
        for row, instrument in zip(price_rows[:5], instruments[:5])
    ]
    abnormal = [item for item in stock_top if abs(item["change_pct"]) > 5]
    return {"period": period, "quote_top": quote_top, "quote_bottom": quote_bottom, "stock_top": stock_top, "stock_bottom": [], "abnormal": abnormal}

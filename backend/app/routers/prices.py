from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import EquityPrice, Instrument
from app.schemas import PaginatedResponse, PriceRow

router = APIRouter(tags=["prices"])

PERIOD_DAYS = {"1W": 7, "1M": 31, "3M": 93, "6M": 186, "1Y": 366}


@router.get("/prices/{ticker}")
async def get_prices(
    ticker: str,
    market: str,
    start_date: date | None = None,
    end_date: date | None = None,
    period: str | None = None,
    page: int = 1,
    page_size: int = 100,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    instrument = await db.scalar(select(Instrument).where(Instrument.ticker == ticker, Instrument.market == market))
    if not instrument:
        raise HTTPException(status_code=404, detail="instrument_not_found")
    if period and not start_date:
        start_date = date.today() - timedelta(days=PERIOD_DAYS.get(period, 366))
    stmt = select(EquityPrice).where(EquityPrice.instrument_id == instrument.id)
    if start_date:
        stmt = stmt.where(EquityPrice.trade_date >= start_date)
    if end_date:
        stmt = stmt.where(EquityPrice.trade_date <= end_date)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0
    rows = (
        await db.scalars(
            stmt.order_by(EquityPrice.trade_date.desc()).offset((page - 1) * page_size).limit(page_size)
        )
    ).all()
    data = [
        PriceRow(
            date=row.trade_date,
            open=row.open,
            high=row.high,
            low=row.low,
            close=row.close,
            volume=row.volume,
        )
        for row in rows
    ]
    return PaginatedResponse(total_count=total, data=data)

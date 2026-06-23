import csv
from io import StringIO

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import EquityPrice, Instrument, TrendMetric
from app.schemas import PaginatedResponse

router = APIRouter(tags=["query"])


@router.get("/query/stock_table")
async def stock_table(
    request: Request,
    market: str | None = None,
    tier: str | None = None,
    tag: str | None = None,
    search: str | None = None,
    sort_by: str = "ticker",
    sort_order: str = "asc",
    page: int = 1,
    page_size: int = 100,
    db: AsyncSession = Depends(get_db),
):
    latest_price = (
        select(EquityPrice.instrument_id, func.max(EquityPrice.trade_date).label("trade_date"))
        .group_by(EquityPrice.instrument_id)
        .subquery()
    )
    latest_metric = (
        select(TrendMetric.instrument_id, func.max(TrendMetric.as_of_date).label("as_of_date"))
        .group_by(TrendMetric.instrument_id)
        .subquery()
    )
    stmt = (
        select(
            Instrument.ticker,
            Instrument.name,
            Instrument.market,
            Instrument.tier,
            Instrument.supply_chain_tag,
            EquityPrice.close,
            TrendMetric.change_pct,
            TrendMetric.momentum,
            TrendMetric.ma_state,
        )
        .join(latest_price, latest_price.c.instrument_id == Instrument.id, isouter=True)
        .join(
            EquityPrice,
            and_(
                EquityPrice.instrument_id == latest_price.c.instrument_id,
                EquityPrice.trade_date == latest_price.c.trade_date,
            ),
            isouter=True,
        )
        .join(latest_metric, latest_metric.c.instrument_id == Instrument.id, isouter=True)
        .join(
            TrendMetric,
            and_(
                TrendMetric.instrument_id == latest_metric.c.instrument_id,
                TrendMetric.as_of_date == latest_metric.c.as_of_date,
                TrendMetric.period == "1M",
            ),
            isouter=True,
        )
    )
    if market:
        stmt = stmt.where(Instrument.market == market)
    if tier:
        stmt = stmt.where(Instrument.tier == tier)
    if tag:
        stmt = stmt.where(Instrument.supply_chain_tag == tag)
    if search:
        stmt = stmt.where(or_(Instrument.ticker.ilike(f"%{search}%"), Instrument.name.ilike(f"%{search}%")))
    sort_column = getattr(Instrument, sort_by, Instrument.ticker)
    if sort_by == "change_pct":
        sort_column = TrendMetric.change_pct
    # Keep rows that still lack price/metric data at the bottom regardless of
    # sort direction, so populated instruments surface first.
    if sort_order == "desc":
        stmt = stmt.order_by(desc(sort_column).nulls_last())
    else:
        stmt = stmt.order_by(sort_column.nulls_last())
    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = (await db.execute(stmt.offset((page - 1) * page_size).limit(page_size))).all()
    data = [
        {
            "ticker": row.ticker,
            "name": row.name,
            "market": row.market,
            "tier": row.tier,
            "tag": row.supply_chain_tag,
            "latest_close": row.close,
            "change_pct_1m": row.change_pct,
            "momentum": row.momentum,
            "ma_state": row.ma_state,
        }
        for row in rows
    ]
    if "text/csv" in request.headers.get("accept", ""):
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=list(data[0].keys()) if data else ["ticker"])
        writer.writeheader()
        writer.writerows(data)
        return PlainTextResponse(output.getvalue(), media_type="text/csv")
    return PaginatedResponse(total_count=total, data=data)

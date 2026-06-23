from datetime import date
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import MemoryQuote
from app.schemas import PaginatedResponse, QuoteRow

router = APIRouter(tags=["quotes"])


@router.get("/quotes")
async def get_quotes(
    category: str | None = None,
    product: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 100,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    stmt = select(MemoryQuote)
    if category:
        stmt = stmt.where(MemoryQuote.category == category)
    if product:
        stmt = stmt.where(MemoryQuote.product == product)
    if start_date:
        stmt = stmt.where(MemoryQuote.snapshot_date >= start_date)
    if end_date:
        stmt = stmt.where(MemoryQuote.snapshot_date <= end_date)
    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = (
        await db.scalars(
            stmt.order_by(MemoryQuote.snapshot_date.desc()).offset((page - 1) * page_size).limit(page_size)
        )
    ).all()
    data = [
        QuoteRow(
            product=row.product,
            category=row.category,
            price_type=row.price_type,
            price_avg=row.price_avg,
            change_pct=row.change_pct,
            snapshot_date=row.snapshot_date,
        )
        for row in rows
    ]
    return PaginatedResponse(total_count=total, data=data)


@router.get("/quotes/heatmap")
async def quote_heatmap(db: AsyncSession = Depends(get_db)) -> list[dict]:
    rows = (await db.scalars(select(MemoryQuote).order_by(MemoryQuote.snapshot_date.asc()))).all()
    grouped: dict[str, list[MemoryQuote]] = defaultdict(list)
    for row in rows:
        grouped[row.product].append(row)

    periods = ["1D", "1W", "1M", "3M", "6M", "1Y"]
    lookbacks = {"1D": 1, "1W": 5, "1M": 21, "3M": 63, "6M": 126, "1Y": 252}
    output: list[dict] = []
    for product, product_rows in grouped.items():
        latest = product_rows[-1]
        values = [float(row.price_avg or 0) for row in product_rows]
        changes: dict[str, float | None] = {}
        for period in periods:
          lookback = lookbacks[period]
          if len(values) > lookback and values[-(lookback + 1)]:
              base = values[-(lookback + 1)]
              changes[period] = round(((values[-1] - base) / base) * 100, 2) if base else None
          else:
              changes[period] = None
        output.append(
            {
                "id": product,
                "label": product,
                "label_en": product,
                "category": latest.category,
                "changes": changes,
                "definition": f"{latest.category} {latest.price_type or 'spot'}",
            }
        )
    return output


@router.get("/quotes/{quote_id}/sparkline")
async def quote_sparkline(quote_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    rows = (
        await db.scalars(
            select(MemoryQuote)
            .where(MemoryQuote.product == quote_id)
            .order_by(MemoryQuote.snapshot_date.asc())
            .limit(30)
        )
    ).all()
    return {
        "dates": [row.snapshot_date.isoformat() for row in rows],
        "values": [float(row.price_avg or 0) for row in rows],
    }

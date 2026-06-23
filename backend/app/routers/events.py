from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import MarketEvent
from app.schemas import MarketEventIn, MarketEventOut

router = APIRouter(tags=["events"])


@router.get("/events")
async def list_events(
    start_date: date | None = None,
    end_date: date | None = None,
    ticker: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[MarketEventOut]:
    stmt = select(MarketEvent)
    if start_date:
        stmt = stmt.where(MarketEvent.event_date >= start_date)
    if end_date:
        stmt = stmt.where(MarketEvent.event_date <= end_date)
    rows = (await db.scalars(stmt.order_by(MarketEvent.event_date.desc()))).all()
    if ticker:
        rows = [row for row in rows if row.related_tickers and ticker in row.related_tickers]
    return [MarketEventOut.model_validate(row) for row in rows]


@router.post("/events")
async def create_event(payload: MarketEventIn, db: AsyncSession = Depends(get_db)) -> MarketEventOut:
    event = MarketEvent(**payload.model_dump())
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return MarketEventOut.model_validate(event)


@router.patch("/events/{event_id}")
async def update_event(event_id: int, payload: MarketEventIn, db: AsyncSession = Depends(get_db)) -> MarketEventOut:
    event = await db.get(MarketEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event_not_found")
    for key, value in payload.model_dump().items():
        setattr(event, key, value)
    await db.commit()
    await db.refresh(event)
    return MarketEventOut.model_validate(event)


@router.delete("/events/{event_id}", status_code=204)
async def delete_event(event_id: int, db: AsyncSession = Depends(get_db)) -> None:
    event = await db.get(MarketEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="event_not_found")
    await db.delete(event)
    await db.commit()

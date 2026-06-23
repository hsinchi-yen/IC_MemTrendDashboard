from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Query

from app.db.database import get_db
from app.models import Instrument
from app.schemas import InstrumentOut

router = APIRouter(tags=["instruments"])


@router.get("/instruments")
async def list_instruments(
    market: str | None = None,
    tier: str | None = None,
    tag: str | None = None,
    is_active: bool | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[InstrumentOut]:
    stmt = select(Instrument)
    if market:
        stmt = stmt.where(Instrument.market == market)
    if tier:
        stmt = stmt.where(Instrument.tier == tier)
    if tag:
        stmt = stmt.where(Instrument.supply_chain_tag == tag)
    if is_active is not None:
        stmt = stmt.where(Instrument.is_active == is_active)
    result = await db.scalars(stmt.order_by(Instrument.market, Instrument.ticker))
    return [InstrumentOut.model_validate(item) for item in result.all()]

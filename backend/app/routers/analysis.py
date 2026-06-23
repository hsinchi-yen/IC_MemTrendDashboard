from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import CorrelationMatrix, Instrument

router = APIRouter(tags=["analysis"])


@router.get("/analysis/correlation")
async def correlation_matrix(window: int = Query(default=60), db: AsyncSession = Depends(get_db)) -> list[dict]:
    rows = (await db.scalars(select(CorrelationMatrix).where(CorrelationMatrix.window_days == window))).all()
    instruments = {item.id: item.ticker for item in (await db.scalars(select(Instrument))).all()}
    return [
        {
            "stock": instruments.get(row.instrument_id, str(row.instrument_id)),
            "quote": row.quote_product,
            "value": float(row.coefficient) if row.coefficient is not None else None,
            "window": row.window_days,
        }
        for row in rows
    ]


@router.get("/analysis/supply-chain")
async def supply_chain(db: AsyncSession = Depends(get_db)) -> dict:
    instruments = (
        await db.scalars(
            select(Instrument).where(Instrument.is_active.is_(True)).order_by(Instrument.market, Instrument.ticker)
        )
    ).all()
    nodes = [
        {
            "id": f"{item.market}-{item.ticker}",
            "ticker": item.ticker,
            "name": item.name or item.ticker,
            "layer": item.supply_chain_tag or "maker",
            "tier": item.tier,
            "change_1d": None,
        }
        for item in instruments[:30]
    ]
    edges = [{"source": nodes[idx]["id"], "target": nodes[idx + 1]["id"]} for idx in range(max(0, len(nodes) - 1))]
    return {"nodes": nodes, "edges": edges}

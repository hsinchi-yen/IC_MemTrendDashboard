from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import MarketScore, MemoryQuote

router = APIRouter(tags=["indicators"])


@router.get("/indicators/definitions")
async def indicator_definitions() -> dict:
    return {
        "periods": {
            "1D": "1 trading day",
            "1W": "5 trading days",
            "1M": "21 trading days",
            "3M": "63 trading days",
            "6M": "126 trading days",
            "1Y": "252 trading days",
        },
        "metrics": {
            "change_pct": "Percentage change against the period baseline.",
            "momentum": "Composite score of 1M, 3M, and moving-average strength.",
            "streak": "Consecutive up or down sessions.",
        },
    }


@router.get("/indicators/topbar")
async def topbar_indicators(db: AsyncSession = Depends(get_db)) -> dict:
    latest_score = await db.scalar(select(MarketScore).order_by(MarketScore.score_date.desc()).limit(1))
    quote_rows = (await db.scalars(select(MemoryQuote).order_by(MemoryQuote.snapshot_date.desc()).limit(30))).all()
    dram_quotes = [float(row.change_pct or 0) for row in quote_rows if row.category == "DRAM"]
    nand_quotes = [float(row.change_pct or 0) for row in quote_rows if row.category == "NAND"]
    dram_change = round(sum(dram_quotes) / len(dram_quotes), 2) if dram_quotes else 0.0
    nand_change = round(sum(nand_quotes) / len(nand_quotes), 2) if nand_quotes else 0.0
    stock_change = float(latest_score.quote_momentum_score or 0) if latest_score else 0.0
    updated_at = latest_score.computed_at if latest_score else datetime.now(timezone.utc)
    return {
        "dram": {"label": "DRAM", "change_pct": dram_change, "direction": "up" if dram_change > 0 else "down" if dram_change < 0 else "flat"},
        "nand": {"label": "NAND", "change_pct": nand_change, "direction": "up" if nand_change > 0 else "down" if nand_change < 0 else "flat"},
        "stock_basket": {"label": "股票籃子", "change_pct": stock_change, "direction": "up" if stock_change > 0 else "down" if stock_change < 0 else "flat"},
        "updated_at": updated_at,
    }

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models import Instrument, MarketScore, TrendMetric
from app.schemas import PaginatedResponse, ScoreRow, TrendMetricRow

router = APIRouter(tags=["scores"])


@router.get("/score")
async def get_scores(
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 100,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    stmt = select(MarketScore)
    if start_date:
        stmt = stmt.where(MarketScore.score_date >= start_date)
    if end_date:
        stmt = stmt.where(MarketScore.score_date <= end_date)
    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = (
        await db.scalars(stmt.order_by(MarketScore.score_date.desc()).offset((page - 1) * page_size).limit(page_size))
    ).all()
    data = [
        ScoreRow(
            score_date=row.score_date,
            total_score=row.total_score,
            status=row.status,
            narrative=row.narrative,
            sub_scores={
                "quote_momentum_score": row.quote_momentum_score,
                "equity_momentum_score": row.equity_momentum_score,
                "breadth_score": row.breadth_score,
                "risk_score": row.risk_score,
                "relative_strength_score": row.relative_strength_score,
            },
        )
        for row in rows
    ]
    return PaginatedResponse(total_count=total, data=data)


@router.get("/score/latest")
async def get_latest_score(db: AsyncSession = Depends(get_db)) -> ScoreRow:
    row = await db.scalar(select(MarketScore).order_by(MarketScore.score_date.desc()).limit(1))
    if not row:
        raise HTTPException(status_code=404, detail="score_not_found")
    return ScoreRow(
        score_date=row.score_date,
        total_score=row.total_score,
        status=row.status,
        narrative=row.narrative,
        sub_scores={
            "quote_momentum_score": row.quote_momentum_score,
            "equity_momentum_score": row.equity_momentum_score,
            "breadth_score": row.breadth_score,
            "risk_score": row.risk_score,
            "relative_strength_score": row.relative_strength_score,
        },
    )


@router.get("/trend_metrics/{ticker}")
async def get_trend_metrics(
    ticker: str,
    market: str,
    period: str | None = None,
    as_of_date: date | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[TrendMetricRow]:
    instrument = await db.scalar(select(Instrument).where(Instrument.ticker == ticker, Instrument.market == market))
    if not instrument:
        raise HTTPException(status_code=404, detail="instrument_not_found")
    stmt = select(TrendMetric).where(TrendMetric.instrument_id == instrument.id)
    if period:
        stmt = stmt.where(TrendMetric.period == period)
    if as_of_date:
        stmt = stmt.where(TrendMetric.as_of_date == as_of_date)
    rows = (await db.scalars(stmt.order_by(TrendMetric.as_of_date.desc(), TrendMetric.period))).all()
    return [
        TrendMetricRow(
            as_of_date=row.as_of_date,
            period=row.period,
            change_pct=row.change_pct,
            direction=row.direction,
            momentum=row.momentum,
            ma_state=row.ma_state,
            volatility=row.volatility,
            streak=row.streak,
            normalized_index=row.normalized_index,
            narrative=row.narrative,
        )
        for row in rows
    ]

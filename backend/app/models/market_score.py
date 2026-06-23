from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, JSON, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MarketScore(Base):
    __tablename__ = "market_scores"
    __table_args__ = (UniqueConstraint("score_date", name="uq_market_score_date"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    score_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    total_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    quote_momentum_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    equity_momentum_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    breadth_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    risk_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    relative_strength_score: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    status: Mapped[str | None] = mapped_column(String(20))
    narrative: Mapped[dict | None] = mapped_column(JSON)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

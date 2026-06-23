from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, JSON, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TrendMetric(Base):
    __tablename__ = "trend_metrics"
    __table_args__ = (UniqueConstraint("instrument_id", "as_of_date", "period", name="uq_trend_metric_instrument_date_period"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), nullable=False, index=True)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(5), nullable=False)
    change_pct: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    change_abs: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    direction: Mapped[str | None] = mapped_column(String(10))
    momentum: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    ma_state: Mapped[dict | None] = mapped_column(JSON)
    volatility: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    hi_lo_flag: Mapped[dict | None] = mapped_column(JSON)
    streak: Mapped[int | None]
    acceleration: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    normalized_index: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    narrative: Mapped[str | None]
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

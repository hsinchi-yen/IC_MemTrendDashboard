from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CorrelationMatrix(Base):
    __tablename__ = "correlation_matrix"
    __table_args__ = (UniqueConstraint("instrument_id", "quote_product", "window_days", "as_of_date", name="uq_corr_matrix_key"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    instrument_id: Mapped[int] = mapped_column(ForeignKey("instruments.id"), nullable=False)
    quote_product: Mapped[str] = mapped_column(String(50), nullable=False)
    window_days: Mapped[int]
    coefficient: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

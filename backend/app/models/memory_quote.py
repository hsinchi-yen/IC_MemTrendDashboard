from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MemoryQuote(Base):
    __tablename__ = "memory_quotes"
    __table_args__ = (UniqueConstraint("product", "price_type", "snapshot_date", name="uq_memory_quote_product_type_date"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    price_type: Mapped[str | None] = mapped_column(String(20))
    price_high: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    price_low: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    price_avg: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    change_pct: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    currency: Mapped[str] = mapped_column(String(5), default="USD", nullable=False)
    unit: Mapped[str | None] = mapped_column(String(20))
    source: Mapped[str | None] = mapped_column(String(30))
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

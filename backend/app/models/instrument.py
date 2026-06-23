from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Instrument(Base):
    __tablename__ = "instruments"
    __table_args__ = (UniqueConstraint("ticker", "market", name="uq_instrument_ticker_market"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(20), nullable=False)
    market: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str | None] = mapped_column(String(100))
    name_en: Mapped[str | None] = mapped_column(String(100))
    tier: Mapped[str] = mapped_column(String(5), nullable=False)
    supply_chain_tag: Mapped[str | None] = mapped_column(String(50))
    currency: Mapped[str | None] = mapped_column(String(5))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    score_weight: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0"), nullable=False)
    score_only_observe: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

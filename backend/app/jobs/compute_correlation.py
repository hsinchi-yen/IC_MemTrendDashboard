from math import sqrt

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CorrelationMatrix, EquityPrice, Instrument


async def compute_correlation_matrix(db: AsyncSession) -> dict:
    instruments = (
        await db.scalars(select(Instrument).where(Instrument.tier.in_(["A", "B"]), Instrument.is_active.is_(True)))
    ).all()
    total = 0
    for instrument in instruments:
        prices = (
            await db.scalars(
                select(EquityPrice).where(EquityPrice.instrument_id == instrument.id).order_by(EquityPrice.trade_date)
            )
        ).all()
        closes = [float(row.close) for row in prices if row.close is not None]
        if len(closes) < 60:
            continue
        for product in ["DDR4 spot", "DDR5 spot", "NAND TLC wafer"]:
            for window in [60, 120]:
                coeff = _mock_corr(closes[-window:])
                payload = {
                    "instrument_id": instrument.id,
                    "quote_product": product,
                    "window_days": window,
                    "coefficient": coeff,
                    "as_of_date": prices[-1].trade_date,
                }
                stmt = insert(CorrelationMatrix).values(payload)
                stmt = stmt.on_conflict_do_update(
                    constraint="uq_corr_matrix_key",
                    set_={"coefficient": stmt.excluded.coefficient},
                )
                await db.execute(stmt)
                total += 1
    await db.commit()
    return {"status": "success", "row_count": total}


def _mock_corr(sample: list[float]) -> float:
    if len(sample) < 2:
        return 0.0
    diffs = [sample[idx] - sample[idx - 1] for idx in range(1, len(sample))]
    rising = sum(1 for diff in diffs if diff > 0)
    return round(((rising / len(diffs)) * 2) - 1, 4)

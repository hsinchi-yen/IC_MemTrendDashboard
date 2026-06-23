from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.jobs.common import create_source_run, finish_source_run, get_instruments_by_market, get_last_trade_date, normalize_ohlcv_rows, upsert_equity_prices
from app.services.stooq_client import fetch_stooq_csv
from app.services.yfinance_client import fetch_yfinance_history


def _kr_stooq_symbol(ticker: str) -> str:
    return f"{ticker.split('.')[0].lower()}.kr"


async def ingest_kr_stocks(db: AsyncSession, trigger: str = "manual") -> dict:
    run = await create_source_run(db, "kr_multi_source", trigger)
    instruments = await get_instruments_by_market(db, "KR")
    total_rows = success = fail = 0
    for instrument in instruments:
        last_date = await get_last_trade_date(db, instrument.id)
        start_date = (last_date + timedelta(days=1)) if last_date else (date.today() - timedelta(days=365))
        rows = await fetch_yfinance_history(instrument.ticker, start_date, date.today())
        source = "yfinance"
        if not rows:
            rows = await fetch_stooq_csv(_kr_stooq_symbol(instrument.ticker))
            source = "stooq"
        if not rows:
            fail += 1
            continue
        inserted = await upsert_equity_prices(db, instrument.id, source, normalize_ohlcv_rows(rows))
        total_rows += inserted
        success += 1
    status = "success" if fail == 0 else "partial"
    await finish_source_run(db, run, status, total_rows, success, fail, progress={"current_source": "kr_multi_source"})
    return {"status": status, "row_count": total_rows}

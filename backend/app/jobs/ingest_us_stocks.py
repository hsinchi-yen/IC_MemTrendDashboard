from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.jobs.common import (
    create_source_run,
    finish_source_run,
    get_instruments_by_market,
    get_last_trade_date,
    normalize_ohlcv_rows,
    upsert_equity_prices,
)
from app.services.alpha_vantage_client import fetch_alpha_vantage_daily
from app.services.finmind_client import fetch_finmind
from app.services.http_utils import QuotaExceededError, with_retries
from app.services.stooq_client import fetch_stooq_csv
from app.services.yfinance_client import fetch_yfinance_history


async def ingest_us_stocks(db: AsyncSession, trigger: str = "manual", finmind_token: str | None = None) -> dict:
    run = await create_source_run(db, "us_multi_source", trigger)
    instruments = await get_instruments_by_market(db, "US")
    total_rows = success = fail = 0
    for instrument in instruments:
        last_date = await get_last_trade_date(db, instrument.id)
        start_date = (last_date + timedelta(days=1)) if last_date else (date.today() - timedelta(days=365))
        rows = []
        source = None
        # yfinance first: reliable, token-free coverage for US tickers.
        try:
            rows = await fetch_yfinance_history(instrument.ticker, start_date, date.today())
            source = "yfinance" if rows else None
        except Exception:
            rows = []
        if not rows:
            try:
                rows = await with_retries(lambda: fetch_finmind("USStockPrice", instrument.ticker, start_date, date.today(), token=finmind_token))
                source = "finmind"
            except Exception:
                try:
                    rows = await fetch_stooq_csv(f"{instrument.ticker.lower()}.us")
                    source = "stooq"
                except Exception:
                    rows = await fetch_alpha_vantage_daily(instrument.ticker)
                    source = "alphavantage" if rows else None
        if not rows or not source:
            fail += 1
            continue
        inserted = await upsert_equity_prices(db, instrument.id, source, normalize_ohlcv_rows(rows))
        total_rows += inserted
        success += 1
    status = "success" if fail == 0 else "partial"
    await finish_source_run(db, run, status, total_rows, success, fail, progress={"current_source": "us_multi_source"})
    return {"status": status, "row_count": total_rows}

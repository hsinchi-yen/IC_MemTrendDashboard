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
from app.services.finmind_client import fetch_finmind
from app.services.http_utils import QuotaExceededError, with_retries


async def ingest_tw_stocks(db: AsyncSession, trigger: str = "manual") -> dict:
    run = await create_source_run(db, "tw_finmind", trigger)
    instruments = await get_instruments_by_market(db, "TW")
    total_rows = success = fail = 0
    try:
        for index, instrument in enumerate(instruments, start=1):
            last_date = await get_last_trade_date(db, instrument.id)
            start_date = (last_date + timedelta(days=1)) if last_date else (date.today() - timedelta(days=365))
            try:
                rows = await with_retries(
                    lambda: fetch_finmind("TaiwanStockPrice", instrument.ticker, start_date, date.today())
                )
                inserted = await upsert_equity_prices(db, instrument.id, "finmind", normalize_ohlcv_rows(rows))
                total_rows += inserted
                success += 1
            except QuotaExceededError:
                await finish_source_run(db, run, "quota_exceeded", total_rows, success, fail, "quota_exceeded")
                return {"status": "quota_exceeded", "row_count": total_rows}
            except Exception as exc:  # noqa: BLE001
                fail += 1
                run.progress = {"current_source": "tw_finmind", "current_ticker": instrument.ticker, "index": index}
                run.error_msg = str(exc)
                await db.commit()
        status = "success" if fail == 0 else "partial"
        await finish_source_run(db, run, status, total_rows, success, fail, progress={"current_source": "tw_finmind"})
        return {"status": status, "row_count": total_rows, "success_count": success, "fail_count": fail}
    except Exception as exc:  # noqa: BLE001
        await finish_source_run(db, run, "fail", total_rows, success, fail + 1, str(exc))
        return {"status": "fail", "row_count": total_rows, "error": str(exc)}

import csv
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.jobs.common import create_source_run, finish_source_run, upsert_memory_quotes
from app.services.memory_quote_parser import fetch_memory_quote_tables


async def ingest_memory_quotes(db: AsyncSession, trigger: str = "manual", from_csv: str | None = None) -> dict:
    run = await create_source_run(db, "memory_quotes", trigger)
    try:
        if from_csv:
            rows = _rows_from_csv(Path(from_csv))
        else:
            parsed = await fetch_memory_quote_tables()
            rows = _rows_from_quotes(parsed.get("quotes", []))
        inserted = await upsert_memory_quotes(db, rows)
        status = "success" if inserted else "empty"
        await finish_source_run(db, run, status, inserted, inserted, 0)
        return {"status": status, "row_count": inserted}
    except Exception as exc:  # noqa: BLE001
        await finish_source_run(db, run, "fail", 0, 0, 1, str(exc))
        return {"status": "fail", "error": str(exc)}


def _rows_from_quotes(quotes: list[dict]) -> list[dict]:
    """Map parser output (real prices) into MemoryQuote upsert rows."""
    today = date.today()
    now = datetime.now(timezone.utc)
    rows = []
    for q in quotes:
        if not q.get("product"):
            continue
        rows.append(
            {
                "product": q["product"],
                "category": q.get("category", "DRAM"),
                "price_type": q.get("price_type", "spot"),
                "price_high": q.get("price_high"),
                "price_low": q.get("price_low"),
                "price_avg": q.get("price_avg"),
                "change_pct": q.get("change_pct"),
                "currency": "USD",
                "unit": None,
                "source": "dramexchange",
                "snapshot_date": today,
                "fetched_at": now,
            }
        )
    return rows


def _rows_from_csv(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "product": row["product"],
                    "category": row.get("category", "DRAM"),
                    "price_type": row.get("price_type"),
                    "price_high": row.get("price_high"),
                    "price_low": row.get("price_low"),
                    "price_avg": row.get("price_avg"),
                    "change_pct": row.get("change_pct"),
                    "currency": row.get("currency", "USD"),
                    "unit": row.get("unit"),
                    "source": "manual",
                    "snapshot_date": row["snapshot_date"],
                    "fetched_at": datetime.now(timezone.utc),
                }
            )
    return rows

#!/usr/bin/env python3
"""
scripts/data_import/load_real_data.py

One-shot REAL-DATA loader / verifier.

1. Creates all tables (init_db).
2. Seeds the full instrument universe from instruments_seed.json (ORM upsert).
3. Runs the real ingestion pipeline:
     - real equity prices via yfinance (US / KR / JP / TW)
     - real DRAM/NAND quotes scraped from DRAMeXchange (incl. DDR3)
     - trend metrics, market score, alert evaluation
4. Prints a verification summary straight from the database.

Usage (PowerShell):
    $env:DATABASE_URL="postgresql+asyncpg://memdash:changeme@localhost:5544/memdash"
    $env:PYTHONPATH="backend"
    python scripts/data_import/load_real_data.py --markets US,TW --limit 6

Pass --markets to restrict which equity markets to ingest, and --limit to cap
the number of instruments per market (handy for a fast smoke verification).
Omit both to ingest the entire universe.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy import func, select

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_SEED_JSON = _PROJECT_ROOT / "scripts" / "data_import" / "instruments_seed.json"


async def _seed_instruments(db) -> int:
    from app.models import Instrument

    instruments = json.loads(_SEED_JSON.read_text(encoding="utf-8"))
    existing = {
        (i.ticker, i.market)
        for i in (await db.scalars(select(Instrument))).all()
    }
    added = 0
    for row in instruments:
        key = (row["ticker"], row["market"])
        if key in existing:
            continue
        db.add(Instrument(
            ticker=row["ticker"], market=row["market"], name=row.get("name"),
            name_en=row.get("name_en"), tier=row.get("tier", "C"),
            supply_chain_tag=row.get("supply_chain_tag"), currency=row.get("currency"),
            is_active=bool(row.get("is_active", True)),
            score_weight=row.get("score_weight", 0) or 0,
            score_only_observe=bool(row.get("score_only_observe", False)),
        ))
        added += 1
    await db.commit()
    return added


async def _ingest_market(db, market: str, limit: int | None) -> dict:
    """Ingest a single market, optionally limited to N instruments."""
    from app.jobs.ingest_us_stocks import ingest_us_stocks
    from app.jobs.ingest_tw_stocks import ingest_tw_stocks
    from app.jobs.ingest_jp_stocks import ingest_jp_stocks
    from app.jobs.ingest_kr_stocks import ingest_kr_stocks
    from app.models import Instrument

    funcs = {"US": ingest_us_stocks, "TW": ingest_tw_stocks,
             "JP": ingest_jp_stocks, "KR": ingest_kr_stocks}

    if limit:
        # Temporarily deactivate instruments beyond the limit so the existing
        # job (which filters on is_active) only processes the first N.
        ids = (await db.scalars(
            select(Instrument.id).where(Instrument.market == market, Instrument.is_active.is_(True))
            .order_by(Instrument.score_weight.desc(), Instrument.id).offset(limit)
        )).all()
        if ids:
            for inst in (await db.scalars(select(Instrument).where(Instrument.id.in_(ids)))).all():
                inst.is_active = False
            await db.commit()

    result = await funcs[market](db, trigger="manual")
    return {market: result}


async def main(markets: list[str], limit: int | None) -> None:
    from app.db.database import AsyncSessionLocal, init_db
    from app.jobs.compute_trend_metrics import compute_trend_metrics
    from app.jobs.compute_market_score import compute_market_score
    from app.jobs.ingest_memory_quotes import ingest_memory_quotes
    from app.models import EquityPrice, Instrument, MarketScore, MemoryQuote, TrendMetric

    print("→ init_db (create tables) …")
    await init_db()

    async with AsyncSessionLocal() as db:
        added = await _seed_instruments(db)
        total_inst = await db.scalar(select(func.count()).select_from(Instrument))
        print(f"→ seeded instruments: +{added} (total {total_inst})")

        print(f"→ ingesting memory quotes (DRAMeXchange) …")
        q = await ingest_memory_quotes(db, trigger="manual")
        print(f"   quotes: {q}")

        for m in markets:
            print(f"→ ingesting {m} equity prices (yfinance) …")
            r = await _ingest_market(db, m, limit)
            print(f"   {r}")

        print("→ computing trend metrics …")
        tm = await compute_trend_metrics(db)
        print(f"   trend_metrics: {tm}")

        print("→ computing market score …")
        ms = await compute_market_score(db)
        print(f"   market_score: {ms}")

        # ---------------- verification summary ----------------
        print("\n" + "=" * 60)
        print("REAL-DATA VERIFICATION SUMMARY")
        print("=" * 60)
        n_prices = await db.scalar(select(func.count()).select_from(EquityPrice))
        n_quotes = await db.scalar(select(func.count()).select_from(MemoryQuote))
        n_tm = await db.scalar(select(func.count()).select_from(TrendMetric))
        n_ms = await db.scalar(select(func.count()).select_from(MarketScore))
        print(f"equity_prices : {n_prices}")
        print(f"memory_quotes : {n_quotes}")
        print(f"trend_metrics : {n_tm}")
        print(f"market_scores : {n_ms}")

        print("\nSample memory quotes (real):")
        for row in (await db.scalars(
            select(MemoryQuote).order_by(MemoryQuote.category, MemoryQuote.product).limit(12)
        )).all():
            print(f"  {row.category:4} {row.price_type:6} {row.product[:32]:32} avg={row.price_avg} chg={row.change_pct}%")

        print("\nSample equity latest closes (real):")
        rows = (await db.execute(
            select(Instrument.ticker, Instrument.market, func.max(EquityPrice.trade_date), func.count(EquityPrice.id))
            .join(EquityPrice, EquityPrice.instrument_id == Instrument.id)
            .group_by(Instrument.id).order_by(Instrument.market).limit(12)
        )).all()
        for tk, mk, last, cnt in rows:
            print(f"  {mk} {tk:12} last_date={last} rows={cnt}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--markets", default="US,TW,JP,KR")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    asyncio.run(main([m.strip() for m in args.markets.split(",") if m.strip()], args.limit))

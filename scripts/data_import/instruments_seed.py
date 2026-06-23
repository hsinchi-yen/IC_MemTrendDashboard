#!/usr/bin/env python3
"""
scripts/data_import/instruments_seed.py
ACTION-011: Seed all instrument master data into PostgreSQL.

Usage:
    python scripts/data_import/instruments_seed.py
    python scripts/data_import/instruments_seed.py --dry-run
    python scripts/data_import/instruments_seed.py --json-path /custom/path/instruments_seed.json

Environment variables required:
    DATABASE_URL  — asyncpg-compatible PostgreSQL DSN
                    e.g. postgresql+asyncpg://user:pass@localhost:5432/ic_mem
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

import asyncpg
from dotenv import load_dotenv

# ── load .env from project root (two levels up from this script) ────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=False)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("instruments_seed")

# Default JSON path — sibling of this script
_DEFAULT_JSON = _SCRIPT_DIR / "instruments_seed.json"

# ── asyncpg DSN conversion ────────────────────────────────────────────────────
def _asyncpg_dsn(url: str) -> str:
    """Convert a SQLAlchemy-style URL to a bare asyncpg DSN.

    SQLAlchemy uses ``postgresql+asyncpg://…``; asyncpg.connect() wants
    ``postgresql://…``.
    """
    return url.replace("postgresql+asyncpg://", "postgresql://", 1)


# ── upsert logic ─────────────────────────────────────────────────────────────

_UPSERT_SQL = """
INSERT INTO instruments
    (ticker, market, name, name_en, tier, supply_chain_tag,
     currency, is_active, score_weight, score_only_observe)
VALUES
    ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
ON CONFLICT (ticker, market) DO UPDATE SET
    name              = EXCLUDED.name,
    name_en           = EXCLUDED.name_en,
    tier              = EXCLUDED.tier,
    supply_chain_tag  = EXCLUDED.supply_chain_tag,
    currency          = EXCLUDED.currency,
    is_active         = EXCLUDED.is_active,
    score_weight      = EXCLUDED.score_weight,
    score_only_observe= EXCLUDED.score_only_observe
"""


async def _seed(conn: asyncpg.Connection, instruments: list[dict], dry_run: bool) -> int:
    """Upsert all instruments into the database.

    Parameters
    ----------
    conn:
        Active asyncpg connection.
    instruments:
        Parsed list of instrument dicts.
    dry_run:
        If True, validate data but do not write to DB.

    Returns
    -------
    int
        Number of rows processed (upserted or validated).
    """
    ok = 0
    errors: list[str] = []

    for inst in instruments:
        ticker = inst.get("ticker", "")
        market = inst.get("market", "")

        # Basic validation
        if not ticker or not market:
            errors.append(f"Missing ticker/market in record: {inst}")
            continue

        score_weight = float(inst.get("score_weight", 0.0))
        is_active = bool(inst.get("is_active", True))
        score_only_observe = bool(inst.get("score_only_observe", False))

        if dry_run:
            logger.debug("[DRY-RUN] Would upsert %s.%s", market, ticker)
            ok += 1
            continue

        try:
            await conn.execute(
                _UPSERT_SQL,
                ticker,
                market,
                inst.get("name"),
                inst.get("name_en"),
                inst.get("tier"),
                inst.get("supply_chain_tag"),
                inst.get("currency"),
                is_active,
                score_weight,
                score_only_observe,
            )
            logger.debug("Upserted %s.%s", market, ticker)
            ok += 1
        except Exception as exc:  # noqa: BLE001
            msg = f"Failed to upsert {market}.{ticker}: {exc}"
            logger.error(msg)
            errors.append(msg)

    if errors:
        logger.warning("%d error(s) occurred during seed:", len(errors))
        for err in errors:
            logger.warning("  • %s", err)

    return ok


# ── entry point ───────────────────────────────────────────────────────────────

async def main(json_path: Path, dry_run: bool) -> None:
    """Load instruments JSON and upsert into PostgreSQL."""

    # --- read seed JSON -------------------------------------------------------
    if not json_path.exists():
        logger.error("Seed file not found: %s", json_path)
        sys.exit(1)

    logger.info("Loading seed data from: %s", json_path)
    raw = json_path.read_text(encoding="utf-8")
    instruments: list[dict] = json.loads(raw)
    logger.info("Loaded %d instrument entries.", len(instruments))

    if dry_run:
        logger.info("[DRY-RUN] mode active — no database writes will occur.")

    # --- connect to DB --------------------------------------------------------
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        logger.error("DATABASE_URL environment variable is not set.")
        sys.exit(1)

    dsn = _asyncpg_dsn(database_url)

    try:
        conn: asyncpg.Connection = await asyncpg.connect(dsn)
    except Exception as exc:
        logger.error("Cannot connect to database: %s", exc)
        sys.exit(1)

    try:
        # --- ensure table exists (fail gracefully if schema not yet applied) --
        try:
            await conn.fetchval("SELECT 1 FROM instruments LIMIT 1")
        except asyncpg.UndefinedTableError:
            logger.error(
                "Table 'instruments' does not exist. "
                "Run the DB migration / init_db first."
            )
            sys.exit(1)

        # --- execute upsert ---------------------------------------------------
        logger.info("Starting upsert …")
        processed = await _seed(conn, instruments, dry_run)

        if dry_run:
            logger.info("[DRY-RUN] Validated %d records. No DB changes made.", processed)
        else:
            logger.info("✅  Seeded %d instrument records successfully.", processed)

    finally:
        await conn.close()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed instrument master data into PostgreSQL."
    )
    parser.add_argument(
        "--json-path",
        type=Path,
        default=_DEFAULT_JSON,
        help=f"Path to instruments_seed.json (default: {_DEFAULT_JSON})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Validate data without writing to the database.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(main(json_path=args.json_path, dry_run=args.dry_run))

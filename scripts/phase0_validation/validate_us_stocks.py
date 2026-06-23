#!/usr/bin/env python3
"""
ACTION-002: Validate US memory/semiconductor stocks via multiple sources.
Output: scripts/phase0_validation/results/us_stocks_result.json

Sources tested (independently — one failure does NOT abort others):
  1. FinMind  – dataset USStockPrice
  2. Stooq   – CSV download (no key required)
  3. Alpha Vantage – TIME_SERIES_DAILY_ADJUSTED (free tier: 25 req/day)

Run:
    python validate_us_stocks.py
Requires (in .env):
    FINMIND_TOKEN   – FinMind API token
    ALPHAVANTAGE_KEY – Alpha Vantage API key  (free at alphavantage.co)
"""

import os
import io
import json
import time
import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import requests

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ticker universe
# ---------------------------------------------------------------------------
US_TICKERS: list[str] = [
    # Pure-play memory
    "MU",    # Micron Technology
    "SNDK",  # SanDisk (reborn 2024)
    "WDC",   # Western Digital
    "SIMO",  # Silicon Motion
    "RMBS",  # Rambus
    # Controller / IP adjacent
    "MRVL",  # Marvell Technology
    "AVGO",  # Broadcom
    "CDNS",  # Cadence Design
    "SNPS",  # Synopsys
    # Equipment
    "AMAT",  # Applied Materials
    "LRCX",  # Lam Research
    "KLAC",  # KLA Corporation
    # Test & inspection
    "TER",   # Teradyne
    "FORM",  # FormFactor
    "COHU",  # Cohu
    # Backend / packaging
    "AMKR",  # Amkor Technology
    # Materials / chemicals
    "ENTG",  # Entegris
    "MKSI",  # MKS Instruments
    # Metrology / advanced process
    "ONTO",  # Onto Innovation
    "ACLS",  # Axcelis Technologies
    "VECO",  # Veeco Instruments
    "PLAB",  # Photronics
    # Storage
    "STX",   # Seagate Technology
    "PSTG",  # Pure Storage
]

# ---------------------------------------------------------------------------
# API constants
# ---------------------------------------------------------------------------
FINMIND_API = "https://api.finmindtrade.com/api/v4/data"
ALPHAVANTAGE_API = "https://www.alphavantage.co/query"
STOOQ_BASE = "https://stooq.com/q/d/l/"

RESULTS_DIR = Path(__file__).parent / "results"

# Alpha Vantage free tier: 25 requests/day, ~5/min => use 12s interval
AV_INTERVAL_SECS = 12.0
# FinMind / Stooq: polite delay
DEFAULT_INTERVAL_SECS = 0.5


# ---------------------------------------------------------------------------
# Source 1: FinMind USStockPrice
# ---------------------------------------------------------------------------


def _finmind_us_stock(
    ticker: str,
    token: str,
    start_date: str,
    end_date: str,
    max_retries: int = 3,
) -> dict[str, Any]:
    """Query FinMind USStockPrice for a single ticker.

    Returns:
        dict with status, row_count, last_date, error (if any).
    """
    params = {
        "dataset": "USStockPrice",
        "data_id": ticker,
        "start_date": start_date,
        "end_date": end_date,
        "token": token,
    }
    for attempt in range(max_retries):
        try:
            resp = requests.get(FINMIND_API, params=params, timeout=30)
            if resp.status_code == 402:
                return {"status": "quota_exceeded", "error": "HTTP 402"}
            if resp.status_code == 401:
                return {"status": "auth_fail", "error": "HTTP 401"}
            resp.raise_for_status()

            records: list[dict] = resp.json().get("data", [])
            if not records:
                return {"status": "no_data", "row_count": 0, "last_date": None}
            return {
                "status": "success",
                "row_count": len(records),
                "last_date": records[-1].get("date"),
                "first_date": records[0].get("date"),
            }
        except requests.exceptions.Timeout:
            logger.warning("FinMind timeout %s (attempt %d)", ticker, attempt + 1)
        except requests.exceptions.RequestException as exc:
            logger.warning("FinMind error %s: %s", ticker, exc)

        if attempt < max_retries - 1:
            time.sleep(2**attempt)

    return {"status": "fail", "error": "max retries exceeded"}


# ---------------------------------------------------------------------------
# Source 2: Stooq CSV
# ---------------------------------------------------------------------------


def _stooq_us_stock(
    ticker: str,
    start_date: str,
    end_date: str,
    max_retries: int = 3,
) -> dict[str, Any]:
    """Download historical CSV from Stooq for a US ticker.

    Stooq symbol for US stocks is simply the uppercase ticker.
    URL pattern: https://stooq.com/q/d/l/?s=MU.US&d1=20240101&d2=20250101&i=d

    Returns:
        dict with status, row_count, last_date, error (if any).
    """
    stooq_sym = f"{ticker.lower()}.us"
    d1 = start_date.replace("-", "")
    d2 = end_date.replace("-", "")
    url = f"{STOOQ_BASE}?s={stooq_sym}&d1={d1}&d2={d2}&i=d"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    }

    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()

            text = resp.text.strip()
            lines = [ln for ln in text.splitlines() if ln.strip()]

            # Stooq returns "No data" or similar when symbol not found
            if len(lines) <= 1 or "No data" in text or "Przekroczono" in text:
                return {"status": "no_data", "row_count": 0, "last_date": None}

            # Header line + data lines
            data_lines = lines[1:]  # skip header
            last_row = data_lines[-1].split(",")
            last_date = last_row[0] if last_row else None
            return {
                "status": "success",
                "row_count": len(data_lines),
                "last_date": last_date,
                "first_date": data_lines[0].split(",")[0] if data_lines else None,
            }

        except requests.exceptions.Timeout:
            logger.warning("Stooq timeout %s (attempt %d)", ticker, attempt + 1)
        except requests.exceptions.RequestException as exc:
            logger.warning("Stooq error %s: %s", ticker, exc)

        if attempt < max_retries - 1:
            time.sleep(2**attempt)

    return {"status": "fail", "error": "max retries exceeded"}


# ---------------------------------------------------------------------------
# Source 3: Alpha Vantage
# ---------------------------------------------------------------------------


def _alphavantage_stock(
    ticker: str,
    api_key: str,
    max_retries: int = 3,
) -> dict[str, Any]:
    """Query Alpha Vantage TIME_SERIES_DAILY_ADJUSTED for a ticker.

    Returns:
        dict with status, row_count, last_date, error (if any).
    """
    if not api_key:
        return {"status": "skipped", "error": "ALPHAVANTAGE_KEY not set"}

    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker,
        "outputsize": "compact",  # 100 trading days
        "apikey": api_key,
    }

    for attempt in range(max_retries):
        try:
            resp = requests.get(ALPHAVANTAGE_API, params=params, timeout=30)
            resp.raise_for_status()

            data = resp.json()

            # Rate limit / note response
            if "Note" in data or "Information" in data:
                note = data.get("Note") or data.get("Information", "")
                logger.warning("Alpha Vantage note for %s: %s", ticker, note[:80])
                return {"status": "rate_limited", "error": note[:120]}

            ts_key = "Time Series (Daily)"
            if ts_key not in data:
                return {"status": "no_data", "row_count": 0, "last_date": None}

            ts: dict = data[ts_key]
            dates = sorted(ts.keys(), reverse=True)
            return {
                "status": "success",
                "row_count": len(dates),
                "last_date": dates[0] if dates else None,
                "first_date": dates[-1] if dates else None,
            }

        except requests.exceptions.Timeout:
            logger.warning("AV timeout %s (attempt %d)", ticker, attempt + 1)
        except requests.exceptions.RequestException as exc:
            logger.warning("AV error %s: %s", ticker, exc)

        if attempt < max_retries - 1:
            time.sleep(2**attempt)

    return {"status": "fail", "error": "max retries exceeded"}


# ---------------------------------------------------------------------------
# Validation runner
# ---------------------------------------------------------------------------


def validate_ticker(
    ticker: str,
    finmind_token: str,
    av_key: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """Run all three source checks for a single US ticker.

    Each source is checked independently; failure in one does not abort others.

    Returns:
        Dict with ticker, finmind, stooq, alphavantage sub-dicts.
    """
    logger.info("--- %s ---", ticker)

    logger.info("  [FinMind] querying...")
    fm_result = _finmind_us_stock(ticker, finmind_token, start_date, end_date)
    _log_result("FinMind", ticker, fm_result)
    time.sleep(DEFAULT_INTERVAL_SECS)

    logger.info("  [Stooq] querying...")
    stooq_result = _stooq_us_stock(ticker, start_date, end_date)
    _log_result("Stooq", ticker, stooq_result)
    time.sleep(DEFAULT_INTERVAL_SECS)

    logger.info("  [AlphaVantage] querying...")
    av_result = _alphavantage_stock(ticker, av_key)
    _log_result("AlphaVantage", ticker, av_result)
    # AV free tier: wait 12s before next AV call
    time.sleep(AV_INTERVAL_SECS)

    # Determine best available source
    best_source = _pick_best_source(
        finmind=fm_result,
        stooq=stooq_result,
        alphavantage=av_result,
    )

    return {
        "ticker": ticker,
        "best_source": best_source,
        "finmind": fm_result,
        "stooq": stooq_result,
        "alphavantage": av_result,
    }


def _log_result(source: str, ticker: str, result: dict[str, Any]) -> None:
    status = result.get("status", "?")
    if status == "success":
        logger.info(
            "    %s OK: %s rows, last=%s",
            source,
            result.get("row_count"),
            result.get("last_date"),
        )
    else:
        logger.warning("    %s %s: %s", source, status.upper(), result.get("error", ""))


def _pick_best_source(
    finmind: dict[str, Any],
    stooq: dict[str, Any],
    alphavantage: dict[str, Any],
) -> str:
    """Return name of first source with status=='success', else 'none'."""
    if stooq.get("status") == "success":
        return "stooq"
    if finmind.get("status") == "success":
        return "finmind"
    if alphavantage.get("status") == "success":
        return "alphavantage"
    return "none"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Validate all US tickers across three data sources and write JSON report."""
    finmind_token = os.getenv("FINMIND_TOKEN", "").strip()
    av_key = os.getenv("ALPHAVANTAGE_KEY", "").strip()

    if not finmind_token:
        logger.warning("FINMIND_TOKEN not set – FinMind checks will fail.")
    if not av_key:
        logger.warning("ALPHAVANTAGE_KEY not set – AV checks will be skipped.")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=365)).isoformat()

    logger.info(
        "Starting US stocks validation | %d tickers | %s -> %s",
        len(US_TICKERS),
        start_date,
        end_date,
    )

    results: list[dict[str, Any]] = []
    source_success: dict[str, int] = {"finmind": 0, "stooq": 0, "alphavantage": 0}

    for ticker in US_TICKERS:
        row = validate_ticker(ticker, finmind_token, av_key, start_date, end_date)
        results.append(row)

        for src in ("finmind", "stooq", "alphavantage"):
            if row.get(src, {}).get("status") == "success":
                source_success[src] += 1

    # Build summary per source
    summary = {
        "total_tickers": len(results),
        "period": {"start_date": start_date, "end_date": end_date},
        "source_coverage": {
            src: {
                "success": cnt,
                "total": len(results),
                "pct": round(cnt / len(results) * 100, 1) if results else 0,
            }
            for src, cnt in source_success.items()
        },
        "tickers_with_no_source": [
            r["ticker"] for r in results if r["best_source"] == "none"
        ],
    }

    report: dict[str, Any] = {
        "generated_at": date.today().isoformat(),
        "market": "US",
        "sources": ["FinMind", "Stooq", "AlphaVantage"],
        "summary": summary,
        "results": results,
    }

    out_path = RESULTS_DIR / "us_stocks_result.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Report saved to %s", out_path)
    logger.info("Coverage: FinMind=%d  Stooq=%d  AV=%d  (of %d tickers)",
                source_success["finmind"], source_success["stooq"],
                source_success["alphavantage"], len(results))


if __name__ == "__main__":
    main()

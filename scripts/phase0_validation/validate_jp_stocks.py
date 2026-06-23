#!/usr/bin/env python3
"""
ACTION-002: Validate Japan semiconductor stocks via Stooq and yfinance.
Output: scripts/phase0_validation/results/jp_stocks_result.json

Sources tested (independently):
  1. Stooq  – CSV download using <code>.jp symbol format
  2. yfinance – using <code>.T suffix (Tokyo Stock Exchange)

Special note: Kioxia (285A) trades on TSE; yfinance symbol is 285A.T

Run:
    python validate_jp_stocks.py
No API keys required.
"""

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
# Note: bare code -> Stooq uses <code>.jp, yfinance uses <code>.T
# Kioxia: code=285A (special: listed 2024-12-18 on TSE, yfinance: 285A.T)
# ---------------------------------------------------------------------------
JP_TICKERS: list[str] = [
    "285A",   # Kioxia Holdings (NAND flash; IPO Dec 2024 on TSE)
    "6857",   # Advantest
    "8035",   # Tokyo Electron (TEL)
    "7735",   # Dainippon Screen / SCREEN Holdings
    "6146",   # Disco Corporation
    "6920",   # Lasertec
    "6361",   # Ebara Corporation
    "7731",   # Nikon Corporation
    "7751",   # Canon Inc.
    "6728",   # Ulvac
    "6590",   # Shibaura Mechatronics
    "3436",   # Sumco Corporation
    "4063",   # Shin-Etsu Chemical
    "4004",   # Resonac Holdings (formerly Showa Denko)
    "4186",   # Tokyo Ohka Kogyo (TOK)
    "4901",   # Fujifilm Holdings
    "7741",   # Hoya Corporation
    "4062",   # Ibiden
    "7911",   # Toppan Holdings
    "7912",   # Dai Nippon Printing (DNP)
    "4401",   # ADEKA Corporation
    "4088",   # Air Water
]

STOOQ_BASE = "https://stooq.com/q/d/l/"
RESULTS_DIR = Path(__file__).parent / "results"

STOOQ_INTERVAL = 0.5   # seconds between Stooq requests
YFINANCE_INTERVAL = 0.5  # seconds between yfinance requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}


# ---------------------------------------------------------------------------
# Source 1: Stooq CSV
# ---------------------------------------------------------------------------


def _stooq_jp_stock(
    code: str,
    start_date: str,
    end_date: str,
    max_retries: int = 3,
) -> dict[str, Any]:
    """Download historical price CSV from Stooq for a Japan-listed stock.

    Stooq symbol format: <code>.jp (e.g. 6857.jp for Advantest)

    Args:
        code:       Numeric TSE code string, e.g. '6857'.
        start_date: ISO date string.
        end_date:   ISO date string.
        max_retries: Max HTTP retry attempts.

    Returns:
        Dict with status, row_count, last_date, error.
    """
    sym = f"{code.lower()}.jp"
    d1 = start_date.replace("-", "")
    d2 = end_date.replace("-", "")
    url = f"{STOOQ_BASE}?s={sym}&d1={d1}&d2={d2}&i=d"

    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()

            text = resp.text.strip()
            lines = [ln for ln in text.splitlines() if ln.strip()]

            if len(lines) <= 1 or "No data" in text or "Przekroczono" in text:
                return {"status": "no_data", "row_count": 0, "last_date": None}

            data_lines = lines[1:]
            last_date = data_lines[-1].split(",")[0] if data_lines else None
            first_date = data_lines[0].split(",")[0] if data_lines else None
            return {
                "status": "success",
                "row_count": len(data_lines),
                "last_date": last_date,
                "first_date": first_date,
                "stooq_symbol": sym,
            }

        except requests.exceptions.Timeout:
            logger.warning("Stooq timeout %s.jp (attempt %d)", code, attempt + 1)
        except requests.exceptions.RequestException as exc:
            logger.warning("Stooq error %s.jp: %s", code, exc)

        if attempt < max_retries - 1:
            time.sleep(2**attempt)

    return {"status": "fail", "error": "max retries exceeded", "stooq_symbol": sym}


# ---------------------------------------------------------------------------
# Source 2: yfinance
# ---------------------------------------------------------------------------


def _yfinance_jp_stock(
    code: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """Fetch price history via yfinance for a TSE-listed stock.

    yfinance symbol format: <code>.T (e.g. '6857.T')
    Kioxia special case: '285A.T'

    Args:
        code:       TSE numeric code, e.g. '6857'.
        start_date: ISO date string.
        end_date:   ISO date string.

    Returns:
        Dict with status, row_count, last_date, error.
    """
    try:
        import yfinance as yf  # noqa: PLC0415 — lazy import
    except ImportError:
        return {"status": "skipped", "error": "yfinance not installed"}

    yf_sym = f"{code}.T"
    try:
        ticker_obj = yf.Ticker(yf_sym)
        hist = ticker_obj.history(start=start_date, end=end_date, auto_adjust=True)

        if hist is None or hist.empty:
            return {"status": "no_data", "row_count": 0, "last_date": None, "yf_symbol": yf_sym}

        dates = hist.index.strftime("%Y-%m-%d").tolist()
        return {
            "status": "success",
            "row_count": len(dates),
            "last_date": dates[-1] if dates else None,
            "first_date": dates[0] if dates else None,
            "yf_symbol": yf_sym,
        }

    except Exception as exc:  # yfinance raises broad exceptions
        logger.warning("yfinance error %s: %s", yf_sym, exc)
        return {"status": "fail", "error": str(exc), "yf_symbol": yf_sym}


# ---------------------------------------------------------------------------
# Validation runner
# ---------------------------------------------------------------------------


def validate_ticker(
    code: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """Run both source checks for a single Japan ticker.

    Each source is checked independently.

    Returns:
        Dict with code, stooq, yfinance sub-dicts and best_source.
    """
    logger.info("--- %s ---", code)

    logger.info("  [Stooq] querying %s.jp...", code)
    stooq_result = _stooq_jp_stock(code, start_date, end_date)
    _log_result("Stooq", code, stooq_result)
    time.sleep(STOOQ_INTERVAL)

    logger.info("  [yfinance] querying %s.T...", code)
    yf_result = _yfinance_jp_stock(code, start_date, end_date)
    _log_result("yfinance", code, yf_result)
    time.sleep(YFINANCE_INTERVAL)

    best_source = _pick_best_source(stooq=stooq_result, yfinance=yf_result)

    return {
        "code": code,
        "yf_symbol": f"{code}.T",
        "stooq_symbol": f"{code.lower()}.jp",
        "best_source": best_source,
        "stooq": stooq_result,
        "yfinance": yf_result,
    }


def _log_result(source: str, code: str, result: dict[str, Any]) -> None:
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


def _pick_best_source(stooq: dict[str, Any], yfinance: dict[str, Any]) -> str:
    if stooq.get("status") == "success":
        return "stooq"
    if yfinance.get("status") == "success":
        return "yfinance"
    return "none"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Validate all Japan tickers and write JSON report."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=365)).isoformat()

    logger.info(
        "Starting Japan stocks validation | %d tickers | %s -> %s",
        len(JP_TICKERS),
        start_date,
        end_date,
    )

    results: list[dict[str, Any]] = []
    source_success: dict[str, int] = {"stooq": 0, "yfinance": 0}

    for code in JP_TICKERS:
        row = validate_ticker(code, start_date, end_date)
        results.append(row)

        for src in ("stooq", "yfinance"):
            if row.get(src, {}).get("status") == "success":
                source_success[src] += 1

    tickers_no_source = [r["code"] for r in results if r["best_source"] == "none"]

    # Extra note for Kioxia (285A) – IPO Dec 2024, coverage may be limited
    kioxia_note = (
        "Kioxia (285A) IPO'd on TSE on 2024-12-18. "
        "Coverage before that date will be empty. "
        "yfinance symbol: 285A.T  |  Stooq symbol: 285a.jp"
    )

    report: dict[str, Any] = {
        "generated_at": date.today().isoformat(),
        "market": "JP",
        "sources": ["Stooq", "yfinance"],
        "notes": {
            "kioxia": kioxia_note,
            "stooq_symbol_format": "<code>.jp (lowercase)",
            "yfinance_symbol_format": "<code>.T",
        },
        "summary": {
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
            "tickers_with_no_source": tickers_no_source,
        },
        "results": results,
    }

    out_path = RESULTS_DIR / "jp_stocks_result.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Report saved to %s", out_path)
    logger.info(
        "Coverage: Stooq=%d  yfinance=%d  (of %d tickers)",
        source_success["stooq"],
        source_success["yfinance"],
        len(results),
    )


if __name__ == "__main__":
    main()

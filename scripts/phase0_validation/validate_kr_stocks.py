#!/usr/bin/env python3
"""
ACTION-002: Validate Korea semiconductor stocks via yfinance and Stooq.
Output: scripts/phase0_validation/results/kr_stocks_result.json

Sources tested (independently):
  1. yfinance – .KS (KOSPI) / .KQ (KOSDAQ) suffix
  2. Stooq   – .kr suffix (not all KR stocks are on Stooq; failure is expected)

Run:
    python validate_kr_stocks.py
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
# Ticker universe (yfinance format)
# .KS = KOSPI, .KQ = KOSDAQ
# ---------------------------------------------------------------------------
KR_TICKERS: list[str] = [
    "005930.KS",   # Samsung Electronics (DRAM/NAND/HBM)
    "000660.KS",   # SK Hynix (DRAM/HBM)
    "240810.KQ",   # Wonik IPS (ALD/CVD equipment)
    "319660.KQ",   # Techwing (memory test handler)
    "031980.KQ",   # Piontech (socket)
    "084370.KQ",   # ISC (test socket/rubber)
    "095610.KQ",   # Tester / test solution
    "222800.KQ",   # Simple Plus (semiconductor packaging material)
    "095340.KQ",   # ISC (integrated semiconductor)
    "058470.KQ",   # Rifa Semicon
    "067310.KQ",   # HB Solution (test handler)
    "036540.KQ",   # SFA Semicon (wire bonding)
    "033640.KQ",   # Hana Materials (etch gas)
    "131290.KQ",   # Kovio / Isplice (memory module)
    "092870.KQ",   # Ecopro HN (high-purity materials)
    "357780.KQ",   # Solbrain Holdings (CMP slurry / etchant)
    "005290.KQ",   # Partron
    "014680.KS",   # Hansol Chemical (H2O2 for semiconductor)
    "104830.KQ",   # Wonik QnC (quartz products)
    "092070.KQ",   # Aprogen Pharma / Iljin Materials (copper foil)
    "093370.KS",   # Korea Circuit (PCB substrate)
]

STOOQ_BASE = "https://stooq.com/q/d/l/"
RESULTS_DIR = Path(__file__).parent / "results"

STOOQ_INTERVAL = 0.5
YFINANCE_INTERVAL = 0.5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}


# ---------------------------------------------------------------------------
# Helpers: parse code / exchange from yfinance symbol
# ---------------------------------------------------------------------------


def _parse_ticker(yf_sym: str) -> tuple[str, str]:
    """Split '005930.KS' -> ('005930', 'KS')."""
    parts = yf_sym.rsplit(".", 1)
    code = parts[0]
    exchange = parts[1] if len(parts) > 1 else ""
    return code, exchange


def _stooq_symbol(yf_sym: str) -> str:
    """Convert yfinance KR symbol to Stooq format.

    Examples:
        '005930.KS' -> '005930.kr'
        '240810.KQ' -> '240810.kr'
    """
    code, _ = _parse_ticker(yf_sym)
    return f"{code}.kr"


# ---------------------------------------------------------------------------
# Source 1: yfinance
# ---------------------------------------------------------------------------


def _yfinance_kr_stock(
    yf_sym: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """Fetch price history via yfinance for a KR-listed stock.

    Args:
        yf_sym:     yfinance symbol, e.g. '005930.KS'.
        start_date: ISO date string.
        end_date:   ISO date string.

    Returns:
        Dict with status, row_count, last_date, error.
    """
    try:
        import yfinance as yf  # noqa: PLC0415
    except ImportError:
        return {"status": "skipped", "error": "yfinance not installed"}

    try:
        ticker_obj = yf.Ticker(yf_sym)
        hist = ticker_obj.history(start=start_date, end=end_date, auto_adjust=True)

        if hist is None or hist.empty:
            return {"status": "no_data", "row_count": 0, "last_date": None}

        dates = hist.index.strftime("%Y-%m-%d").tolist()
        return {
            "status": "success",
            "row_count": len(dates),
            "last_date": dates[-1] if dates else None,
            "first_date": dates[0] if dates else None,
            "sample_close": float(hist["Close"].iloc[-1]) if not hist.empty else None,
        }

    except Exception as exc:
        logger.warning("yfinance error %s: %s", yf_sym, exc)
        return {"status": "fail", "error": str(exc)}


# ---------------------------------------------------------------------------
# Source 2: Stooq CSV
# ---------------------------------------------------------------------------


def _stooq_kr_stock(
    yf_sym: str,
    start_date: str,
    end_date: str,
    max_retries: int = 3,
) -> dict[str, Any]:
    """Download historical CSV from Stooq for a KR-listed stock.

    Stooq coverage for KR stocks is partial (mainly KOSPI blue chips).
    KOSDAQ tickers may return no_data – this is expected and noted.

    Args:
        yf_sym:      yfinance symbol, used to derive Stooq symbol.
        start_date:  ISO date string.
        end_date:    ISO date string.
        max_retries: Max HTTP retry attempts.

    Returns:
        Dict with status, row_count, last_date, stooq_symbol, error.
    """
    stooq_sym = _stooq_symbol(yf_sym)
    d1 = start_date.replace("-", "")
    d2 = end_date.replace("-", "")
    url = f"{STOOQ_BASE}?s={stooq_sym}&d1={d1}&d2={d2}&i=d"

    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()

            text = resp.text.strip()
            lines = [ln for ln in text.splitlines() if ln.strip()]

            if len(lines) <= 1 or "No data" in text or "Przekroczono" in text:
                return {
                    "status": "no_data",
                    "row_count": 0,
                    "last_date": None,
                    "stooq_symbol": stooq_sym,
                    "note": "Stooq KR coverage is partial; KOSDAQ stocks often absent",
                }

            data_lines = lines[1:]
            last_date = data_lines[-1].split(",")[0] if data_lines else None
            first_date = data_lines[0].split(",")[0] if data_lines else None
            return {
                "status": "success",
                "row_count": len(data_lines),
                "last_date": last_date,
                "first_date": first_date,
                "stooq_symbol": stooq_sym,
            }

        except requests.exceptions.Timeout:
            logger.warning("Stooq timeout %s (attempt %d)", stooq_sym, attempt + 1)
        except requests.exceptions.RequestException as exc:
            logger.warning("Stooq error %s: %s", stooq_sym, exc)

        if attempt < max_retries - 1:
            time.sleep(2**attempt)

    return {"status": "fail", "error": "max retries exceeded", "stooq_symbol": stooq_sym}


# ---------------------------------------------------------------------------
# Validation runner
# ---------------------------------------------------------------------------


def validate_ticker(
    yf_sym: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """Run both source checks for a single Korea ticker.

    Each source is checked independently; failure in one does not abort others.

    Returns:
        Dict with ticker info, yfinance, stooq sub-dicts, best_source.
    """
    code, exchange = _parse_ticker(yf_sym)
    logger.info("--- %s (%s) ---", yf_sym, exchange)

    logger.info("  [yfinance] querying %s...", yf_sym)
    yf_result = _yfinance_kr_stock(yf_sym, start_date, end_date)
    _log_result("yfinance", yf_sym, yf_result)
    time.sleep(YFINANCE_INTERVAL)

    logger.info("  [Stooq] querying %s.kr...", code)
    stooq_result = _stooq_kr_stock(yf_sym, start_date, end_date)
    _log_result("Stooq", yf_sym, stooq_result)
    time.sleep(STOOQ_INTERVAL)

    best_source = _pick_best_source(yfinance=yf_result, stooq=stooq_result)

    return {
        "ticker": yf_sym,
        "code": code,
        "exchange": exchange,
        "stooq_symbol": f"{code}.kr",
        "best_source": best_source,
        "yfinance": yf_result,
        "stooq": stooq_result,
    }


def _log_result(source: str, sym: str, result: dict[str, Any]) -> None:
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


def _pick_best_source(yfinance: dict[str, Any], stooq: dict[str, Any]) -> str:
    """Prefer yfinance for KR because Stooq KR coverage is incomplete."""
    if yfinance.get("status") == "success":
        return "yfinance"
    if stooq.get("status") == "success":
        return "stooq"
    return "none"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Validate all Korea tickers and write JSON report."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=365)).isoformat()

    logger.info(
        "Starting Korea stocks validation | %d tickers | %s -> %s",
        len(KR_TICKERS),
        start_date,
        end_date,
    )

    results: list[dict[str, Any]] = []
    source_success: dict[str, int] = {"yfinance": 0, "stooq": 0}

    for yf_sym in KR_TICKERS:
        row = validate_ticker(yf_sym, start_date, end_date)
        results.append(row)

        for src in ("yfinance", "stooq"):
            if row.get(src, {}).get("status") == "success":
                source_success[src] += 1

    tickers_no_source = [r["ticker"] for r in results if r["best_source"] == "none"]

    report: dict[str, Any] = {
        "generated_at": date.today().isoformat(),
        "market": "KR",
        "sources": ["yfinance", "Stooq"],
        "notes": {
            "stooq_coverage": (
                "Stooq KR coverage is partial. KOSPI majors (Samsung, Hynix) "
                "are typically available. Most KOSDAQ tickers return no_data. "
                "yfinance is the recommended primary source for KR."
            ),
            "yf_suffixes": ".KS = KOSPI, .KQ = KOSDAQ",
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

    out_path = RESULTS_DIR / "kr_stocks_result.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Report saved to %s", out_path)
    logger.info(
        "Coverage: yfinance=%d  Stooq=%d  (of %d tickers)",
        source_success["yfinance"],
        source_success["stooq"],
        len(results),
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
ACTION-002: Validate Taiwan stocks via FinMind API
Output: scripts/phase0_validation/results/tw_finmind_result.json

Tests TaiwanStockPrice endpoint coverage for all Taiwan memory/IC tickers.
Run:
    python validate_tw_finmind.py
Requires:
    FINMIND_TOKEN in .env
"""

import os
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
TW_TICKERS: dict[str, str] = {
    # Core memory
    "2408": "南亞科",
    "2344": "華邦電",
    "6770": "力積電",
    "3006": "晶豪科",
    "2337": "旺宏",
    "8299": "群聯",
    "2451": "創見",
    "3260": "威剛",
    "4967": "十銓",
    "5289": "宜鼎",
    "8271": "宇瞻",
    "8088": "品安",
    # Control IC / IP
    "8054": "安國",
    "6104": "創惟",
    "3529": "力旺",
    "3661": "世芯-KY",
    # Backend test / substrate
    "6239": "力成",
    "8150": "南茂",
    "2449": "京元電子",
    "6257": "矽格",
    "8110": "華東",
    "3711": "日月光投控",
    "3264": "欣銓",
    "6515": "穎崴",
    "6510": "中華精測",
    "6223": "旺矽",
    "6683": "雍智科技",
    "3037": "欣興",
    "3189": "景碩",
    "8046": "南電",
    # Equipment / material
    "6488": "環球晶",
    "5483": "中美晶",
    "3532": "台勝科",
    "3680": "家登",
    "3131": "弘塑",
    "3583": "辛耘",
    "6196": "帆宣",
    "2404": "漢唐",
    "5434": "崇越",
}

FINMIND_API = "https://api.finmindtrade.com/api/v4/data"
RESULTS_DIR = Path(__file__).parent / "results"

# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------


def fetch_stock_price(
    ticker: str,
    token: str,
    start_date: str,
    end_date: str,
    max_retries: int = 3,
) -> dict[str, Any]:
    """Fetch daily stock prices from FinMind TaiwanStockPrice endpoint.

    Args:
        ticker:      4-digit Taiwan stock code.
        token:       FinMind API bearer token.
        start_date:  ISO date string, e.g. '2024-06-01'.
        end_date:    ISO date string, e.g. '2025-06-01'.
        max_retries: Number of retry attempts on network errors.

    Returns:
        Dict with keys: status, row_count, last_date, (error).
    """
    params = {
        "dataset": "TaiwanStockPrice",
        "data_id": ticker,
        "start_date": start_date,
        "end_date": end_date,
        "token": token,
    }

    for attempt in range(max_retries):
        try:
            resp = requests.get(FINMIND_API, params=params, timeout=30)

            if resp.status_code == 402:
                return {
                    "status": "quota_exceeded",
                    "error": f"HTTP 402 - API quota exceeded (ticker: {ticker})",
                }

            if resp.status_code == 401:
                return {
                    "status": "auth_fail",
                    "error": "HTTP 401 - invalid or missing token",
                }

            resp.raise_for_status()

            payload = resp.json()
            records: list[dict] = payload.get("data", [])

            if not records:
                return {"status": "no_data", "row_count": 0, "last_date": None}

            return {
                "status": "success",
                "row_count": len(records),
                "last_date": records[-1].get("date"),
                "first_date": records[0].get("date"),
                "sample_close": records[-1].get("close"),
            }

        except requests.exceptions.Timeout:
            logger.warning(
                "Timeout for %s (attempt %d/%d)", ticker, attempt + 1, max_retries
            )
        except requests.exceptions.HTTPError as exc:
            logger.warning("HTTP error for %s: %s", ticker, exc)
        except requests.exceptions.RequestException as exc:
            logger.warning("Request error for %s: %s", ticker, exc)

        if attempt < max_retries - 1:
            sleep_secs = 2 ** attempt  # 1s, 2s
            logger.info("Retrying %s in %ds...", ticker, sleep_secs)
            time.sleep(sleep_secs)

    return {"status": "fail", "error": "max retries exceeded"}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Run FinMind validation for all Taiwan tickers and write JSON report."""
    token = os.getenv("FINMIND_TOKEN", "").strip()
    if not token:
        logger.error("FINMIND_TOKEN not set. Add it to .env and retry.")
        return

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=365)).isoformat()

    logger.info(
        "Starting Taiwan FinMind validation | %d tickers | %s -> %s",
        len(TW_TICKERS),
        start_date,
        end_date,
    )

    results: list[dict[str, Any]] = []
    success_count = fail_count = no_data_count = 0
    quota_hit = False

    for ticker, name in TW_TICKERS.items():
        logger.info("Testing %s (%s)...", ticker, name)
        result = fetch_stock_price(ticker, token, start_date, end_date)

        status = result.get("status", "fail")
        if status == "quota_exceeded":
            logger.error("Quota exceeded - stopping early after %d results.", len(results))
            results.append({"ticker": ticker, "name": name, **result})
            quota_hit = True
            break

        if status == "auth_fail":
            logger.error("Authentication failed - check FINMIND_TOKEN.")
            results.append({"ticker": ticker, "name": name, **result})
            break

        results.append({"ticker": ticker, "name": name, **result})

        if status == "success":
            success_count += 1
            logger.info(
                "  OK %s rows, last date %s",
                result.get("row_count"),
                result.get("last_date"),
            )
        elif status == "no_data":
            no_data_count += 1
            logger.warning("  WARN No data returned for %s", ticker)
        else:
            fail_count += 1
            logger.warning("  FAIL %s: %s", ticker, result.get("error"))

        time.sleep(0.5)  # Respect FinMind rate limit

    report: dict[str, Any] = {
        "generated_at": date.today().isoformat(),
        "market": "TW",
        "source": "FinMind",
        "period": {"start_date": start_date, "end_date": end_date},
        "summary": {
            "total": len(results),
            "success": success_count,
            "no_data": no_data_count,
            "fail": fail_count,
            "quota_hit": quota_hit,
        },
        "results": results,
    }

    out_path = RESULTS_DIR / "tw_finmind_result.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Report saved to %s", out_path)
    logger.info(
        "Summary -> success=%d  no_data=%d  fail=%d  total=%d",
        success_count,
        no_data_count,
        fail_count,
        len(results),
    )


if __name__ == "__main__":
    main()

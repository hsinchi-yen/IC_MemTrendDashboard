#!/usr/bin/env python3
"""
ACTION-002: Validate DRAMeXchange public spot/contract price snapshots.
Output: scripts/phase0_validation/results/memory_quotes_result.json

Strategy:
  1. HTTP GET https://www.dramexchange.com/ with Chrome User-Agent
  2. Parse HTML tables with BeautifulSoup (lxml parser)
  3. Record table headers, row count, and sample data
  4. If parsing fails or JS rendering is required, note that Playwright is needed

Rate limit: 3s between requests (be a good citizen).

Run:
    python validate_memory_quotes.py
No API keys required.
"""

import json
import time
import logging
from datetime import date
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DRAMEX_BASE = "https://www.dramexchange.com/"

# Pages / endpoints to try — DRAMeXchange has category sub-paths
DRAMEX_URLS: list[dict[str, str]] = [
    {"label": "homepage",     "url": "https://www.dramexchange.com/"},
    {"label": "dram_spot",    "url": "https://www.dramexchange.com/WeeklyResearch/Post/2/type/1.html"},
    {"label": "nand_spot",    "url": "https://www.dramexchange.com/WeeklyResearch/Post/2/type/2.html"},
    {"label": "module_price", "url": "https://www.dramexchange.com/WeeklyResearch/Post/3/type/1.html"},
]

RESULTS_DIR = Path(__file__).parent / "results"

REQUEST_INTERVAL = 3.0  # seconds — polite crawl delay

CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": CHROME_UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


# ---------------------------------------------------------------------------
# HTML fetcher
# ---------------------------------------------------------------------------


def fetch_html(url: str, max_retries: int = 3) -> dict[str, Any]:
    """Fetch a URL and return status + HTML text.

    Args:
        url:         Target URL.
        max_retries: Max HTTP retry attempts.

    Returns:
        Dict with status, http_code, html (truncated), error.
    """
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
            return {
                "status": "ok",
                "http_code": resp.status_code,
                "content_type": resp.headers.get("Content-Type", ""),
                "content_length": len(resp.content),
                "html": resp.text,
            }
        except requests.exceptions.Timeout:
            logger.warning("Timeout for %s (attempt %d)", url, attempt + 1)
        except requests.exceptions.SSLError as exc:
            logger.warning("SSL error for %s: %s", url, exc)
            return {"status": "ssl_error", "http_code": None, "error": str(exc)}
        except requests.exceptions.RequestException as exc:
            logger.warning("Request error for %s: %s", url, exc)

        if attempt < max_retries - 1:
            time.sleep(2**attempt)

    return {"status": "fail", "http_code": None, "error": "max retries exceeded"}


# ---------------------------------------------------------------------------
# HTML parser
# ---------------------------------------------------------------------------


def parse_price_tables(html: str, url: str) -> dict[str, Any]:
    """Parse HTML for price tables using BeautifulSoup with lxml backend.

    Extracts:
      - All <table> elements with their headers and first 3 data rows.
      - Any <div> / <span> elements that look like price lists.
      - Flags if the page appears JS-rendered (very little text content).

    Args:
        html: Raw HTML string.
        url:  Source URL (used for logging).

    Returns:
        Dict with tables_found, tables, js_render_likely, notes.
    """
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception as exc:
        logger.warning("BeautifulSoup parse error for %s: %s", url, exc)
        return {"tables_found": 0, "error": str(exc)}

    # Heuristic: JS-heavy pages have little visible text
    text_len = len(soup.get_text(strip=True))
    js_render_likely = text_len < 500

    if js_render_likely:
        logger.warning(
            "Page text length=%d — page may require JS rendering (Playwright). URL: %s",
            text_len,
            url,
        )

    tables: list[dict[str, Any]] = []
    for i, table in enumerate(soup.find_all("table")):
        headers: list[str] = []
        rows: list[list[str]] = []

        # Extract headers from <th> or first <tr>
        th_tags = table.find_all("th")
        if th_tags:
            headers = [th.get_text(strip=True) for th in th_tags]
        else:
            first_tr = table.find("tr")
            if first_tr:
                headers = [td.get_text(strip=True) for td in first_tr.find_all(["td", "th"])]

        # Extract up to first 3 data rows
        all_trs = table.find_all("tr")
        data_trs = all_trs[1:4] if headers else all_trs[:3]
        for tr in data_trs:
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if any(cells):
                rows.append(cells)

        total_rows = max(0, len(all_trs) - 1)
        tables.append(
            {
                "table_index": i,
                "headers": headers,
                "sample_rows": rows,
                "total_rows": total_rows,
            }
        )

    # Look for price-like divs (fallback for non-table layouts)
    price_divs: list[str] = []
    for cls_hint in ["price", "quote", "market", "spot", "dram", "nand"]:
        found = soup.find_all(
            ["div", "span", "td"],
            class_=lambda c: c and cls_hint in c.lower() if c else False,
        )
        for elem in found[:3]:
            txt = elem.get_text(strip=True)
            if txt:
                price_divs.append(txt[:120])

    notes: list[str] = []
    if js_render_likely:
        notes.append(
            "PLAYWRIGHT_NEEDED: Page appears to be JS-rendered. "
            "Static HTML scraping will not capture live price data. "
            "Use Playwright (playwright.chromium.launch) to render and scrape."
        )
    if not tables and not price_divs:
        notes.append("No price tables or price-like elements found in static HTML.")

    return {
        "tables_found": len(tables),
        "text_length": text_len,
        "js_render_likely": js_render_likely,
        "tables": tables,
        "price_divs_sample": price_divs[:5],
        "notes": notes,
    }


# ---------------------------------------------------------------------------
# Page validator
# ---------------------------------------------------------------------------


def validate_url(entry: dict[str, str]) -> dict[str, Any]:
    """Fetch and parse one DRAMeXchange URL.

    Args:
        entry: Dict with 'label' and 'url'.

    Returns:
        Comprehensive result dict.
    """
    label = entry["label"]
    url = entry["url"]
    logger.info("Checking [%s] %s", label, url)

    fetch_result = fetch_html(url)
    if fetch_result["status"] != "ok":
        return {
            "label": label,
            "url": url,
            "fetch_status": fetch_result["status"],
            "http_code": fetch_result.get("http_code"),
            "error": fetch_result.get("error"),
            "parse": None,
        }

    html = fetch_result.get("html", "")
    parse_result = parse_price_tables(html, url)

    logger.info(
        "  HTTP %s | tables=%d | text_len=%d | js_render=%s",
        fetch_result.get("http_code"),
        parse_result.get("tables_found", 0),
        parse_result.get("text_length", 0),
        parse_result.get("js_render_likely"),
    )
    for note in parse_result.get("notes", []):
        logger.warning("  NOTE: %s", note)

    return {
        "label": label,
        "url": url,
        "fetch_status": "ok",
        "http_code": fetch_result.get("http_code"),
        "content_type": fetch_result.get("content_type"),
        "content_length": fetch_result.get("content_length"),
        "parse": parse_result,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Validate DRAMeXchange URLs and write JSON report."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Starting DRAMeXchange validation | %d URLs | rate limit: %ss",
        len(DRAMEX_URLS),
        REQUEST_INTERVAL,
    )

    results: list[dict[str, Any]] = []
    playwright_needed = False

    for i, entry in enumerate(DRAMEX_URLS):
        result = validate_url(entry)
        results.append(result)

        parse = result.get("parse") or {}
        if parse.get("js_render_likely"):
            playwright_needed = True

        # Rate limit — wait between requests
        if i < len(DRAMEX_URLS) - 1:
            logger.info("Waiting %.1fs before next request...", REQUEST_INTERVAL)
            time.sleep(REQUEST_INTERVAL)

    # Summarize
    urls_ok = sum(1 for r in results if r.get("fetch_status") == "ok")
    urls_with_tables = sum(
        1 for r in results if (r.get("parse") or {}).get("tables_found", 0) > 0
    )

    recommendation = (
        "PLAYWRIGHT_REQUIRED"
        if playwright_needed
        else "STATIC_SCRAPING_SUFFICIENT"
    )

    report: dict[str, Any] = {
        "generated_at": date.today().isoformat(),
        "source": "DRAMeXchange",
        "base_url": DRAMEX_BASE,
        "summary": {
            "total_urls": len(results),
            "urls_fetched_ok": urls_ok,
            "urls_with_price_tables": urls_with_tables,
            "playwright_needed": playwright_needed,
            "recommendation": recommendation,
            "recommendation_detail": (
                "DRAMeXchange renders price tables via JavaScript. "
                "Static HTML fetching captures page chrome but not live price data. "
                "Use Playwright (pip install playwright; playwright install chromium) "
                "to render full DOM before scraping tables."
                if playwright_needed
                else "Static scraping appears sufficient for this page."
            ),
        },
        "results": results,
    }

    out_path = RESULTS_DIR / "memory_quotes_result.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Report saved to %s", out_path)
    logger.info(
        "Summary: fetched=%d  with_tables=%d  playwright_needed=%s",
        urls_ok,
        urls_with_tables,
        playwright_needed,
    )
    if playwright_needed:
        logger.warning(
            "RECOMMENDATION: Install Playwright for full JS rendering: "
            "pip install playwright && playwright install chromium"
        )


if __name__ == "__main__":
    main()

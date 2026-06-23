"""
backend/app/services/memory_quote_parser.py

Scrape and parse public memory spot/contract price tables from DRAMeXchange.

The public landing page renders several price tables (DRAM Spot, Module Spot,
Flash Spot, GDDR Spot, Wafer Spot, Memory Card …). Each priced row has the
shape::

    [Item, Daily/Weekly High, Daily/Weekly Low, Session High,
     Session Low, Session Average, Change %, (history)]

e.g. ``['DDR3 4Gb 512Mx8 1600/1866', '16.50', '6.60', '16.50', '6.60',
        '11.271', '1.07 %', '']``

This module extracts those rows **including their real prices**, classifies
each product into a category (DRAM / NAND) and a price_type (spot / module /
wafer / flash / card), and returns normalised quote dicts ready to upsert.

Covers DDR2 / DDR3 / DDR4 / DDR5, GDDR, LPDDR, NAND wafer/flash, etc.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Any

import httpx
from bs4 import BeautifulSoup

DRAMEXCHANGE_URL = "https://www.dramexchange.com/"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)

_NUM_RE = re.compile(r"^-?\d{1,3}(?:,\d{3})*(?:\.\d+)?$")
_PCT_RE = re.compile(r"^-?\d+(?:\.\d+)?\s*%$")


def _to_float(token: str) -> float | None:
    token = (token or "").replace(",", "").strip()
    if not token or not _NUM_RE.match(token):
        return None
    try:
        return float(token)
    except ValueError:
        return None


def _parse_pct(token: str) -> float | None:
    token = (token or "").strip()
    if not _PCT_RE.match(token):
        return None
    try:
        return float(token.rstrip("%").strip())
    except ValueError:
        return None


def classify_product(product: str) -> tuple[str, str]:
    """Return ``(category, price_type)`` for a memory product label.

    category   : ``DRAM`` | ``NAND``
    price_type : ``spot`` | ``module`` | ``wafer`` | ``flash`` | ``card`` | ``ssd``
    """
    p = product.upper()

    if any(k in p for k in ("DDR", "GDDR", "LPDDR", "HBM")):
        category = "DRAM"
    else:
        category = "NAND"

    if any(k in p for k in ("UDIMM", "RDIMM", "SODIMM", "DIMM")):
        price_type = "module"
    elif "SSD" in p:
        price_type = "ssd"
    elif "MICROSD" in p or "SD CARD" in p or p.startswith("SD "):
        price_type = "card"
    elif ("TLC" in p or "QLC" in p) and category == "NAND":
        price_type = "wafer"
    elif any(k in p for k in ("SLC", "MLC")) and category == "NAND":
        price_type = "flash"
    else:
        price_type = "spot"

    return category, price_type


def _looks_like_price_row(cells: list[str]) -> bool:
    """A priced row = non-numeric item + >=4 numeric cells + a percent cell."""
    if len(cells) < 7:
        return False
    item = cells[0].strip()
    if not item or _to_float(item) is not None:
        return False
    if not any(_PCT_RE.match(c.strip()) for c in cells[1:8]):
        return False
    numeric = sum(1 for c in cells[1:7] if _to_float(c) is not None)
    return numeric >= 4


def _extract_quote(cells: list[str]) -> dict[str, Any] | None:
    """Map a priced row's cells into a normalised quote dict."""
    product = cells[0].strip()
    nums = [_to_float(c) for c in cells[1:7]]
    pct = next((_parse_pct(c) for c in cells[1:8] if _parse_pct(c) is not None), None)

    # nums layout: [high, low, sess_high, sess_low, avg, …]
    high = nums[0] if len(nums) > 0 else None
    low = nums[1] if len(nums) > 1 else None
    # Session Average is the 5th numeric column; fall back to mid of hi/lo.
    avg = nums[4] if len(nums) > 4 and nums[4] is not None else None
    if avg is None and high is not None and low is not None:
        avg = round((high + low) / 2, 4)

    if avg is None and high is None and low is None:
        return None

    category, price_type = classify_product(product)
    return {
        "product": product,
        "category": category,
        "price_type": price_type,
        "price_high": high,
        "price_low": low,
        "price_avg": avg,
        "change_pct": pct,
    }


def parse_quotes_from_html(html: str) -> list[dict[str, Any]]:
    """Parse all priced memory rows from a DRAMeXchange HTML page."""
    soup = BeautifulSoup(html, "lxml")
    seen: set[tuple[str, str]] = set()
    quotes: list[dict[str, Any]] = []

    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        if not _looks_like_price_row(cells):
            continue
        quote = _extract_quote(cells)
        if not quote:
            continue
        key = (quote["product"], quote["price_type"])
        if key in seen:
            continue
        seen.add(key)
        quotes.append(quote)

    return quotes


async def fetch_memory_quote_tables() -> dict[str, Any]:
    """Fetch DRAMeXchange and return parsed real memory quotes.

    Returns
    -------
    dict
        ``status``      : ``success`` | ``requires_manual_or_playwright``
        ``quotes``      : list of normalised quote dicts (with real prices)
        ``last_update`` : ISO date string
    """
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, timeout=30.0) as client:
        response = await client.get(DRAMEXCHANGE_URL)
    response.raise_for_status()

    quotes = parse_quotes_from_html(response.text)
    if not quotes:
        return {"status": "requires_manual_or_playwright", "quotes": [], "tables": []}
    return {"status": "success", "quotes": quotes, "last_update": date.today().isoformat()}

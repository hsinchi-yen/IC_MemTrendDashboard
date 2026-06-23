"""
backend/app/jobs/ingest_news.py
==================================
ACTION-048: Fetch memory-industry news via RSS and optionally enrich with LLM.

RSS sources
-----------
* https://feeds.reuters.com/reuters/technologyNews

Keyword filter
--------------
Articles are retained only when their title or summary contains at least one
of: memory, dram, nand, hbm, micron, samsung, sk hynix, kioxia

LLM enrichment
--------------
When ``LLM_API_KEY`` is set and ``LLM_PROVIDER`` is configured, each retained
article's title + summary are sent to the LLM to extract:
  - sentiment  : "bullish" | "bearish" | "neutral"
  - key_points : list[str] (up to 3 bullet points)
  - related_tickers : list[str] (known ticker symbols mentioned)

When the LLM key is absent, those fields are stored as ``null``.

URL is used as the unique key (ON CONFLICT DO NOTHING).
"""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

import feedparser
import httpx
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.news_item import NewsItem

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RSS_FEEDS: list[str] = [
    "https://feeds.reuters.com/reuters/technologyNews",
]

KEYWORDS: list[str] = [
    "memory",
    "dram",
    "nand",
    "hbm",
    "micron",
    "samsung",
    "sk hynix",
    "kioxia",
]

KNOWN_TICKERS: list[str] = [
    "MU", "SNDK", "WDC", "INTC", "NVDA",     # US
    "005930", "000660",                         # KR (Samsung, SK Hynix)
    "285A",                                     # KR (Kioxia if listed)
    "2408", "2344", "3711", "4863",            # TW
]

LLM_TIMEOUT = 20.0


# ---------------------------------------------------------------------------
# Public entry-point
# ---------------------------------------------------------------------------


async def ingest_news(db: AsyncSession) -> dict[str, Any]:
    """Fetch, filter, enrich, and upsert memory-industry news items.

    Parameters
    ----------
    db:
        An active async SQLAlchemy session.

    Returns
    -------
    dict
        ``{"status": "success", "fetched": N, "inserted": M}``
    """
    settings = get_settings()
    fetched = 0
    inserted = 0

    for feed_url in RSS_FEEDS:
        try:
            entries = await _fetch_feed(feed_url)
        except Exception as exc:
            logger.error("ingest_news – failed to fetch %s: %s", feed_url, exc)
            continue

        for entry in entries:
            title: str = entry.get("title", "")
            summary: str = entry.get("summary", "")
            url: str = entry.get("link", "")
            source: str = entry.get("_feed_title", "RSS")

            # Parse published time
            published_struct = entry.get("published_parsed")
            if published_struct:
                published_at = datetime(*published_struct[:6], tzinfo=timezone.utc)
            else:
                published_at = datetime.now(timezone.utc)

            if not url:
                continue

            blob = f"{title} {summary}".lower()
            if not any(kw in blob for kw in KEYWORDS):
                continue

            fetched += 1

            # Optionally enrich with LLM
            enrichment: dict[str, Any] = {
                "sentiment": None,
                "key_points": None,
                "related_tickers": None,
            }
            if settings.LLM_API_KEY:
                try:
                    enrichment = await _llm_enrich(
                        title=title,
                        content=summary,
                        api_key=settings.LLM_API_KEY,
                        provider=settings.LLM_PROVIDER,
                    )
                except Exception as exc:
                    logger.warning(
                        "ingest_news – LLM enrichment failed for '%s': %s",
                        url,
                        exc,
                    )

            payload: dict[str, Any] = {
                "title": title[:500],
                "url": url[:1000],
                "content": summary[:5000] if summary else None,
                "source": source[:100],
                "published_at": published_at,
                **enrichment,
            }

            stmt = insert(NewsItem).values(payload)
            stmt = stmt.on_conflict_do_nothing(constraint="uq_news_item_url")
            result = await db.execute(stmt)
            if result.rowcount:
                inserted += 1

    await db.commit()
    logger.info("ingest_news – fetched=%d inserted=%d", fetched, inserted)
    return {"status": "success", "fetched": fetched, "inserted": inserted}


# ---------------------------------------------------------------------------
# RSS fetching (async)
# ---------------------------------------------------------------------------


async def _fetch_feed(url: str) -> list[dict[str, Any]]:
    """Download and parse an RSS feed; returns a list of entry dicts."""
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(url, follow_redirects=True)
        resp.raise_for_status()
        raw = resp.content

    # feedparser is synchronous – run in thread to avoid blocking
    loop = asyncio.get_event_loop()
    feed = await loop.run_in_executor(None, feedparser.parse, raw)

    feed_title: str = feed.feed.get("title", "RSS") if hasattr(feed, "feed") else "RSS"
    entries: list[dict[str, Any]] = []
    for e in getattr(feed, "entries", []):
        d = dict(e)
        d["_feed_title"] = feed_title
        entries.append(d)
    return entries


# ---------------------------------------------------------------------------
# LLM enrichment
# ---------------------------------------------------------------------------


async def _llm_enrich(
    *,
    title: str,
    content: str,
    api_key: str,
    provider: str,
) -> dict[str, Any]:
    """Call LLM to extract sentiment, key_points, and related_tickers.

    Supports providers: ``gemini``, ``openai``.
    Falls back to heuristics on parse error.
    """
    prompt = (
        "You are a semiconductor industry analyst. Analyse the following news "
        "article and return a JSON object with three keys:\n"
        '  "sentiment": one of "bullish", "bearish", "neutral"\n'
        '  "key_points": array of up to 3 concise bullet-point strings\n'
        '  "related_tickers": array of stock ticker symbols mentioned '
        f'(choose from {KNOWN_TICKERS})\n\n'
        f"Title: {title}\n\nContent: {content[:800]}\n\n"
        "Return ONLY the JSON object."
    )

    if provider == "gemini":
        return await _call_gemini(prompt, api_key)
    if provider == "openai":
        return await _call_openai(prompt, api_key)

    # Unknown provider – fall back to heuristic
    return _heuristic_enrich(title, content)


async def _call_gemini(prompt: str, api_key: str) -> dict[str, Any]:
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-pro:generateContent?key={api_key}"
    )
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        resp = await client.post(url, json=body)
        resp.raise_for_status()
        data = resp.json()

    text = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
    )
    return _parse_llm_json(text)


async def _call_openai(prompt: str, api_key: str) -> dict[str, Any]:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
    }
    async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
        resp = await client.post(url, json=body, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    text = data["choices"][0]["message"]["content"]
    return _parse_llm_json(text)


def _parse_llm_json(text: str) -> dict[str, Any]:
    """Try to parse the LLM response as JSON; fall back to heuristic."""
    try:
        obj = json.loads(text)
        return {
            "sentiment": str(obj.get("sentiment", "neutral")),
            "key_points": obj.get("key_points") or [],
            "related_tickers": obj.get("related_tickers") or [],
        }
    except (json.JSONDecodeError, TypeError):
        return {"sentiment": "neutral", "key_points": [], "related_tickers": []}


def _heuristic_enrich(title: str, content: str) -> dict[str, Any]:
    """Simple keyword-based sentiment + ticker extraction."""
    lower = f"{title} {content}".lower()
    bullish_words = {"rise", "surge", "growth", "rally", "gain", "beat", "outperform"}
    bearish_words = {"fall", "drop", "decline", "loss", "miss", "oversupply", "weak"}
    bull_hits = sum(1 for w in bullish_words if w in lower)
    bear_hits = sum(1 for w in bearish_words if w in lower)
    if bull_hits > bear_hits:
        sentiment = "bullish"
    elif bear_hits > bull_hits:
        sentiment = "bearish"
    else:
        sentiment = "neutral"
    tickers = [t for t in KNOWN_TICKERS if t.lower() in lower or t.upper() in content]
    return {
        "sentiment": sentiment,
        "key_points": [title[:200]],
        "related_tickers": tickers,
    }

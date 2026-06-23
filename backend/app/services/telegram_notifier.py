"""
backend/app/services/telegram_notifier.py
==========================================
Send notifications to a Telegram chat via the Bot API.

Configuration required in environment / .env:
    TELEGRAM_BOT_TOKEN = "123456:ABCDEF..."
    TELEGRAM_CHAT_ID   = "-100123456789"  (group or channel id)

Retries up to 3 times with exponential back-off (1s, 2s, 4s) on transport
errors.  HTTP errors from Telegram (4xx/5xx) are logged but not retried.
"""
from __future__ import annotations

import asyncio
import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


async def send_telegram(message: str, parse_mode: str = "Markdown") -> bool:
    """Send *message* to the configured Telegram chat.

    Parameters
    ----------
    message:
        Text to send.  Supports Markdown formatting when *parse_mode* is
        ``"Markdown"`` (default) or ``"MarkdownV2"`` / ``"HTML"``.
    parse_mode:
        Telegram parse mode.  Defaults to ``"Markdown"``.

    Returns
    -------
    bool
        ``True`` if the message was delivered successfully.
    """
    settings = get_settings()

    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warning("send_telegram – TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not configured")
        return False

    url = (
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    )
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": parse_mode,
    }

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, json=payload)

            if resp.status_code == 200:
                logger.debug("send_telegram – delivered successfully")
                return True

            # Telegram returned an API error – log and do NOT retry
            logger.error(
                "send_telegram – Telegram API error %s: %s",
                resp.status_code,
                resp.text[:300],
            )
            return False

        except httpx.TransportError as exc:
            backoff = 2 ** attempt
            if attempt < 2:
                logger.warning(
                    "send_telegram – transport error (attempt %d/3), retrying in %ds: %s",
                    attempt + 1,
                    backoff,
                    exc,
                )
                await asyncio.sleep(backoff)
            else:
                logger.error("send_telegram – all retries exhausted: %s", exc)

    return False

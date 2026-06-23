"""
backend/app/services/line_notifier.py
======================================
Send notifications via LINE Notify.

Configuration required in environment / .env:
    LINE_NOTIFY_TOKEN = "your_line_notify_token"

LINE Notify is a POST-form endpoint (not JSON).  Retries up to 3 times with
exponential back-off on transport errors.
"""
from __future__ import annotations

import asyncio
import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

LINE_NOTIFY_URL = "https://notify-api.line.me/api/notify"


async def send_line(message: str) -> bool:
    """Send *message* via LINE Notify.

    Parameters
    ----------
    message:
        Text to send.  The LINE Notify API prepends a newline automatically,
        so plain text is fine.

    Returns
    -------
    bool
        ``True`` if the message was delivered (HTTP 200).
    """
    settings = get_settings()

    if not settings.LINE_NOTIFY_TOKEN:
        logger.warning("send_line – LINE_NOTIFY_TOKEN not configured")
        return False

    headers = {"Authorization": f"Bearer {settings.LINE_NOTIFY_TOKEN}"}
    data = {"message": message}

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    LINE_NOTIFY_URL,
                    data=data,
                    headers=headers,
                )

            if resp.status_code == 200:
                logger.debug("send_line – delivered successfully")
                return True

            # API error (e.g. 400 invalid token, 401 unauthorized)
            logger.error(
                "send_line – LINE Notify API error %s: %s",
                resp.status_code,
                resp.text[:300],
            )
            return False  # No retry on API errors

        except httpx.TransportError as exc:
            backoff = 2 ** attempt
            if attempt < 2:
                logger.warning(
                    "send_line – transport error (attempt %d/3), retrying in %ds: %s",
                    attempt + 1,
                    backoff,
                    exc,
                )
                await asyncio.sleep(backoff)
            else:
                logger.error("send_line – all retries exhausted: %s", exc)

    return False

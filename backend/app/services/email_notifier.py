"""
backend/app/services/email_notifier.py
========================================
Send HTML + plain-text multipart e-mails via aiosmtplib (async SMTP).

Configuration required in environment / .env:
    SMTP_HOST      = "smtp.gmail.com"
    SMTP_PORT      = 587
    SMTP_USER      = "user@example.com"
    SMTP_PASS      = "app-password"
    ALERT_EMAIL_TO = "recipient@example.com"   # comma-separated for multiple

The connection uses STARTTLS (port 587).  Retries up to 3 times with
exponential back-off on SMTP / network errors.
"""
from __future__ import annotations

import asyncio
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Sequence

import aiosmtplib

from app.config import get_settings

logger = logging.getLogger(__name__)


async def send_email(
    subject: str,
    plain_text: str,
    html_text: str,
    *,
    to_addresses: Sequence[str] | None = None,
) -> bool:
    """Send a multipart (plain + HTML) e-mail.

    Parameters
    ----------
    subject:
        E-mail subject line.
    plain_text:
        Plain-text body fallback.
    html_text:
        HTML body (displayed by modern mail clients).
    to_addresses:
        Override recipient list.  If *None*, uses ``ALERT_EMAIL_TO`` from
        settings (supports comma-separated addresses).

    Returns
    -------
    bool
        ``True`` if the message was accepted by the SMTP server.
    """
    settings = get_settings()

    # Validate required settings
    required = (settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASS)
    if not all(required):
        logger.warning(
            "send_email – SMTP_HOST / SMTP_USER / SMTP_PASS not fully configured"
        )
        return False

    # Determine recipients
    if to_addresses:
        recipients = list(to_addresses)
    elif settings.ALERT_EMAIL_TO:
        recipients = [addr.strip() for addr in settings.ALERT_EMAIL_TO.split(",") if addr.strip()]
    else:
        logger.warning("send_email – no recipient configured (ALERT_EMAIL_TO is empty)")
        return False

    # Build message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_text, "html", "utf-8"))

    for attempt in range(3):
        try:
            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASS,
                start_tls=True,
            )
            logger.debug("send_email – delivered to %s", recipients)
            return True

        except (aiosmtplib.SMTPException, OSError, TimeoutError) as exc:
            backoff = 2 ** attempt
            if attempt < 2:
                logger.warning(
                    "send_email – SMTP error (attempt %d/3), retrying in %ds: %s",
                    attempt + 1,
                    backoff,
                    exc,
                )
                await asyncio.sleep(backoff)
            else:
                logger.error("send_email – all retries exhausted: %s", exc)

    return False

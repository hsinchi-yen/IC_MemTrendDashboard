"""
backend/app/services/finmind_client.py
Async FinMind API client for Taiwan and US stock price data.

FinMind API docs: https://finmind.github.io/
Endpoint: https://api.finmindtrade.com/api/v4/data
Auth: Bearer token via FINMIND_TOKEN env var

Rate limiting: 0.5 s between requests (module-level singleton).
Retry: 3 attempts with exponential back-off (1 s, 2 s, 4 s).
HTTP 402 → QuotaExceededError (not retried).
"""
from __future__ import annotations

import logging
from datetime import date
from typing import Any

import httpx

from app.config import get_settings
from app.services.http_utils import AsyncRateLimiter, QuotaExceededError

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.finmindtrade.com/api/v4/data"
_TIMEOUT_S = 30.0
_MAX_RETRIES = 3
_BASE_BACKOFF_S = 1.0

# Module-level singleton — shared across all callers in the same process
_rate_limiter = AsyncRateLimiter(min_interval_seconds=0.5)


class FinMindClient:
    """Async FinMind API client.

    Parameters
    ----------
    token:
        FinMind Bearer token. Reads ``FINMIND_TOKEN`` from settings when
        not supplied explicitly.
    """

    BASE_URL = _BASE_URL

    def __init__(self, token: str | None = None) -> None:
        settings = get_settings()
        self._token: str = token or settings.FINMIND_TOKEN
        if not self._token:
            raise RuntimeError(
                "FinMindClient requires a FinMind token. "
                "Set FINMIND_TOKEN in your .env file."
            )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    async def get_tw_stock_price(
        self,
        ticker: str,
        start_date: str | date,
        end_date: str | date,
    ) -> list[dict[str, Any]]:
        """Fetch Taiwan stock daily OHLCV data from FinMind.

        Parameters
        ----------
        ticker:
            Taiwan stock ticker, e.g. ``"2408"`` or ``"8299"``.
        start_date:
            Inclusive start date (``date`` or ISO-8601 string).
        end_date:
            Inclusive end date.

        Returns
        -------
        list[dict]
            Each item has keys: ``date``, ``open``, ``high``, ``low``,
            ``close``, ``volume``.

        Raises
        ------
        QuotaExceededError
            On HTTP 402 — caller should stop further requests.
        httpx.HTTPStatusError
            On other non-2xx responses after all retries are exhausted.
        """
        raw = await self._fetch(
            dataset="TaiwanStockPrice",
            data_id=str(ticker),
            start_date=_to_date(start_date),
            end_date=_to_date(end_date),
        )
        return [_normalise_tw_row(r) for r in raw]

    async def get_us_stock_price(
        self,
        ticker: str,
        start_date: str | date,
        end_date: str | date,
    ) -> list[dict[str, Any]]:
        """Fetch US stock daily OHLCV data from FinMind.

        Parameters
        ----------
        ticker:
            US stock ticker, e.g. ``"MU"``, ``"SNDK"``.
        start_date:
            Inclusive start date.
        end_date:
            Inclusive end date.

        Returns
        -------
        list[dict]
            Each item has keys: ``date``, ``open``, ``high``, ``low``,
            ``close``, ``volume``.

        Raises
        ------
        QuotaExceededError
            On HTTP 402.
        httpx.HTTPStatusError
            On other non-2xx errors.
        """
        raw = await self._fetch(
            dataset="USStockPrice",
            data_id=str(ticker),
            start_date=_to_date(start_date),
            end_date=_to_date(end_date),
        )
        return [_normalise_us_row(r) for r in raw]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _fetch(
        self,
        dataset: str,
        data_id: str,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        """Low-level request with rate-limiting and retry.

        Raises
        ------
        QuotaExceededError
            Immediately on HTTP 402, without retrying.
        httpx.HTTPStatusError
            After all retries are exhausted on other HTTP errors.
        RuntimeError
            If all retries fail for non-HTTP reasons.
        """
        import asyncio

        params: dict[str, Any] = {
            "dataset": dataset,
            "data_id": data_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        headers = {"Authorization": f"Bearer {self._token}"}

        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            await _rate_limiter.wait()
            try:
                async with httpx.AsyncClient(timeout=_TIMEOUT_S) as client:
                    resp = await client.get(
                        self.BASE_URL, params=params, headers=headers
                    )

                if resp.status_code == 402:
                    logger.warning(
                        "FinMind quota exceeded (HTTP 402) for dataset=%s data_id=%s",
                        dataset,
                        data_id,
                    )
                    raise QuotaExceededError(
                        f"FinMind quota exceeded for {dataset}/{data_id}"
                    )

                resp.raise_for_status()
                payload: dict[str, Any] = resp.json()

                # FinMind wraps data in {"status": 200, "data": [...]}
                data = payload.get("data", [])
                if not isinstance(data, list):
                    logger.warning(
                        "Unexpected FinMind response shape for %s/%s: %s",
                        dataset,
                        data_id,
                        type(data),
                    )
                    return []

                logger.debug(
                    "FinMind %s/%s → %d rows (attempt %d)",
                    dataset,
                    data_id,
                    len(data),
                    attempt + 1,
                )
                return data

            except QuotaExceededError:
                raise  # never retry quota errors

            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                last_exc = exc
                if attempt < _MAX_RETRIES - 1:
                    backoff = _BASE_BACKOFF_S * (2**attempt)
                    logger.warning(
                        "FinMind request failed (attempt %d/%d): %s — retrying in %.1fs",
                        attempt + 1,
                        _MAX_RETRIES,
                        exc,
                        backoff,
                    )
                    await asyncio.sleep(backoff)
                else:
                    logger.error(
                        "FinMind request failed after %d attempts for %s/%s: %s",
                        _MAX_RETRIES,
                        dataset,
                        data_id,
                        exc,
                    )

        if last_exc is not None:
            raise last_exc
        raise RuntimeError(f"FinMind fetch failed after {_MAX_RETRIES} retries")


# ---------------------------------------------------------------------------
# Row normalisation helpers
# ---------------------------------------------------------------------------

def _normalise_tw_row(row: dict[str, Any]) -> dict[str, Any]:
    """Map FinMind TaiwanStockPrice fields → standard OHLCV dict."""
    return {
        "date": str(row.get("date", ""))[:10],
        "open": _float_or_none(row.get("open")),
        "high": _float_or_none(row.get("max")),   # FinMind uses "max"/"min"
        "low": _float_or_none(row.get("min")),
        "close": _float_or_none(row.get("close")),
        "volume": _int_or_none(row.get("Trading_Volume") or row.get("volume")),
    }


def _normalise_us_row(row: dict[str, Any]) -> dict[str, Any]:
    """Map FinMind USStockPrice fields → standard OHLCV dict."""
    return {
        "date": str(row.get("date", ""))[:10],
        "open": _float_or_none(row.get("Open") or row.get("open")),
        "high": _float_or_none(row.get("High") or row.get("high")),
        "low": _float_or_none(row.get("Low") or row.get("low")),
        "close": _float_or_none(row.get("Close") or row.get("close")),
        "volume": _int_or_none(row.get("Volume") or row.get("volume")),
    }


# ---------------------------------------------------------------------------
# Util
# ---------------------------------------------------------------------------

def _to_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def _float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(str(value).replace(",", "")))
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Module-level convenience functions (backwards-compatible with existing code)
# ---------------------------------------------------------------------------

async def fetch_finmind(
    dataset: str,
    data_id: str,
    start_date: date,
    end_date: date,
    token: str | None = None,
) -> list[dict[str, Any]]:
    """Module-level helper used by legacy job code.

    Calls FinMind with the given dataset / data_id and returns the raw
    ``data`` list without normalisation (so existing ``normalize_ohlcv_rows``
    callers continue to work).

    Parameters
    ----------
    token:
        Optional per-request FinMind token. When supplied (e.g. provided by
        the user from the UI and stored in localStorage), it overrides
        ``FINMIND_TOKEN`` from the environment.

    Raises
    ------
    QuotaExceededError
        On HTTP 402.
    RuntimeError
        If no FinMind token is available.
    """
    finmind_token = token or get_settings().FINMIND_TOKEN
    if not finmind_token:
        raise RuntimeError("FINMIND_TOKEN is required")

    await _rate_limiter.wait()

    headers = {"Authorization": f"Bearer {finmind_token}"}
    params: dict[str, Any] = {
        "dataset": dataset,
        "data_id": data_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }

    import asyncio

    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT_S) as client:
                resp = await client.get(_BASE_URL, params=params, headers=headers)

            if resp.status_code == 402:
                raise QuotaExceededError("quota_exceeded")

            resp.raise_for_status()
            return resp.json().get("data", [])

        except QuotaExceededError:
            raise

        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < _MAX_RETRIES - 1:
                backoff = _BASE_BACKOFF_S * (2**attempt)
                await asyncio.sleep(backoff)

    if last_exc:
        raise last_exc
    raise RuntimeError("fetch_finmind retry failed")

from typing import Any

import httpx

from app.config import get_settings
from app.services.http_utils import AsyncRateLimiter

settings = get_settings()
rate_limiter = AsyncRateLimiter(12.0)


async def fetch_alpha_vantage_daily(symbol: str) -> list[dict[str, Any]]:
    if not settings.ALPHA_VANTAGE_KEY:
        return []
    await rate_limiter.wait()
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": settings.ALPHA_VANTAGE_KEY,
        "outputsize": "compact",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get("https://www.alphavantage.co/query", params=params)
    response.raise_for_status()
    payload = response.json()
    series = payload.get("Time Series (Daily)", {})
    return [
        {
            "date": trade_date,
            "open": values.get("1. open"),
            "high": values.get("2. high"),
            "low": values.get("3. low"),
            "close": values.get("4. close"),
            "volume": values.get("5. volume"),
        }
        for trade_date, values in series.items()
    ]

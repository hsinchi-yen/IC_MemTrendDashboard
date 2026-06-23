from datetime import date

import math

import yfinance as yf


def _clean(value) -> float | None:
    """Return a float, or None for missing/NaN values."""
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) else f


async def fetch_yfinance_history(symbol: str, start_date: date, end_date: date) -> list[dict]:
    ticker = yf.Ticker(symbol)
    frame = ticker.history(start=start_date.isoformat(), end=end_date.isoformat(), auto_adjust=False)
    results = []
    for idx, row in frame.iterrows():
        close = _clean(row.get("Close"))
        # Skip rows with no usable close (holidays / not-yet-settled sessions).
        if close is None:
            continue
        volume = _clean(row.get("Volume"))
        results.append(
            {
                "date": idx.date().isoformat(),
                "open": _clean(row.get("Open")),
                "high": _clean(row.get("High")),
                "low": _clean(row.get("Low")),
                "close": close,
                "volume": int(volume) if volume is not None else None,
            }
        )
    return results

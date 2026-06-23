from datetime import date

import yfinance as yf


async def fetch_yfinance_history(symbol: str, start_date: date, end_date: date) -> list[dict]:
    ticker = yf.Ticker(symbol)
    frame = ticker.history(start=start_date.isoformat(), end=end_date.isoformat(), auto_adjust=False)
    results = []
    for idx, row in frame.iterrows():
        results.append(
            {
                "date": idx.date().isoformat(),
                "open": float(row["Open"]) if row.get("Open") is not None else None,
                "high": float(row["High"]) if row.get("High") is not None else None,
                "low": float(row["Low"]) if row.get("Low") is not None else None,
                "close": float(row["Close"]) if row.get("Close") is not None else None,
                "volume": int(row["Volume"]) if row.get("Volume") is not None else None,
            }
        )
    return results

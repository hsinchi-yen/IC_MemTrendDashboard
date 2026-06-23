import csv
from datetime import date
from io import StringIO

import httpx


async def fetch_stooq_csv(symbol: str) -> list[dict]:
    url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
    response.raise_for_status()
    text = response.text.strip()
    if not text or text.lower() == "no_data":
        return []
    reader = csv.DictReader(StringIO(text))
    rows = []
    for row in reader:
        rows.append(
            {
                "date": row.get("Date"),
                "open": row.get("Open"),
                "high": row.get("High"),
                "low": row.get("Low"),
                "close": row.get("Close"),
                "volume": row.get("Volume"),
            }
        )
    return rows

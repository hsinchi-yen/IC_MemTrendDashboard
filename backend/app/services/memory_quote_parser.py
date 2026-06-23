from datetime import date
from typing import Any

import httpx
from bs4 import BeautifulSoup


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)


async def fetch_memory_quote_tables() -> dict[str, Any]:
    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, timeout=30.0) as client:
        response = await client.get("https://www.dramexchange.com/")
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    tables = []
    for table in soup.find_all("table"):
        headers = [cell.get_text(" ", strip=True) for cell in table.find_all("th")]
        rows = []
        for tr in table.find_all("tr")[1:3]:
            values = [cell.get_text(" ", strip=True) for cell in tr.find_all(["td", "th"])]
            if values:
                rows.append(values)
        if headers or rows:
            title = "Unknown"
            prev = table.find_previous(["h1", "h2", "h3", "h4", "caption"])
            if prev:
                title = prev.get_text(" ", strip=True)
            tables.append(
                {
                    "table_name": title,
                    "columns": headers,
                    "row_count": len(table.find_all("tr")) - 1,
                    "sample_data": rows,
                    "last_update": date.today().isoformat(),
                }
            )
    if not tables:
        return {"status": "requires_manual_or_playwright", "tables": []}
    return {"status": "success", "tables": tables}

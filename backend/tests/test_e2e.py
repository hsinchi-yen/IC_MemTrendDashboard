"""
backend/tests/test_e2e.py

End-to-end API smoke/integration test for IC_MemTrendDashboard.

Runs the full FastAPI app against an isolated SQLite database, seeds a small
but representative dataset (instruments, prices, quotes, scores, trend metrics,
events, news, correlations, alert rules), then exercises every public endpoint
and asserts on status codes and response shapes.

Run with:
    DATABASE_URL=sqlite+aiosqlite:///./e2e_test.db \
    PYTHONPATH=backend python -m pytest backend/tests/test_e2e.py -v
"""
from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Ensure a SQLite DSN is in place BEFORE app modules import their engine.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./e2e_test.db")

from app.db.database import AsyncSessionLocal, engine  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.main import app  # noqa: E402
from app.models import (  # noqa: E402
    AlertRule,
    CorrelationMatrix,
    EquityPrice,
    Instrument,
    MarketEvent,
    MarketScore,
    MemoryQuote,
    NewsItem,
    TrendMetric,
)

TODAY = date.today()


async def _seed() -> None:
    """Create schema and insert a deterministic fixture dataset."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as s:
        mu = Instrument(ticker="MU", market="US", name="Micron Technology", name_en="Micron",
                        tier="A", supply_chain_tag="memory-maker", currency="USD",
                        is_active=True, score_weight=Decimal("0.08"), score_only_observe=False)
        sams = Instrument(ticker="005930.KS", market="KR", name="Samsung", name_en="Samsung Electronics",
                          tier="A", supply_chain_tag="memory-maker", currency="KRW",
                          is_active=True, score_weight=Decimal("0.10"), score_only_observe=False)
        s.add_all([mu, sams])
        await s.flush()

        # 40 days of prices for MU (trend up)
        for i in range(40):
            d = TODAY - timedelta(days=40 - i)
            base = Decimal("100") + Decimal(i)
            s.add(EquityPrice(instrument_id=mu.id, trade_date=d, open=base, high=base + 2,
                              low=base - 2, close=base + Decimal("0.5"), volume=1_000_000 + i, source="test"))

        # Memory quotes — DRAM + NAND across 30 days
        for i in range(30):
            d = TODAY - timedelta(days=30 - i)
            s.add(MemoryQuote(product="DDR5 16Gb", category="DRAM", price_type="spot",
                              price_avg=Decimal("5.0") + Decimal(i) / 10, change_pct=Decimal("1.2"),
                              currency="USD", snapshot_date=d, source="test"))
            s.add(MemoryQuote(product="NAND 512Gb", category="NAND", price_type="contract",
                              price_avg=Decimal("3.0") + Decimal(i) / 20, change_pct=Decimal("-0.5"),
                              currency="USD", snapshot_date=d, source="test"))

        # Market scores
        for i in range(10):
            d = TODAY - timedelta(days=10 - i)
            s.add(MarketScore(score_date=d, total_score=Decimal("65.5"), quote_momentum_score=Decimal("12"),
                              equity_momentum_score=Decimal("15"), breadth_score=Decimal("10"),
                              risk_score=Decimal("8"), relative_strength_score=Decimal("20"),
                              status="bull", narrative={"summary": "test"}))

        # Trend metrics for MU
        for period in ["1D", "1W", "1M", "3M"]:
            s.add(TrendMetric(instrument_id=mu.id, as_of_date=TODAY, period=period,
                              change_pct=Decimal("3.5"), direction="up", momentum=Decimal("2.1"),
                              ma_state={"ma20": "above"}, volatility=Decimal("1.5"), streak=3,
                              normalized_index=Decimal("72"), narrative="uptrend"))

        # Event, news, correlation, alert rule
        s.add(MarketEvent(event_date=TODAY, title="Test Event", description="d",
                          related_tickers=["MU"], category="earnings"))
        s.add(NewsItem(title="Micron beats", url="https://example.com/1", content="body",
                       source="Reuters", sentiment="positive", key_points=["kp1"],
                       related_tickers=["MU"], published_at=datetime.now(timezone.utc)))
        s.add(CorrelationMatrix(instrument_id=mu.id, quote_product="DDR5 16Gb", window_days=60,
                                coefficient=Decimal("0.75"), as_of_date=TODAY))
        s.add(AlertRule(rule_name="r1", metric="total_score", condition="gt",
                        threshold=Decimal("60"), channel="email", is_active=True))
        await s.commit()


@pytest_asyncio.fixture(scope="module")
async def client():
    await _seed()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# --------------------------------------------------------------------------- #
# Read endpoints — (path, expected_status)
# --------------------------------------------------------------------------- #
READ_CASES = [
    ("/health", 200),
    ("/api/health", 200),
    ("/api/instruments", 200),
    ("/api/instruments?market=US", 200),
    ("/api/instruments?tier=A&is_active=true", 200),
    ("/api/quotes", 200),
    ("/api/quotes?category=DRAM", 200),
    ("/api/quotes/heatmap", 200),
    ("/api/quotes/DDR5 16Gb/sparkline", 200),
    ("/api/score", 200),
    ("/api/score/latest", 200),
    ("/api/trend_metrics/MU?market=US", 200),
    ("/api/trend_metrics/MU?market=US&period=1M", 200),
    ("/api/prices/MU?market=US", 200),
    ("/api/prices/MU?market=US&period=1M", 200),
    ("/api/leaderboard", 200),
    ("/api/leaderboard?period=3M", 200),
    ("/api/trends/chart", 200),
    ("/api/indicators/definitions", 200),
    ("/api/indicators/topbar", 200),
    ("/api/query/stock_table", 200),
    ("/api/query/stock_table?market=US&sort_by=change_pct&sort_order=desc", 200),
    ("/api/refresh/status", 200),
    ("/api/refresh/health", 200),
    ("/api/analysis/correlation?window=60", 200),
    ("/api/analysis/supply-chain", 200),
    ("/api/news/latest", 200),
    ("/api/events", 200),
    ("/api/alerts/rules", 200),
    ("/api/alerts/events", 200),
    # Error paths
    ("/api/score/latest", 200),
    ("/api/prices/NOPE?market=US", 404),
    ("/api/trend_metrics/NOPE?market=US", 404),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("path,expected", READ_CASES)
async def test_read_endpoints(client, path, expected):
    r = await client.get(path)
    assert r.status_code == expected, f"{path} -> {r.status_code}: {r.text[:300]}"


@pytest.mark.asyncio
async def test_instruments_payload(client):
    r = await client.get("/api/instruments")
    body = r.json()
    assert isinstance(body, list) and len(body) >= 2
    assert {"ticker", "market", "tier"} <= set(body[0].keys())


@pytest.mark.asyncio
async def test_heatmap_payload(client):
    r = await client.get("/api/quotes/heatmap")
    body = r.json()
    assert isinstance(body, list) and len(body) >= 1
    assert "changes" in body[0]


@pytest.mark.asyncio
async def test_score_latest_payload(client):
    r = await client.get("/api/score/latest")
    body = r.json()
    assert "total_score" in body and "sub_scores" in body


@pytest.mark.asyncio
async def test_stock_table_csv(client):
    r = await client.get("/api/query/stock_table", headers={"accept": "text/csv"})
    assert r.status_code == 200
    assert "ticker" in r.text


@pytest.mark.asyncio
async def test_event_crud(client):
    payload = {"event_date": TODAY.isoformat(), "title": "CRUD ev", "description": "x",
               "related_tickers": ["MU"], "category": "macro"}
    r = await client.post("/api/events", json=payload)
    assert r.status_code == 200, r.text
    eid = r.json()["id"]
    r = await client.patch(f"/api/events/{eid}", json={**payload, "title": "upd"})
    assert r.status_code == 200 and r.json()["title"] == "upd"
    r = await client.delete(f"/api/events/{eid}")
    assert r.status_code == 204
    r = await client.delete(f"/api/events/{eid}")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_alert_rule_crud(client):
    payload = {"rule_name": "r2", "metric": "total_score", "condition": "gt",
               "threshold": "70", "channel": "email", "is_active": True}
    r = await client.post("/api/alerts/rules", json=payload)
    assert r.status_code == 200, r.text
    rid = r.json()["id"]
    r = await client.patch(f"/api/alerts/rules/{rid}", json={"threshold": "80"})
    assert r.status_code == 200
    # invalid metric rejected
    bad = {**payload, "metric": "bogus"}
    r = await client.post("/api/alerts/rules", json=bad)
    assert r.status_code == 422
    r = await client.delete(f"/api/alerts/rules/{rid}")
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_backtest(client):
    payload = {"entry_condition": "score_gt_60", "exit_condition": "hold_30d",
               "start_date": (TODAY - timedelta(days=10)).isoformat(),
               "end_date": TODAY.isoformat(), "target": "tier_a_basket"}
    r = await client.post("/api/backtest", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "trades" in body and "equity_curve" in body

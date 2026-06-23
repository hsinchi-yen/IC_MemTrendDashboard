"""
backend/app/main.py
FastAPI application entry-point for IC_MemTrendDashboard.
"""
from __future__ import annotations

import logging
import traceback
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .db.database import init_db
from .routers import alerts, analysis, backtest, events, health, indicators, instruments, leaderboard, news, prices, query, quotes, refresh, scores, trends

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Scheduler placeholder callables
# (Real implementations will live in app.tasks.* and be imported here)
# ---------------------------------------------------------------------------


async def _daily_ingestion() -> None:
    """Trigger the nightly data ingestion pipeline (01:00 Asia/Taipei).

    Runs the full orchestrator: ingest TW/US/JP/KR stocks + memory quotes,
    then compute trend metrics, market score, and evaluate alerts.
    """
    logger.info("[scheduler] daily_ingestion – starting …")
    try:
        from .jobs.run_all import run_all_ingestion_jobs

        result = await run_all_ingestion_jobs(trigger="scheduled")
        logger.info("[scheduler] daily_ingestion – finished: %s", result.get("status"))
    except Exception:  # noqa: BLE001
        logger.exception("[scheduler] daily_ingestion – failed.")


async def _daily_summary() -> None:
    """Recompute trend metrics and market scores (05:30 Asia/Taipei).

    A lighter-weight pass that re-derives analytics from already-ingested data,
    in case any late-arriving prices landed after the 01:00 ingestion run.
    """
    logger.info("[scheduler] daily_summary – starting …")
    try:
        from .db.database import AsyncSessionLocal
        from .jobs.compute_market_score import compute_market_score
        from .jobs.compute_trend_metrics import compute_trend_metrics

        async with AsyncSessionLocal() as db:
            await compute_trend_metrics(db)
            await compute_market_score(db)
        logger.info("[scheduler] daily_summary – finished.")
    except Exception:  # noqa: BLE001
        logger.exception("[scheduler] daily_summary – failed.")


# ---------------------------------------------------------------------------
# Scheduler factory
# ---------------------------------------------------------------------------

def _build_scheduler() -> AsyncIOScheduler:
    """Construct and configure the APScheduler instance.

    Returns
    -------
    AsyncIOScheduler
        Configured scheduler (not yet started).
    """
    scheduler = AsyncIOScheduler(timezone="Asia/Taipei")

    scheduler.add_job(
        _daily_ingestion,
        trigger=CronTrigger(hour=1, minute=0, timezone="Asia/Taipei"),
        id="daily_ingestion",
        name="Daily Data Ingestion",
        max_instances=1,
        replace_existing=True,
        misfire_grace_time=3600,
    )

    scheduler.add_job(
        _daily_summary,
        trigger=CronTrigger(hour=5, minute=30, timezone="Asia/Taipei"),
        id="daily_summary",
        name="Daily Summary & Scoring",
        max_instances=1,
        replace_existing=True,
        misfire_grace_time=3600,
    )

    return scheduler


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Startup
    -------
    1. Initialise the database (create tables).
    2. Start the APScheduler.

    Shutdown
    --------
    3. Gracefully stop the APScheduler.
    """
    # ---- Startup ----
    logger.info("IC_MemTrendDashboard API starting up …")

    try:
        await init_db()
    except Exception as exc:
        logger.critical("Database initialisation failed – aborting startup: %s", exc)
        raise

    scheduler = _build_scheduler()
    scheduler.start()
    logger.info("APScheduler started with %d jobs.", len(scheduler.get_jobs()))

    # Expose scheduler on app.state for potential test/admin access
    app.state.scheduler = scheduler

    yield  # Application runs here

    # ---- Shutdown ----
    logger.info("IC_MemTrendDashboard API shutting down …")
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped.")


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="IC MemTrend Dashboard API",
    description=(
        "Backend API for tracking IC memory supply-chain trends, "
        "equity prices, DRAM/NAND quotes, and market health scores."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8510",
        "http://127.0.0.1:8510",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled exceptions.

    Returns a JSON body with a stable error key so clients can pattern-match
    without parsing human-readable strings.
    """
    logger.error(
        "Unhandled exception on %s %s: %s\n%s",
        request.method,
        request.url.path,
        exc,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "detail": str(exc),
        },
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

# /health  – bare path for Docker HEALTHCHECK compatibility
app.include_router(health.router)

# /api/health  – versioned prefix for all API consumers
app.include_router(health.router, prefix="/api")
app.include_router(scores.router, prefix="/api")
app.include_router(quotes.router, prefix="/api")
app.include_router(prices.router, prefix="/api")
app.include_router(events.router, prefix="/api")
app.include_router(backtest.router, prefix="/api")
app.include_router(query.router, prefix="/api")
app.include_router(instruments.router, prefix="/api")
app.include_router(indicators.router, prefix="/api")
app.include_router(refresh.router, prefix="/api")
app.include_router(trends.router, prefix="/api")
app.include_router(leaderboard.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(news.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")

# ---------------------------------------------------------------------------
# Dev entrypoint
# ---------------------------------------------------------------------------
# Run with:  uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        log_level="info",
    )

from app.db.database import AsyncSessionLocal
from app.jobs.common import acquire_refresh_lock, update_refresh_job
from app.jobs.compute_market_score import compute_market_score
from app.jobs.compute_trend_metrics import compute_trend_metrics
from app.jobs.evaluate_alerts import evaluate_alerts
from app.jobs.ingest_jp_stocks import ingest_jp_stocks
from app.jobs.ingest_kr_stocks import ingest_kr_stocks
from app.jobs.ingest_memory_quotes import ingest_memory_quotes
from app.jobs.ingest_tw_stocks import ingest_tw_stocks
from app.jobs.ingest_us_stocks import ingest_us_stocks


async def run_all_ingestion_jobs(trigger: str = "manual") -> dict:
    async with AsyncSessionLocal() as db:
        job = await acquire_refresh_lock(db, "daily_ingestion", trigger)
        if not job:
            return {"status": "skipped", "reason": "job_already_running"}
        results = {}
        try:
            for name, func in [
                ("tw", ingest_tw_stocks),
                ("us", ingest_us_stocks),
                ("jp", ingest_jp_stocks),
                ("kr", ingest_kr_stocks),
                ("quotes", ingest_memory_quotes),
            ]:
                await update_refresh_job(db, job, progress={"current_source": name})
                results[name] = await func(db, trigger=trigger)
            await update_refresh_job(db, job, progress={"current_source": "trend_metrics"})
            results["trend_metrics"] = await compute_trend_metrics(db)
            await update_refresh_job(db, job, progress={"current_source": "market_score"})
            results["market_score"] = await compute_market_score(db)
            await update_refresh_job(db, job, progress={"current_source": "alerts"})
            results["alerts"] = await evaluate_alerts(db)
            await update_refresh_job(db, job, status="success", progress={"current_source": "done"})
            return {"status": "success", "job_id": job.id, "results": results}
        except Exception as exc:  # noqa: BLE001
            await update_refresh_job(db, job, status="fail", error_msg=str(exc))
            return {"status": "fail", "job_id": job.id, "error": str(exc)}

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config.settings import get_settings
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = AsyncIOScheduler()


async def _run_pipeline():
    from app.services.pipeline_orchestrator import NewsPipeline
    db = SessionLocal()
    try:
        pipeline = NewsPipeline(db=db)
        await pipeline.run_full_pipeline()
    except Exception as e:
        logger.error(f"Scheduled pipeline run failed: {e}")
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        _run_pipeline,
        trigger=IntervalTrigger(hours=settings.scheduler_interval_hours),
        id="news_pipeline",
        replace_existing=True,
        misfire_grace_time=300,
    )
    scheduler.start()
    logger.info(
        f"Scheduler started — pipeline runs every {settings.scheduler_interval_hours}h"
    )


def stop_scheduler():
    scheduler.shutdown(wait=False)

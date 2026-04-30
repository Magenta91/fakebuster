from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run")
async def trigger_pipeline(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Triggers a full pipeline run in the background.
    Called by GitHub Actions cron job.
    """
    from app.services.pipeline_orchestrator import NewsPipeline

    async def _run():
        pipeline = NewsPipeline(db=db)
        await pipeline.run_full_pipeline()

    background_tasks.add_task(_run)
    return {"status": "pipeline started"}


@router.post("/refresh-factchecks")
async def refresh_factchecks(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    from app.services.pipeline_orchestrator import NewsPipeline

    async def _run():
        pipeline = NewsPipeline(db=db)
        await pipeline.refresh_factchecks()

    background_tasks.add_task(_run)
    return {"status": "fact-check refresh started"}

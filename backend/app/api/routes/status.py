from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.article import Article
from app.config.settings import get_settings
from datetime import datetime, timedelta

router = APIRouter(prefix="/pipeline", tags=["pipeline"])
settings = get_settings()


@router.get("/status")
def get_pipeline_status(db: Session = Depends(get_db)):
    """
    Returns pipeline status information.
    
    Returns:
        - last_run_time: When the last article was created
        - articles_count: Total articles in database
        - debunked_count: Articles with verdict="debunked"
        - next_scheduled_run: Estimated next run time
        - telegram_enabled: Whether Telegram scraping is enabled
    """
    # Get last article creation time
    last_article = (
        db.query(Article)
        .order_by(Article.created_at.desc())
        .first()
    )
    last_run_time = last_article.created_at if last_article else None
    
    # Count total articles
    articles_count = db.query(Article).count()
    
    # Count debunked articles
    debunked_count = (
        db.query(Article)
        .filter(Article.verdict == "debunked")
        .count()
    )
    
    # Estimate next run (12 hours from last run)
    next_scheduled_run = None
    if last_run_time:
        next_scheduled_run = last_run_time + timedelta(hours=settings.scheduler_interval_hours)
    
    return {
        "last_run_time": last_run_time.isoformat() if last_run_time else None,
        "articles_count": articles_count,
        "debunked_count": debunked_count,
        "next_scheduled_run": next_scheduled_run.isoformat() if next_scheduled_run else None,
        "telegram_enabled": settings.telegram_enabled,
    }

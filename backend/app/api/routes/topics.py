from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.topic import Topic
from app.api.schemas import TopicOut

router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("/", response_model=List[TopicOut])
def get_active_topics(db: Session = Depends(get_db)):
    return (
        db.query(Topic)
        .filter(Topic.is_active == 1)
        .order_by(Topic.trend_score.desc())
        .all()
    )

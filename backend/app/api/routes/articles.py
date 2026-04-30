from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.article import Article
from app.models.topic import Topic
from app.api.schemas import ArticleOut, ArticleDetail

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/", response_model=List[ArticleOut])
def get_articles(
    verdict: Optional[str] = Query(None, description="Filter by verdict: credible|suspicious|debunked"),
    topic_id: Optional[int] = Query(None),
    limit: int = Query(30, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    q = db.query(Article).filter(Article.is_analyzed == 1)
    if verdict:
        q = q.filter(Article.verdict == verdict)
    if topic_id:
        q = q.filter(Article.topic_id == topic_id)
    return (
        q.order_by(Article.published_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/debunked", response_model=List[ArticleOut])
def get_debunked(
    limit: int = Query(30, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    """
    Returns debunked articles including:
    - PIB Fact Check posts (verdict_layer=0, official government fact-checks)
    - Articles debunked by Layer 1 (trusted fact-checkers)
    """
    return (
        db.query(Article)
        .filter(
            Article.verdict == "debunked",
            Article.verdict_layer.in_([0, 1])  # Include both official (0) and fact-checked (1)
        )
        .order_by(Article.published_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{article_id}", response_model=ArticleDetail)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

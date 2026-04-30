from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TopicOut(BaseModel):
    id: int
    name: str
    keywords: str
    trend_score: float
    region: str
    detected_at: datetime

    class Config:
        from_attributes = True


class ArticleOut(BaseModel):
    id: int
    title: str
    summary: Optional[str]
    source_name: str
    url: str
    published_at: Optional[datetime]
    verdict: Optional[str]
    credibility_score: Optional[float]
    confidence: Optional[float]
    verdict_layer: Optional[int]
    topic_id: Optional[int]
    is_factcheck_post: Optional[bool]  # Flag for PIB Fact Check posts
    created_at: datetime

    class Config:
        from_attributes = True


class FactCheckRef(BaseModel):
    id: int
    source_name: str
    claim_text: str
    verdict: str
    source_url: Optional[str]

    class Config:
        from_attributes = True


class ArticleDetail(ArticleOut):
    content: Optional[str]
    explanation: Optional[str]
    corroboration_count: Optional[int]
    corroborating_sources: Optional[str]  # JSON string — parsed on frontend
    factcheck: Optional[FactCheckRef]

    class Config:
        from_attributes = True

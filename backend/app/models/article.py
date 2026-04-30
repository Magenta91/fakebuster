from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    source_name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    content_hash = Column(String, nullable=True, index=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Topic linkage
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    topic = relationship("Topic")

    # Fact-check linkage (populated if layer-1 match found)
    factcheck_id = Column(Integer, ForeignKey("factchecks.id"), nullable=True)
    factcheck = relationship("FactCheck")

    # Verdict
    verdict = Column(String, nullable=True)            # "credible" | "suspicious" | "debunked"
    verdict_layer = Column(Integer, nullable=True)     # 1, 2, or 3
    credibility_score = Column(Float, nullable=True)   # 0.0 – 10.0
    confidence = Column(Float, nullable=True)          # 0.0 – 1.0
    explanation = Column(Text, nullable=True)          # Gemini-generated plain-language summary

    # Embedding for similarity matching
    embedding = Column(Text, nullable=True)            # JSON-serialized float list

    # Source consensus metadata (layer 2)
    corroboration_count = Column(Integer, default=0)
    corroborating_sources = Column(Text, nullable=True)  # JSON list of source names

    is_analyzed = Column(Integer, default=0)
    is_factcheck_post = Column(Integer, default=0)  # 1 = direct from fact-check source (Telegram/PIB)

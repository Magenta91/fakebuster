from sqlalchemy import Column, Integer, String, DateTime, Text, func
from app.db.database import Base


class FactCheck(Base):
    __tablename__ = "factchecks"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String, nullable=False)       # "PIB Fact Check" | "Alpha Defence"
    claim_text = Column(Text, nullable=False)
    verdict = Column(String, nullable=False)           # "false" | "misleading" | "unverified"
    verdict_detail = Column(Text, nullable=True)
    source_url = Column(String, nullable=True)
    embedding = Column(Text, nullable=True)            # JSON-serialized float list
    published_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, server_default=func.now())

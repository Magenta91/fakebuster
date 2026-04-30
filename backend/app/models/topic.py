from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.db.database import Base


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    keywords = Column(String, nullable=False)       # comma-separated
    trend_score = Column(Float, default=0.0)
    region = Column(String, default="global")
    detected_at = Column(DateTime, server_default=func.now())
    is_active = Column(Integer, default=1)          # 1 = active for current cycle

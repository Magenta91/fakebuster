import asyncio
import logging
from typing import List, Dict
from pytrends.request import TrendReq
from app.config.settings import get_settings
from app.config.sources import GEOPOLITICAL_SEED_KEYWORDS

logger = logging.getLogger(__name__)
settings = get_settings()


class TrendDetector:
    """
    Detects daily trending geopolitical topics using Google Trends.
    Returns a list of topic strings to drive the news fetch pipeline.

    To change how trends are detected, subclass this or modify detect().
    """

    def __init__(self):
        self.pytrends = TrendReq(hl="en-US", tz=330)  # IST timezone

    async def detect(self) -> List[Dict]:
        """
        Returns top N trending topics as list of dicts:
            { name, keywords, trend_score, region }
        """
        loop = asyncio.get_event_loop()
        topics = await loop.run_in_executor(None, self._fetch_trends)
        return topics

    def _fetch_trends(self) -> List[Dict]:
        topics = []

        try:
            # India trending searches
            india_trending = self.pytrends.trending_searches(pn="india")
            for term in india_trending[0].tolist()[:settings.trend_topics_count]:
                topics.append({
                    "name": term,
                    "keywords": term,
                    "trend_score": 1.0,
                    "region": "india",
                })
        except Exception as e:
            logger.warning(f"Google Trends India fetch failed: {e}")

        try:
            # Global geopolitical — build interest over time for seed keywords
            self.pytrends.build_payload(
                GEOPOLITICAL_SEED_KEYWORDS[:5],
                timeframe="now 1-d",
                geo="",
            )
            interest = self.pytrends.interest_over_time()
            if not interest.empty:
                scores = interest.mean().drop("isPartial", errors="ignore")
                for kw, score in scores.nlargest(5).items():
                    topics.append({
                        "name": kw,
                        "keywords": kw,
                        "trend_score": float(score),
                        "region": "global",
                    })
        except Exception as e:
            logger.warning(f"Google Trends global fetch failed: {e}")

        # Deduplicate by name
        seen = set()
        unique = []
        for t in topics:
            if t["name"].lower() not in seen:
                seen.add(t["name"].lower())
                unique.append(t)

        return unique[:settings.trend_topics_count]

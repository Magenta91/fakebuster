import httpx
from typing import List, Dict, Any
from datetime import datetime
from app.core.base_fetcher import BaseFetcher
from app.config.settings import get_settings

settings = get_settings()

NEWSAPI_BASE = "https://newsapi.org/v2/everything"


class NewsAPIFetcher(BaseFetcher):
    """Fetches articles from NewsAPI based on topic query."""

    @property
    def source_name(self) -> str:
        return "NewsAPI"

    async def fetch(self, query: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        if not settings.newsapi_key:
            self.logger.warning("NEWSAPI_KEY not set, skipping")
            return []

        params = {
            "q": query or "world news",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": min(limit, 100),
            "apiKey": settings.newsapi_key,
        }

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(NEWSAPI_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()

        articles = []
        for a in data.get("articles", []):
            articles.append({
                "title": a.get("title", ""),
                "url": a.get("url", ""),
                "source": a.get("source", {}).get("name", "Unknown"),
                "published_at": self._parse_date(a.get("publishedAt")),
                "content": a.get("description", "") or a.get("content", ""),
                "credibility": "medium",
            })
        return articles

    def _parse_date(self, date_str: str) -> datetime:
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return datetime.utcnow()

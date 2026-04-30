import httpx
from typing import List, Dict, Any
from datetime import datetime
from app.core.base_fetcher import BaseFetcher
from app.config.sources import RSS_SOURCES, RSSSource, SKIP_KEYWORDS


class RSSFetcher(BaseFetcher):
    """Fetches articles from configured RSS feeds filtered by query keyword."""

    @property
    def source_name(self) -> str:
        return "RSS Fetcher"

    def _should_skip_article(self, title: str, description: str = "") -> bool:
        """Check if article should be skipped based on SKIP_KEYWORDS."""
        text = (title + " " + description).lower()
        return any(keyword.lower() in text for keyword in SKIP_KEYWORDS)

    async def fetch(self, query: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        articles = []
        for source in RSS_SOURCES:
            try:
                import feedparser
                feed = feedparser.parse(source.url)
                for entry in feed.entries[:limit]:
                    title = entry.get("title", "")
                    description = entry.get("summary", "") or entry.get("description", "")
                    
                    # Skip opinion/editorial content
                    if self._should_skip_article(title, description):
                        self.logger.debug(f"Skipping opinion/editorial: {title[:50]}")
                        continue
                    
                    if query and query.lower() not in title.lower():
                        continue
                    
                    articles.append({
                        "title": title,
                        "url": entry.get("link", ""),
                        "source": source.name,
                        "published_at": self._parse_date(entry),
                        "content": description,
                        "credibility": source.credibility,
                    })
            except Exception as e:
                self.logger.warning(f"RSS feed failed: {source.name} — {e}")
        return articles[:limit]

    def _parse_date(self, entry) -> datetime:
        try:
            import time
            t = entry.get("published_parsed") or entry.get("updated_parsed")
            if t:
                return datetime(*t[:6])
        except Exception:
            pass
        return datetime.utcnow()


class TopicRSSFetcher(RSSFetcher):
    """
    Extension of RSSFetcher that accepts a list of topic keywords
    and fetches articles relevant to each topic across all RSS sources.
    """

    async def fetch_for_topics(self, topics: List[str], limit_per_topic: int = 10) -> List[Dict[str, Any]]:
        all_articles = []
        for topic in topics:
            results = await self.safe_fetch(query=topic, limit=limit_per_topic)
            for r in results:
                r["topic_keyword"] = topic
            all_articles.extend(results)
        return all_articles

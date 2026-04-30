from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseFetcher(ABC):
    """
    Base class for all news/data fetchers.
    Subclass this for each data source type (RSS, NewsAPI, Search, etc.)

    To add a new source:
    1. Create a new file in services/fetchers/
    2. Subclass BaseFetcher
    3. Implement fetch() and source_name
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable name for this fetcher."""
        ...

    @abstractmethod
    async def fetch(self, query: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch articles matching the given query.

        Returns a list of dicts with keys:
            title, url, source, published_at, content (optional)
        """
        ...

    async def safe_fetch(self, query: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        """Wraps fetch() with error handling so one broken fetcher never kills the pipeline."""
        try:
            results = await self.fetch(query=query, limit=limit)
            self.logger.info(f"{self.source_name}: fetched {len(results)} articles")
            return results
        except Exception as e:
            self.logger.error(f"{self.source_name}: fetch failed — {e}")
            return []

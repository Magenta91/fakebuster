from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging


class BaseScraper(ABC):
    """
    Base class for all content scrapers.
    Subclass this for different scraping strategies (newspaper3k, playwright, bs4).

    To add a new scraping strategy:
    1. Create a new file in services/scrapers/
    2. Subclass BaseScraper
    3. Implement scrape()
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape content from a URL.

        Returns dict with keys:
            text, title, publish_date, top_image
        Returns None on failure.
        """
        ...

    async def safe_scrape(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            result = await self.scrape(url)
            if result:
                self.logger.debug(f"Scraped: {url}")
            return result
        except Exception as e:
            self.logger.warning(f"Scrape failed for {url} — {e}")
            return None

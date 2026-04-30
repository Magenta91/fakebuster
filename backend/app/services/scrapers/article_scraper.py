import asyncio
from typing import Optional, Dict, Any
from app.core.base_scraper import BaseScraper


class NewspaperScraper(BaseScraper):
    """
    Scrapes article content using newspaper3k.
    Handles standard HTML news pages well.
    """

    async def scrape(self, url: str) -> Optional[Dict[str, Any]]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._scrape_sync, url)

    def _scrape_sync(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            from newspaper import Article as NewspaperArticle
            article = NewspaperArticle(url)
            article.download()
            article.parse()
            return {
                "text": article.text,
                "title": article.title,
                "publish_date": article.publish_date,
                "top_image": article.top_image,
            }
        except Exception as e:
            self.logger.warning(f"newspaper3k failed for {url}: {e}")
            return None


class PlaywrightScraper(BaseScraper):
    """
    Scrapes JS-heavy pages using Playwright.
    Used for Alpha Defence and similar dynamic sites.
    Install with: playwright install chromium
    """

    async def scrape(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=20000)
                text = await page.inner_text("body")
                title = await page.title()
                await browser.close()
                return {
                    "text": text,
                    "title": title,
                    "publish_date": None,
                    "top_image": None,
                }
        except Exception as e:
            self.logger.warning(f"Playwright failed for {url}: {e}")
            return None


def get_scraper(requires_js: bool = False) -> BaseScraper:
    """Factory — returns the right scraper for the source type."""
    if requires_js:
        return PlaywrightScraper()
    return NewspaperScraper()

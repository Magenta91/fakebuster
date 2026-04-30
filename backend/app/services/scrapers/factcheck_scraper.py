import feedparser
import httpx
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
from app.config.sources import FACTCHECK_SOURCES, FactCheckSource
from app.services.scrapers.article_scraper import get_scraper
import logging

logger = logging.getLogger(__name__)


class FactCheckScraper:
    """
    Scrapes fact-check verdicts from all configured FactCheckSource entries.

    To add a new fact-check source:
    1. Add it to config/sources.py FACTCHECK_SOURCES list
    2. If it has an RSS feed, it's handled automatically
    3. If it requires JS, set requires_js=True — PlaywrightScraper handles it
    """

    async def scrape_all(self) -> List[Dict[str, Any]]:
        results = []
        for source in FACTCHECK_SOURCES:
            try:
                items = await self._scrape_source(source)
                logger.info(f"{source.name}: scraped {len(items)} fact-checks")
                results.extend(items)
            except Exception as e:
                logger.error(f"{source.name}: scrape failed — {e}")
        return results

    async def _scrape_source(self, source: FactCheckSource) -> List[Dict[str, Any]]:
        if source.rss_url:
            return self._scrape_rss(source)
        else:
            return await self._scrape_web(source)

    def _scrape_rss(self, source: FactCheckSource) -> List[Dict[str, Any]]:
        try:
            # Fetch with requests to handle BOM and encoding issues
            import requests
            response = requests.get(source.rss_url, timeout=10)
            # Remove BOM and parse with BeautifulSoup for malformed XML
            content = response.content.decode('utf-8-sig')
            soup = BeautifulSoup(content, 'xml')
            items = soup.find_all('item')
            
            results = []
            for item in items:
                title_tag = item.find('title')
                link_tag = item.find('link')
                desc_tag = item.find('description') or item.find('summary')
                
                if not title_tag:
                    continue
                    
                title = title_tag.get_text(strip=True)
                link = link_tag.get_text(strip=True) if link_tag else source.base_url
                description = desc_tag.get_text(strip=True) if desc_tag else ""
                
                results.append({
                    "source_name": source.name,
                    "claim_text": title,
                    "verdict": self._extract_verdict(title + " " + description),
                    "verdict_detail": description,
                    "source_url": link,
                    "published_at": datetime.utcnow(),
                })
            return results
        except Exception as e:
            logger.error(f"RSS scrape failed for {source.name}: {e}")
            return []

    async def _scrape_web(self, source: FactCheckSource) -> List[Dict[str, Any]]:
        scraper = get_scraper(requires_js=source.requires_js)
        result = await scraper.safe_scrape(source.base_url)
        if not result:
            return []
        soup = BeautifulSoup(result["text"], "lxml") if result.get("text") else None
        if not soup:
            return []
        items = []
        # Generic extractor — grabs article headlines from the page
        for tag in soup.find_all(["h2", "h3", "h4"])[:30]:
            text = tag.get_text(strip=True)
            if len(text) > 20:
                items.append({
                    "source_name": source.name,
                    "claim_text": text,
                    "verdict": "false",
                    "verdict_detail": "",
                    "source_url": source.base_url,
                    "published_at": datetime.utcnow(),
                })
        return items

    def _extract_verdict(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["false", "fake", "fabricated", "misinformation"]):
            return "false"
        if any(w in text_lower for w in ["misleading", "partial", "out of context"]):
            return "misleading"
        return "unverified"

    def _parse_date(self, entry) -> datetime:
        try:
            t = entry.get("published_parsed") or entry.get("updated_parsed")
            if t:
                return datetime(*t[:6])
        except Exception:
            pass
        return datetime.utcnow()

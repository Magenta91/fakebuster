import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.fetchers.trend_detector import TrendDetector
from app.services.fetchers.rss_fetcher import TopicRSSFetcher
from app.services.fetchers.newsapi_fetcher import NewsAPIFetcher
from app.services.scrapers.article_scraper import NewspaperScraper
from app.services.scrapers.factcheck_scraper import FactCheckScraper
from app.services.processors.text_cleaner import TextCleaner, ContentHasher
from app.services.processors.embedding_processor import EmbeddingProcessor
from app.services.verifiers.pipeline import VerificationPipeline
from app.models.article import Article
from app.models.topic import Topic
from app.models.factcheck import FactCheck
from app.config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class NewsPipeline:
    """
    Top-level orchestrator for the full pipeline run.

    Run order:
    1. Refresh fact-check DB (PIB, Alpha Defence)
    2. Detect trending topics
    3. Fetch articles for each topic
    4. Scrape + clean article content
    5. Generate embeddings
    6. Run 3-layer verification
    7. Persist to DB

    Each step is isolated — failures in one step don't crash the others.
    """

    def __init__(self, db: Session):
        self.db = db
        self.text_cleaner = TextCleaner()
        self.content_hasher = ContentHasher()
        self.embedding_processor = EmbeddingProcessor()
        self.scraper = NewspaperScraper()
        self.rss_fetcher = TopicRSSFetcher()
        self.newsapi_fetcher = NewsAPIFetcher()
        self.factcheck_scraper = FactCheckScraper()
        self.trend_detector = TrendDetector()

    async def run_full_pipeline(self):
        logger.info("=== Pipeline run started ===")
        
        # Step 0: Scrape Telegram fact-checks FIRST
        await self.scrape_telegram_factchecks()
        
        await self.refresh_factchecks()
        topics = await self.detect_and_store_topics()
        topic_keywords = [t.keywords for t in topics]
        raw_articles = await self.fetch_articles(topic_keywords)
        processed = await self.process_articles(raw_articles)
        await self.verify_and_store(processed, topics)
        logger.info("=== Pipeline run complete ===")

    # ─── Step 0: Telegram fact-check scraping ────────────────────────────────

    async def scrape_telegram_factchecks(self):
        """
        Scrape PIB Fact Check Telegram channel for debunked claims.
        
        IMPORTANT: PIB Fact Check posts are ALREADY OFFICIALLY FACT-CHECKED
        by the Government of India. They skip ALL verification layers:
        - No Layer 1 (factcheck DB matching)
        - No Layer 2 (source consensus)
        - No Layer 3 (Gemini analysis)
        
        These posts are stored directly with:
        - verdict = "debunked" (always)
        - verdict_layer = 0 (no verification needed)
        - credibility_score = 1.0 (maximum)
        - confidence = 1.0 (100%)
        """
        if not settings.telegram_enabled:
            logger.info("Telegram scraping disabled")
            return
        
        try:
            from app.services.scrapers.telegram_scraper import scrape_telegram_factchecks
            
            # Check if this is first run (no Telegram articles in DB)
            existing_count = (
                self.db.query(Article)
                .filter(Article.source_name == "PIB Fact Check")
                .filter(Article.is_factcheck_post == 1)
                .count()
            )
            is_first_run = existing_count == 0
            
            logger.info(f"Scraping Telegram fact-checks (first_run={is_first_run})...")
            articles = await scrape_telegram_factchecks(is_first_run)
            
            stored_count = 0
            for data in articles:
                # Check for duplicate URL
                exists = (
                    self.db.query(Article)
                    .filter(Article.url == data["url"])
                    .first()
                )
                if exists:
                    continue
                
                # Store directly WITHOUT any verification
                # PIB Fact Check posts are already officially fact-checked by the government
                # They skip all 3 verification layers entirely
                article = Article(
                    title=data["title"],
                    content=data["content"],
                    summary=data["content"][:300],
                    source_name=data["source"],
                    url=data["url"],
                    published_at=data["published_at"],
                    verdict=data["verdict"],  # Always "debunked"
                    verdict_layer=0,  # 0 = No verification needed (official source)
                    credibility_score=10.0,  # Maximum credibility (0-10 scale)
                    confidence=1.0,  # 100% confidence
                    explanation="Officially fact-checked and debunked by PIB Fact Check (Government of India)",
                    is_analyzed=1,  # Mark as analyzed
                    is_factcheck_post=1,  # Flag as official fact-check post
                    # No embedding needed - these don't go through verification
                    embedding=None,
                    corroboration_count=0,
                    corroborating_sources=None,
                    factcheck_id=None,
                )
                self.db.add(article)
                stored_count += 1
            
            self.db.commit()
            logger.info(f"Telegram: {stored_count} new fact-check posts stored")
            
        except Exception as e:
            logger.error(f"Telegram scraping failed: {e}")
            # Don't crash the pipeline - continue with regular flow
            self.db.rollback()

    # ─── Step 1: Fact-check refresh ──────────────────────────────────────────

    async def refresh_factchecks(self):
        logger.info("Refreshing fact-check database...")
        items = await self.factcheck_scraper.scrape_all()
        new_count = 0
        for item in items:
            exists = (
                self.db.query(FactCheck)
                .filter(FactCheck.source_url == item.get("source_url"))
                .first()
            )
            if exists:
                continue
            fc = FactCheck(**{k: v for k, v in item.items() if k != "embedding"})
            # Generate embedding for the claim text
            processed = await self.embedding_processor.process(
                {"title": item["claim_text"], "content": ""}
            )
            fc.embedding = processed.get("embedding")
            self.db.add(fc)
            new_count += 1
        self.db.commit()
        logger.info(f"Fact-checks: {new_count} new entries added")

    # ─── Step 2: Trend detection ──────────────────────────────────────────────

    async def detect_and_store_topics(self):
        logger.info("Detecting trending topics...")
        # Deactivate old topics
        self.db.query(Topic).update({"is_active": 0})
        raw_topics = await self.trend_detector.detect()
        stored = []
        for t in raw_topics:
            topic = Topic(
                name=t["name"],
                keywords=t["keywords"],
                trend_score=t["trend_score"],
                region=t["region"],
                is_active=1,
            )
            self.db.add(topic)
            self.db.flush()
            stored.append(topic)
        self.db.commit()
        logger.info(f"Topics: {len(stored)} active topics set")
        return stored

    # ─── Step 3: Article fetching ─────────────────────────────────────────────

    async def fetch_articles(self, topic_keywords: list) -> list:
        logger.info(f"Fetching articles for {len(topic_keywords)} topics...")
        rss_articles = await self.rss_fetcher.fetch_for_topics(
            topic_keywords, limit_per_topic=10
        )
        newsapi_articles = []
        for kw in topic_keywords:
            results = await self.newsapi_fetcher.safe_fetch(
                query=kw, limit=5
            )
            for r in results:
                r["topic_keyword"] = kw
            newsapi_articles.extend(results)

        all_articles = rss_articles + newsapi_articles
        logger.info(f"Fetched {len(all_articles)} raw articles")
        return all_articles

    # ─── Step 4 + 5: Scrape, clean, embed ────────────────────────────────────

    async def process_articles(self, raw_articles: list) -> list:
        logger.info("Processing articles...")
        processed = []
        for raw in raw_articles:
            # Deduplicate by URL
            if not raw.get("url"):
                continue
            exists = (
                self.db.query(Article)
                .filter(Article.url == raw["url"])
                .first()
            )
            if exists:
                continue

            # Scrape full content if only summary available
            if not raw.get("content") or len(raw.get("content", "")) < 200:
                scraped = await self.scraper.safe_scrape(raw["url"])
                if scraped:
                    raw["content"] = scraped.get("text", raw.get("content", ""))

            # Clean text
            raw = self.text_cleaner.safe_process(raw)
            raw = self.content_hasher.safe_process(raw)

            # Deduplicate by content hash
            if raw.get("content_hash"):
                hash_exists = (
                    self.db.query(Article)
                    .filter(Article.content_hash == raw["content_hash"])
                    .first()
                )
                if hash_exists:
                    continue

            # Generate embedding
            raw = await self.embedding_processor.process(raw)
            processed.append(raw)

        logger.info(f"{len(processed)} articles ready for verification")
        return processed

    # ─── Step 6 + 7: Verify and persist ──────────────────────────────────────

    async def verify_and_store(self, articles: list, topics: list):
        logger.info("Running verification pipeline...")
        topic_map = {t.keywords.lower(): t for t in topics}
        verifier = VerificationPipeline(db=self.db)

        stored_count = 0
        for data in articles[: settings.max_articles_per_run]:
            try:
                result = await verifier.run(
                    title=data.get("title", ""),
                    content=data.get("content", ""),
                )

                # Resolve topic FK
                topic_keyword = data.get("topic_keyword", "").lower()
                topic = topic_map.get(topic_keyword)

                article = Article(
                    title=data.get("title", ""),
                    content=data.get("content", ""),
                    summary=data.get("content", "")[:300],
                    source_name=data.get("source", "Unknown"),
                    url=data["url"],
                    content_hash=data.get("content_hash"),
                    published_at=data.get("published_at"),
                    topic_id=topic.id if topic else None,
                    factcheck_id=result.factcheck_id,
                    verdict=result.verdict,
                    verdict_layer=result.layer,
                    credibility_score=result.credibility_score,
                    confidence=result.confidence,
                    explanation=result.explanation,
                    embedding=data.get("embedding"),
                    corroboration_count=result.corroboration_count,
                    corroborating_sources=json.dumps(result.corroborating_sources or []),
                    is_analyzed=1,
                )
                self.db.add(article)
                self.db.commit()
                stored_count += 1
            except Exception as e:
                logger.warning(f"Failed to store article {data.get('url')}: {e}")
                self.db.rollback()
                continue

        logger.info(f"Verification and storage complete: {stored_count} articles stored")

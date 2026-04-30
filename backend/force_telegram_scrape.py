"""
Force scrape latest Telegram posts from PIB Fact Check.
This will fetch the last 200 messages regardless of what's in the database.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.scrapers.telegram_scraper import scrape_telegram_factchecks
from app.db.database import SessionLocal
from app.models.article import Article
from app.models.topic import Topic  # Import Topic to avoid SQLAlchemy error
from app.models.factcheck import FactCheck  # Import all models
from datetime import datetime


async def main():
    print("=" * 60)
    print("FORCE TELEGRAM SCRAPE - PIB Fact Check")
    print("=" * 60)
    print()
    
    # Force first_run mode to get last 200 messages
    print("Fetching last 200 messages from PIB Fact Check channel...")
    articles = await scrape_telegram_factchecks(is_first_run=True)
    
    print(f"✓ Scraped {len(articles)} messages from Telegram")
    print()
    
    if not articles:
        print("No articles found. Check your Telegram credentials.")
        return
    
    # Show date range
    dates = [a["published_at"] for a in articles]
    oldest = min(dates)
    newest = max(dates)
    print(f"Date range: {oldest.strftime('%Y-%m-%d')} to {newest.strftime('%Y-%m-%d')}")
    print()
    
    # Store in database
    db = SessionLocal()
    stored_count = 0
    duplicate_count = 0
    
    try:
        for data in articles:
            # Check for duplicate URL
            exists = db.query(Article).filter(Article.url == data["url"]).first()
            if exists:
                duplicate_count += 1
                continue
            
            # Store as official fact-check (no verification needed)
            article = Article(
                title=data["title"],
                content=data["content"],
                summary=data["content"][:300],
                source_name=data["source"],
                url=data["url"],
                published_at=data["published_at"],
                verdict="debunked",
                verdict_layer=0,  # Official source, no verification needed
                credibility_score=10.0,  # Maximum score (0-10 scale)
                confidence=1.0,
                explanation="Official fact-check from PIB (Press Information Bureau, Government of India). This claim has been officially debunked by the government.",
                is_analyzed=1,
                is_factcheck_post=1,
                created_at=datetime.utcnow(),
            )
            
            db.add(article)
            stored_count += 1
        
        db.commit()
        print(f"✓ Stored {stored_count} new articles")
        print(f"⊘ Skipped {duplicate_count} duplicates")
        print()
        
        # Show latest 5
        print("Latest 5 articles:")
        print("-" * 60)
        for article in sorted(articles, key=lambda x: x["published_at"], reverse=True)[:5]:
            print(f"[{article['published_at'].strftime('%Y-%m-%d %H:%M')}]")
            print(f"  {article['title'][:80]}...")
            print()
        
    finally:
        db.close()
    
    print("=" * 60)
    print("SCRAPE COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

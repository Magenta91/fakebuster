"""
Telegram Scraper for PIB Fact Check Channel

SETUP INSTRUCTIONS:
1. Get TELEGRAM_API_ID and TELEGRAM_API_HASH:
   - Go to https://my.telegram.org
   - Log in with your phone number
   - Click "API development tools"
   - Create a new application (any name/description)
   - Copy the api_id and api_hash values
   
2. Add to .env:
   TELEGRAM_API_ID=your_api_id_here
   TELEGRAM_API_HASH=your_api_hash_here
   TELEGRAM_BOT_TOKEN=your_bot_token_here (if you have one)
   
3. On first run, Telethon will create a session file (pib_scraper.session)
   This file stores authentication - keep it secure and add to .gitignore
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import Message
from app.config.settings import get_settings
from app.config.sources import TELEGRAM_SOURCES

logger = logging.getLogger(__name__)
settings = get_settings()


class TelegramScraper:
    """
    Scrapes PIB Fact Check Telegram channel for debunked claims.
    
    Uses Telethon library to fetch messages from the channel.
    On first run: fetches last 200 messages as backfill.
    On subsequent runs: fetches only last 24 hours.
    """
    
    def __init__(self):
        self.session_file = "pib_scraper"  # Will create pib_scraper.session
        
    async def scrape_all(self, is_first_run: bool = False) -> List[Dict[str, Any]]:
        """
        Scrape all configured Telegram sources.
        
        Args:
            is_first_run: If True, fetch last 200 messages. If False, fetch last 24h.
            
        Returns:
            List of article dictionaries ready for database insertion.
        """
        if not settings.telegram_enabled:
            logger.warning("Telegram scraping disabled in settings")
            return []
            
        if not settings.telegram_api_id or not settings.telegram_api_hash:
            logger.warning("Telegram API credentials not configured - skipping")
            return []
        
        all_articles = []
        
        try:
            # Create Telethon client
            # NOTE: We use user authentication (not bot) because bots cannot
            # read channel message history. Run setup_telegram_session.py first
            # to create the session file interactively.
            client = TelegramClient(
                self.session_file,
                settings.telegram_api_id,
                settings.telegram_api_hash
            )
            
            # Start client - will use existing session if available
            # If no session exists, this will fail (run setup script first)
            await client.start()
            logger.info("Telegram client connected successfully")
            
            for source in TELEGRAM_SOURCES:
                try:
                    articles = await self._scrape_channel(
                        client, 
                        source, 
                        is_first_run
                    )
                    all_articles.extend(articles)
                    logger.info(
                        f"{source.source}: scraped {len(articles)} messages"
                    )
                except Exception as e:
                    logger.error(f"{source.source}: scrape failed — {e}")
                    continue
            
            await client.disconnect()
            
        except Exception as e:
            logger.error(f"Telegram scraper failed: {e}")
            return []
        
        return all_articles
    
    async def _scrape_channel(
        self, 
        client: TelegramClient, 
        source, 
        is_first_run: bool
    ) -> List[Dict[str, Any]]:
        """
        Scrape a single Telegram channel.
        
        Args:
            client: Connected Telethon client
            source: TelegramSource configuration
            is_first_run: Whether this is the first run (backfill mode)
            
        Returns:
            List of article dictionaries
        """
        articles = []
        
        # Determine time range
        if is_first_run:
            # Backfill: get last 200 messages
            limit = 200
            offset_date = None
            logger.info(f"First run: fetching last {limit} messages from {source.source}")
        else:
            # Regular run: get last 24 hours
            limit = None  # No limit, filter by date
            offset_date = datetime.utcnow() - timedelta(hours=24)
            logger.info(f"Regular run: fetching messages from last 24h from {source.source}")
        
        try:
            # Use channel_id (numeric) to identify the channel
            # This is more reliable than username
            # For public channels, we can also try username as fallback
            try:
                async for message in client.iter_messages(
                    source.channel_id,
                    limit=limit,
                    offset_date=offset_date,
                    reverse=False  # Newest first
                ):
                    # Skip if not a Message object
                    if not isinstance(message, Message):
                        continue
                    
                    # Skip forwarded messages
                    if message.forward is not None:
                        continue
                    
                    # Skip messages with no text
                    if not message.text or len(message.text.strip()) < 20:
                        continue
                    
                    # Extract message data
                    article = self._message_to_article(message, source)
                    if article:
                        articles.append(article)
            except Exception as e:
                # Try with username as fallback
                logger.warning(f"Failed with channel_id, trying username: {e}")
                async for message in client.iter_messages(
                    source.username,
                    limit=limit,
                    offset_date=offset_date,
                    reverse=False  # Newest first
                ):
                    # Skip if not a Message object
                    if not isinstance(message, Message):
                        continue
                    
                    # Skip forwarded messages
                    if message.forward is not None:
                        continue
                    
                    # Skip messages with no text
                    if not message.text or len(message.text.strip()) < 20:
                        continue
                    
                    # Extract message data
                    article = self._message_to_article(message, source)
                    if article:
                        articles.append(article)
                    
        except Exception as e:
            logger.error(f"Error iterating messages from {source.source}: {e}")
            raise
        
        return articles
    
    def _message_to_article(self, message: Message, source) -> Dict[str, Any]:
        """
        Convert a Telegram message to FakeBuster article format.
        
        Args:
            message: Telethon Message object
            source: TelegramSource configuration
            
        Returns:
            Article dictionary or None if invalid
        """
        try:
            text = message.text.strip()
            
            # Create title from first 120 chars
            title = text[:120]
            if len(text) > 120:
                title += "..."
            
            # Clean title - remove newlines
            title = " ".join(title.split())
            
            # Build Telegram permalink
            url = f"{source.base_url}/{message.id}"
            
            # Extract photo URLs if any
            photo_urls = []
            if message.photo:
                # Store file_id for later retrieval if needed
                photo_urls.append(f"telegram_photo:{message.photo.id}")
            
            return {
                "title": title,
                "content": text,
                "url": url,
                "source": source.source,
                "verdict": source.verdict,
                "is_factcheck_post": True,
                "published_at": message.date,
                "credibility": "high",
                "photo_urls": photo_urls,
            }
            
        except Exception as e:
            logger.warning(f"Failed to convert message {message.id}: {e}")
            return None


async def scrape_telegram_factchecks(is_first_run: bool = False) -> List[Dict[str, Any]]:
    """
    Convenience function to scrape Telegram fact-checks.
    
    Args:
        is_first_run: Whether this is the first run (backfill mode)
        
    Returns:
        List of article dictionaries
    """
    scraper = TelegramScraper()
    return await scraper.scrape_all(is_first_run)

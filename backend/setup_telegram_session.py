"""
One-time setup script to authenticate Telegram session.

Run this script ONCE to create the session file.
After that, the main app can use the session without prompting.

Usage:
    py -3.13 setup_telegram_session.py

You'll be prompted for:
1. Your phone number (with country code, e.g., +919876543210)
2. The code sent to your Telegram app
3. Your 2FA password (if enabled)

This creates pib_scraper.session file which the app will use.
"""

import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient

# Load environment variables
load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", 0))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
SESSION_FILE = "pib_scraper"

async def main():
    print("=" * 60)
    print("Telegram Session Setup for FakeBuster")
    print("=" * 60)
    print()
    
    if not API_ID or not API_HASH:
        print("ERROR: TELEGRAM_API_ID and TELEGRAM_API_HASH not found in .env")
        print("Please add them to your .env file first.")
        return
    
    print(f"API ID: {API_ID}")
    print(f"API Hash: {API_HASH[:10]}...")
    print()
    
    # Create client
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    
    print("Starting authentication...")
    print("You will be prompted for:")
    print("  1. Your phone number (with country code, e.g., +919876543210)")
    print("  2. The code sent to your Telegram app")
    print("  3. Your 2FA password (if you have one)")
    print()
    
    # Start with user authentication (will prompt for phone)
    # IMPORTANT: Do NOT use bot_token parameter here!
    # We need user authentication to read channel history.
    await client.start()
    
    print()
    print("=" * 60)
    print("SUCCESS! Session file created: pib_scraper.session")
    print("=" * 60)
    print()
    print("You can now run the main app and it will use this session.")
    print("The app will NOT prompt for phone number again.")
    print()
    
    # Test: try to access the PIB channel
    print("Testing channel access...")
    try:
        # Try with username first
        channel = await client.get_entity("PIB_FactCheck")
        print(f"✓ Successfully accessed channel: {channel.title}")
        print(f"  Username: @{channel.username}")
        print(f"  ID: {channel.id}")
        
        # Try fetching a few messages
        print("\nFetching last 5 messages...")
        count = 0
        async for message in client.iter_messages("PIB_FactCheck", limit=5):
            count += 1
            text_preview = message.text[:50] if message.text else "(no text)"
            print(f"  {count}. {text_preview}...")
        print(f"\n✓ Successfully fetched {count} messages")
        
    except Exception as e:
        print(f"✗ Could not access channel: {e}")
    
    await client.disconnect()
    print()
    print("Setup complete!")

if __name__ == "__main__":
    asyncio.run(main())

import json
from app.core.base_processor import BaseProcessor
from app.core.gemini_client import GeminiClient
import asyncio


class EmbeddingProcessor:
    """
    Generates Gemini embeddings for articles and fact-checks.
    Stored as JSON-serialized float list in the DB for similarity matching.

    Async — not a BaseProcessor subclass since it needs await.
    """

    def __init__(self):
        self.client = GeminiClient()

    async def process(self, data: dict) -> dict:
        """Add 'embedding' key (JSON string) to the data dict."""
        text = f"{data.get('title', '')} {data.get('content', '')[:300]}"
        vec = await self.client.embed(text)
        if vec:
            data["embedding"] = json.dumps(vec)
        return data

    async def process_batch(self, items: list) -> list:
        """Process a list of dicts, adding embeddings to each."""
        tasks = [self.process(item) for item in items]
        return await asyncio.gather(*tasks)

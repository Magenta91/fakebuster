import re
import hashlib
from app.core.base_processor import BaseProcessor


class TextCleaner(BaseProcessor):
    """
    Cleans raw scraped article text.
    Normalizes whitespace, removes HTML artifacts, truncates to usable length.
    """

    MAX_CONTENT_LENGTH = 5000

    def process(self, data: dict) -> dict:
        if "content" in data and data["content"]:
            data["content"] = self._clean(data["content"])
        if "title" in data and data["title"]:
            data["title"] = data["title"].strip()
        return data

    def _clean(self, text: str) -> str:
        text = re.sub(r"<[^>]+>", " ", text)           # Strip HTML tags
        text = re.sub(r"&[a-z]+;", " ", text)          # Strip HTML entities
        text = re.sub(r"http\S+", "", text)             # Remove URLs
        text = re.sub(r"\s+", " ", text).strip()        # Normalize whitespace
        return text[:self.MAX_CONTENT_LENGTH]


class ContentHasher(BaseProcessor):
    """
    Generates a content hash for duplicate detection.
    Attach to the pipeline after TextCleaner.
    """

    def process(self, data: dict) -> dict:
        title = data.get("title", "")
        content = data.get("content", "")
        raw = f"{title}{content[:200]}"
        data["content_hash"] = hashlib.md5(raw.encode()).hexdigest()
        return data

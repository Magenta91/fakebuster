import json
import logging
import google.generativeai as genai
from typing import List, Optional
from app.config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

_configured = False


def _configure():
    global _configured
    if not _configured:
        genai.configure(api_key=settings.gemini_api_key)
        _configured = True


class GeminiClient:
    """
    Single wrapper around the Gemini API.
    All LLM and embedding calls go through here.

    To swap providers (e.g. OpenAI), only this file needs to change.
    """

    EMBED_MODEL = "models/gemini-embedding-001"
    CHAT_MODEL = "gemini-2.5-flash"

    def __init__(self):
        _configure()
        self.model = genai.GenerativeModel(self.CHAT_MODEL)

    async def embed(self, text: str) -> Optional[List[float]]:
        """
        Returns a 768-dimensional embedding vector for the given text.
        Returns None on failure.
        """
        try:
            result = genai.embed_content(
                model=self.EMBED_MODEL,
                content=text[:2000],  # Truncate to avoid token limit
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Gemini embed failed: {e}")
            return None

    async def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Embed multiple texts. Returns list of vectors (or None per failure)."""
        results = []
        for text in texts:
            vec = await self.embed(text)
            results.append(vec)
        return results

    async def explain_verdict(
        self,
        title: str,
        content: str,
        verdict: str,
        evidence_summary: str,
    ) -> str:
        """
        Gemini's only decision-making role: write a plain-language explanation
        of WHY a verdict was reached, based on evidence already gathered.

        It does NOT decide the verdict — it explains it.
        """
        prompt = f"""You are a fact-checking assistant. Based on the evidence below, write a clear 2-3 sentence 
explanation for why the following news article is rated as "{verdict}". 
Do not speculate. Only use the provided evidence. Be factual and neutral.

Article title: {title}
Article summary: {content[:500]}

Evidence summary:
{evidence_summary}

Write the explanation:"""

        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini explain failed: {e}")
            return f"This article has been rated {verdict} based on available evidence."

    async def extract_topics_from_trends(self, raw_trends: List[str]) -> List[str]:
        """
        Takes raw Google Trends terms and filters/refines them to geopolitical topics only.
        """
        if not raw_trends:
            return []

        prompt = f"""From the following trending search terms, extract only those that are geopolitical, 
military, diplomatic, or major news topics. Remove entertainment, sports, and trivial trends.
Return as a JSON array of strings. Only return the JSON, nothing else.

Trending terms: {json.dumps(raw_trends)}

JSON output:"""

        try:
            response = await self.model.generate_content_async(prompt)
            text = response.text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            logger.error(f"Gemini topic extraction failed: {e}")
            return raw_trends[:5]


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Pure Python cosine similarity — no torch/numpy needed."""
    if not vec_a or not vec_b:
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = sum(a ** 2 for a in vec_a) ** 0.5
    mag_b = sum(b ** 2 for b in vec_b) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)

import httpx
from typing import Optional, List
from app.core.base_verifier import BaseVerifier, VerificationResult
from app.core.gemini_client import GeminiClient
from app.config.settings import get_settings

settings = get_settings()

# Sources considered high-credibility for consensus scoring
HIGH_CREDIBILITY_SOURCES = [
    "reuters", "associated press", "ap news", "bbc", "the hindu",
    "ndtv", "pti", "ani", "the wire", "scroll", "al jazeera",
    "the guardian", "washington post", "new york times",
]


class ConsensusVerifier(BaseVerifier):
    """
    Layer 2 — Cross-source corroboration.

    Searches for the claim across multiple credible sources.
    High corroboration → credible. Zero corroboration → suspicious.
    """

    @property
    def layer(self) -> int:
        return 2

    def __init__(self):
        super().__init__()
        self.client = GeminiClient()

    async def verify(self, title: str, content: str) -> Optional[VerificationResult]:
        sources = await self._search_corroboration(title)
        count = len(sources)

        # Updated thresholds: 2+ sources = credible, 0-1 = unverified (not suspicious)
        if count >= 2:
            verdict = "credible"
            score = 7.0 if count <= 3 else 9.0
            confidence = 0.7 if count <= 3 else 0.85
        else:
            # Not enough sources - mark as unverified, not suspicious
            verdict = "unverified"
            score = 5.0
            confidence = 0.4

        source_list = ", ".join(sources) if sources else "none found"
        evidence_summary = (
            f"This claim appears in {count} credible source(s): {source_list}."
        )
        explanation = await self.client.explain_verdict(
            title, content, verdict, evidence_summary
        )

        return VerificationResult(
            verdict=verdict,
            confidence=confidence,
            credibility_score=score,
            explanation=explanation,
            layer=2,
            corroboration_count=count,
            corroborating_sources=sources,
        )

    async def _search_corroboration(self, title: str) -> List[str]:
        """
        Uses SerpAPI if key is available, otherwise falls back to
        a basic NewsAPI title search.
        """
        if settings.serpapi_key:
            return await self._serpapi_search(title)
        return await self._newsapi_search(title)

    async def _serpapi_search(self, query: str) -> List[str]:
        params = {
            "q": query,
            "api_key": settings.serpapi_key,
            "num": 10,
            "engine": "google",
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get("https://serpapi.com/search", params=params)
                data = resp.json()
            sources = []
            for result in data.get("organic_results", []):
                domain = result.get("displayed_link", "").lower()
                for credible in HIGH_CREDIBILITY_SOURCES:
                    if credible in domain:
                        sources.append(result.get("source", domain))
                        break
            return list(set(sources))
        except Exception as e:
            self.logger.warning(f"SerpAPI search failed: {e}")
            return []

    async def _newsapi_search(self, query: str) -> List[str]:
        if not settings.newsapi_key:
            return []
        params = {
            "q": query[:100],
            "language": "en",
            "pageSize": 10,
            "apiKey": settings.newsapi_key,
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    "https://newsapi.org/v2/everything", params=params
                )
                data = resp.json()
            sources = []
            for a in data.get("articles", []):
                name = a.get("source", {}).get("name", "").lower()
                for credible in HIGH_CREDIBILITY_SOURCES:
                    if credible in name:
                        sources.append(a["source"]["name"])
                        break
            return list(set(sources))
        except Exception as e:
            self.logger.warning(f"NewsAPI corroboration search failed: {e}")
            return []

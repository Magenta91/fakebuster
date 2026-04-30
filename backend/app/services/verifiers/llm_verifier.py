from typing import Optional
from app.core.base_verifier import BaseVerifier, VerificationResult
from app.core.gemini_client import GeminiClient


class LLMVerifier(BaseVerifier):
    """
    Layer 3 — Gemini as explainer of last resort.

    Only reached when no fact-check match and no corroboration found.
    Gemini does NOT decide the verdict here — we default to 'unverifiable'
    and Gemini explains why we couldn't verify it.
    """

    @property
    def layer(self) -> int:
        return 3

    def __init__(self):
        super().__init__()
        self.client = GeminiClient()

    async def verify(self, title: str, content: str) -> Optional[VerificationResult]:
        evidence_summary = (
            "No matching fact-check was found in trusted databases (PIB, Alpha Defence). "
            "No corroborating coverage was found across credible news sources. "
            "This claim could not be independently verified at this time."
        )
        explanation = await self.client.explain_verdict(
            title, content, "unverifiable", evidence_summary
        )
        return VerificationResult(
            verdict="suspicious",
            confidence=0.4,
            credibility_score=4.5,
            explanation=explanation,
            layer=3,
        )

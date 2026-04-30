import json
from typing import Optional, List
from sqlalchemy.orm import Session
from app.core.base_verifier import BaseVerifier, VerificationResult
from app.core.gemini_client import GeminiClient, cosine_similarity
from app.models.factcheck import FactCheck
from app.config.settings import get_settings

settings = get_settings()


class FactCheckVerifier(BaseVerifier):
    """
    Layer 1 — Semantic match against PIB / Alpha Defence fact-check database.

    If similarity score exceeds threshold, verdict is sourced directly from
    a trusted fact-checker. Highest confidence possible.
    """

    @property
    def layer(self) -> int:
        return 1

    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.client = GeminiClient()

    async def verify(self, title: str, content: str) -> Optional[VerificationResult]:
        article_text = f"{title} {content[:300]}"
        article_vec = await self.client.embed(article_text)
        if not article_vec:
            return None

        # Load all fact-checks that have embeddings
        factchecks: List[FactCheck] = (
            self.db.query(FactCheck)
            .filter(FactCheck.embedding.isnot(None))
            .all()
        )

        best_match = None
        best_score = 0.0

        for fc in factchecks:
            try:
                fc_vec = json.loads(fc.embedding)
                score = cosine_similarity(article_vec, fc_vec)
                if score > best_score:
                    best_score = score
                    best_match = fc
            except Exception:
                continue

        if best_score >= settings.embedding_similarity_threshold and best_match:
            self.logger.info(
                f"Layer 1 match: score={best_score:.3f} source={best_match.source_name}"
            )
            evidence_summary = (
                f"{best_match.source_name} has fact-checked a similar claim "
                f"and rated it as '{best_match.verdict}'. "
                f"Detail: {best_match.verdict_detail or 'No additional detail.'}"
            )
            explanation = await self.client.explain_verdict(
                title, content, best_match.verdict, evidence_summary
            )
            score_map = {"false": 1.0, "misleading": 3.5, "unverified": 5.0}
            return VerificationResult(
                verdict=self._map_verdict(best_match.verdict),
                confidence=best_score,
                credibility_score=score_map.get(best_match.verdict, 5.0),
                explanation=explanation,
                layer=1,
                factcheck_id=best_match.id,
            )

        return None  # No match — pass to Layer 2

    def _map_verdict(self, fc_verdict: str) -> str:
        return {
            "false": "debunked",
            "misleading": "suspicious",
            "unverified": "suspicious",
        }.get(fc_verdict, "suspicious")

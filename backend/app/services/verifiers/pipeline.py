import logging
from sqlalchemy.orm import Session
from app.core.base_verifier import VerificationResult
from app.services.verifiers.factcheck_verifier import FactCheckVerifier
from app.services.verifiers.consensus_verifier import ConsensusVerifier
from app.services.verifiers.headline_verifier import HeadlineVerifier

logger = logging.getLogger(__name__)


class VerificationPipeline:
    """
    Runs the 3-layer verification chain.

    Layer 1 (FactCheckVerifier) → Layer 2 (ConsensusVerifier) → Layer 3 (HeadlineVerifier)

    Each layer returns a VerificationResult or None.
    None means "I can't decide — pass to next layer."
    The first non-None result wins.

    Layer 3 now uses a simple headline-based LLM evaluation instead of
    complex content analysis. This is more transparent and focuses on
    what users see first: the headline.
    """

    def __init__(self, db: Session):
        self.layers = [
            FactCheckVerifier(db=db),
            ConsensusVerifier(),
            HeadlineVerifier(),  # New: Simple headline-based evaluation
        ]

    async def run(self, title: str, content: str) -> VerificationResult:
        for verifier in self.layers:
            try:
                result = await verifier.verify(title=title, content=content)
                if result is not None:
                    logger.info(
                        f"Verified via Layer {result.layer}: "
                        f"verdict={result.verdict} confidence={result.confidence:.2f}"
                    )
                    return result
            except Exception as e:
                logger.error(f"Layer {verifier.layer} crashed: {e}")
                continue

        # Absolute fallback — should never reach here
        return VerificationResult(
            verdict="unverified",
            confidence=0.0,
            credibility_score=5.0,
            explanation="Unable to verify this article through available sources.",
            layer=0,
        )

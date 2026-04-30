from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import logging


@dataclass
class VerificationResult:
    verdict: str                    # "credible" | "suspicious" | "debunked" | "unverifiable"
    confidence: float               # 0.0 – 1.0
    credibility_score: float        # 0.0 – 10.0
    explanation: str
    layer: int                      # 1, 2, or 3 — which layer produced this result
    factcheck_id: Optional[int] = None
    corroboration_count: int = 0
    corroborating_sources: Optional[list] = None


class BaseVerifier(ABC):
    """
    Base class for all verification layers.

    Layer 1 — FactCheckVerifier    : matches against PIB/Alpha Defence DB
    Layer 2 — ConsensusVerifier    : cross-source corroboration check
    Layer 3 — LLMVerifier          : Gemini writes explanation, doesn't decide verdict

    To add a new verification layer:
    1. Create a new file in services/verifiers/
    2. Subclass BaseVerifier
    3. Implement verify()
    4. Register it in services/verifiers/pipeline.py
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    @abstractmethod
    def layer(self) -> int:
        ...

    @abstractmethod
    async def verify(self, title: str, content: str) -> Optional[VerificationResult]:
        """
        Attempt verification. Returns None if this layer cannot produce a verdict,
        which signals the pipeline to move to the next layer.
        """
        ...

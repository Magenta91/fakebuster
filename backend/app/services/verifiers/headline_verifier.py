"""
Headline-based credibility verifier using LLM.

This verifier asks the LLM to evaluate ONLY the headline for credibility,
without looking at the full article content. This provides a quick,
transparent assessment based on the claim itself.
"""

import logging
from typing import Optional
from app.core.base_verifier import BaseVerifier, VerificationResult
from app.core.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


class HeadlineVerifier(BaseVerifier):
    """
    Simple headline-based credibility scorer.
    
    Asks the LLM to evaluate the headline and provide:
    1. Credibility score (0-10)
    2. Brief explanation
    3. Red flags or concerns
    
    This is more transparent than complex multi-layer verification
    and focuses on what users actually see first: the headline.
    """

    @property
    def layer(self) -> int:
        return 3  # Still Layer 3, but simpler approach

    def __init__(self):
        super().__init__()
        self.client = GeminiClient()

    async def verify(self, title: str, content: str) -> Optional[VerificationResult]:
        """
        Evaluate headline credibility using LLM.
        
        Args:
            title: Article headline
            content: Article content (not used, only headline is evaluated)
            
        Returns:
            VerificationResult with credibility score and explanation
        """
        try:
            # Ask LLM to evaluate the headline
            result = await self._evaluate_headline(title)
            
            if result is None:
                # Fallback if LLM fails
                return VerificationResult(
                    verdict="unverified",
                    confidence=0.3,
                    credibility_score=5.0,
                    explanation="Could not evaluate headline credibility.",
                    layer=3,
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Headline verification failed: {e}")
            return VerificationResult(
                verdict="unverified",
                confidence=0.3,
                credibility_score=5.0,
                explanation="Error during headline evaluation.",
                layer=3,
            )

    async def _evaluate_headline(self, headline: str) -> Optional[VerificationResult]:
        """
        Ask LLM to evaluate headline credibility.
        
        Returns:
            VerificationResult with score and explanation
        """
        prompt = f"""You are a fact-checking expert. Evaluate the credibility of this news headline.

Headline: "{headline}"

Analyze this headline for:
1. Sensationalism or clickbait language
2. Vague or unverifiable claims
3. Emotional manipulation
4. Logical consistency
5. Plausibility based on general knowledge

Provide your assessment in this EXACT format:
SCORE: [number from 0-10, where 0=completely false/misleading, 10=highly credible]
VERDICT: [one word: "verified", "unverified", "suspicious", or "debunked"]
EXPLANATION: [2-3 sentences explaining your assessment]

Be objective and factual. Base your score on the headline alone."""

        try:
            response = await self.client.model.generate_content_async(prompt)
            text = response.text.strip()
            
            # Parse the response
            score = self._extract_score(text)
            verdict = self._extract_verdict(text)
            explanation = self._extract_explanation(text)
            
            # Calculate confidence based on how clear the assessment is
            confidence = 0.6 if score > 0 else 0.3
            
            return VerificationResult(
                verdict=verdict,
                confidence=confidence,
                credibility_score=score,
                explanation=explanation,
                layer=3,
            )
            
        except Exception as e:
            logger.error(f"LLM evaluation failed: {e}")
            return None

    def _extract_score(self, text: str) -> float:
        """Extract credibility score from LLM response."""
        try:
            for line in text.split('\n'):
                if line.startswith('SCORE:'):
                    score_str = line.replace('SCORE:', '').strip()
                    # Extract just the number
                    score_str = ''.join(c for c in score_str if c.isdigit() or c == '.')
                    score = float(score_str)
                    return max(0.0, min(10.0, score))  # Clamp to 0-10
        except:
            pass
        return 5.0  # Default to neutral

    def _extract_verdict(self, text: str) -> str:
        """Extract verdict from LLM response."""
        try:
            for line in text.split('\n'):
                if line.startswith('VERDICT:'):
                    verdict = line.replace('VERDICT:', '').strip().lower()
                    # Normalize to our verdict types
                    if 'verified' in verdict or 'credible' in verdict:
                        return 'verified'
                    elif 'debunk' in verdict or 'false' in verdict:
                        return 'debunked'
                    elif 'suspicious' in verdict or 'misleading' in verdict:
                        return 'suspicious'
                    else:
                        return 'unverified'
        except:
            pass
        return 'unverified'  # Default

    def _extract_explanation(self, text: str) -> str:
        """Extract explanation from LLM response."""
        try:
            for i, line in enumerate(text.split('\n')):
                if line.startswith('EXPLANATION:'):
                    # Get this line and any following lines
                    explanation_lines = text.split('\n')[i:]
                    explanation = '\n'.join(explanation_lines)
                    explanation = explanation.replace('EXPLANATION:', '').strip()
                    return explanation
        except:
            pass
        return "Headline evaluated based on general credibility indicators."

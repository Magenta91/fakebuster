"""
Chat API for instant headline verification.

Allows users to submit headlines and get immediate credibility analysis
from the LLM without storing in the database.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.verifiers.headline_verifier import HeadlineVerifier
import logging

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


class HeadlineRequest(BaseModel):
    headline: str


class HeadlineResponse(BaseModel):
    headline: str
    credibility_score: float
    verdict: str
    explanation: str
    confidence: float


@router.post("/verify-headline", response_model=HeadlineResponse)
async def verify_headline(request: HeadlineRequest):
    """
    Verify a user-submitted headline using LLM.
    
    This endpoint allows users to paste any headline and get instant
    credibility analysis without storing it in the database.
    """
    if not request.headline or len(request.headline.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Headline must be at least 10 characters long"
        )
    
    if len(request.headline) > 500:
        raise HTTPException(
            status_code=400,
            detail="Headline must be less than 500 characters"
        )
    
    try:
        verifier = HeadlineVerifier()
        result = await verifier.verify(request.headline.strip(), "")
        
        if result is None:
            raise HTTPException(
                status_code=503,
                detail="AI service temporarily unavailable. Please try again."
            )
        
        return HeadlineResponse(
            headline=request.headline.strip(),
            credibility_score=result.credibility_score,
            verdict=result.verdict,
            explanation=result.explanation,
            confidence=result.confidence,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Headline verification failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to verify headline. Please try again."
        )

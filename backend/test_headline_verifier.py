"""
Test the headline verifier with sample headlines.
"""

import asyncio
from app.services.verifiers.headline_verifier import HeadlineVerifier


async def test_headlines():
    verifier = HeadlineVerifier()
    
    test_cases = [
        "Scientists discover cure for cancer in groundbreaking study",
        "Local man wins lottery twice in same week",
        "Government announces new infrastructure project",
    ]
    
    print("Testing Headline Verifier\n" + "="*60)
    
    for headline in test_cases:
        print(f"\nHeadline: {headline}")
        result = await verifier.verify(headline, "")
        
        if result:
            print(f"  Score: {result.credibility_score}/10")
            print(f"  Verdict: {result.verdict}")
            print(f"  Explanation: {result.explanation}")
        else:
            print("  Failed to evaluate")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(test_headlines())

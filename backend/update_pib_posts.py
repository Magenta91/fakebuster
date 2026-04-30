"""
One-time script to update existing PIB Fact Check posts.

Updates verdict_layer from 1 to 0 to indicate they don't need verification.
Updates credibility_score from 1.0 to 10.0 (maximum on 0-10 scale).
PIB posts are already officially fact-checked by Government of India.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fakebuster.db")

# Create database session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Update all PIB Fact Check posts using raw SQL
    result = db.execute(
        text("""
            UPDATE articles 
            SET verdict_layer = 0,
                credibility_score = 10.0,
                explanation = 'Officially fact-checked and debunked by PIB Fact Check (Government of India)'
            WHERE source_name = 'PIB Fact Check' 
            AND is_factcheck_post = 1
        """)
    )
    
    db.commit()
    print(f"✓ Updated {result.rowcount} PIB Fact Check posts")
    print(f"  - verdict_layer: → 0 (no verification needed)")
    print(f"  - credibility_score: → 10.0 (maximum)")
    print(f"  - explanation: Updated to clarify official source")
    
except Exception as e:
    print(f"✗ Error: {e}")
    db.rollback()
finally:
    db.close()

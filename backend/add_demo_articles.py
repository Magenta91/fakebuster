"""
Add demo articles with varying credibility scores for demonstration purposes.

These are fake/suspicious articles designed to show the system's ability
to detect misinformation and assign appropriate credibility scores.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fakebuster.db")

# Create database session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Demo articles with varying credibility
demo_articles = [
    {
        "title": "Scientists Discover Aliens Living Among Us in Major Cities, Government Confirms",
        "content": "In a shocking revelation, scientists claim to have discovered extraterrestrial beings living disguised as humans in major cities worldwide. Government officials have allegedly confirmed the findings but refuse to provide evidence.",
        "summary": "Scientists claim aliens are living among us in cities, government allegedly confirms without evidence.",
        "source_name": "Unverified News Network",
        "url": "https://example.com/fake-news-1",
        "verdict": "suspicious",
        "verdict_layer": 3,
        "credibility_score": 1.5,
        "confidence": 0.8,
        "explanation": "This headline contains extraordinary claims without credible evidence. The use of vague sources ('scientists claim', 'government confirms') and sensational language are red flags for misinformation.",
        "published_at": datetime.utcnow() - timedelta(hours=2),
    },
    {
        "title": "Drinking 10 Glasses of Soda Daily Cures All Diseases, New Study Claims",
        "content": "A controversial new study suggests that consuming large amounts of carbonated beverages can cure various diseases. Medical experts have not verified these claims, and the study's methodology remains questionable.",
        "summary": "Unverified study claims soda consumption cures diseases, lacks medical expert verification.",
        "source_name": "Health Myths Daily",
        "url": "https://example.com/fake-news-2",
        "verdict": "suspicious",
        "verdict_layer": 3,
        "credibility_score": 2.0,
        "confidence": 0.9,
        "explanation": "This headline promotes dangerous health misinformation. The claim contradicts established medical science and lacks credible sources. Such articles can cause harm by encouraging unhealthy behaviors.",
        "published_at": datetime.utcnow() - timedelta(hours=5),
    },
    {
        "title": "Local Woman Wins Lottery 50 Times in One Month Using This One Weird Trick",
        "content": "A woman from an unnamed city claims to have won the lottery 50 times in 30 days using a secret method. Lottery officials deny any such wins occurred, but the story continues to circulate online.",
        "summary": "Unverified claim of winning lottery 50 times, lottery officials deny the story.",
        "source_name": "Clickbait Central",
        "url": "https://example.com/fake-news-3",
        "verdict": "suspicious",
        "verdict_layer": 3,
        "credibility_score": 1.0,
        "confidence": 0.95,
        "explanation": "Classic clickbait headline using 'one weird trick' language. The claim is statistically impossible and contradicted by official sources. Designed to generate clicks rather than inform.",
        "published_at": datetime.utcnow() - timedelta(hours=8),
    },
    {
        "title": "5G Towers Confirmed to Control Weather Patterns, Experts Warn",
        "content": "Anonymous experts claim that 5G cellular towers are being used to manipulate weather patterns globally. No scientific evidence supports these claims, and meteorologists have dismissed the theory.",
        "summary": "Baseless claim that 5G towers control weather, dismissed by meteorologists.",
        "source_name": "Conspiracy Watch",
        "url": "https://example.com/fake-news-4",
        "verdict": "suspicious",
        "verdict_layer": 3,
        "credibility_score": 1.5,
        "confidence": 0.9,
        "explanation": "This headline spreads a debunked conspiracy theory. It uses vague attribution ('experts warn') and makes scientifically impossible claims. No credible evidence supports this narrative.",
        "published_at": datetime.utcnow() - timedelta(hours=12),
    },
    {
        "title": "Breaking: Moon Landing Footage Found to Be Filmed in Hollywood Studio",
        "content": "A viral video claims to show evidence that the 1969 moon landing was filmed in a Hollywood studio. Space agencies and historians have repeatedly debunked this conspiracy theory with overwhelming evidence.",
        "summary": "Debunked conspiracy theory about moon landing being fake resurfaces online.",
        "source_name": "Alternative Facts Media",
        "url": "https://example.com/fake-news-5",
        "verdict": "debunked",
        "verdict_layer": 3,
        "credibility_score": 0.5,
        "confidence": 1.0,
        "explanation": "This is a long-debunked conspiracy theory that contradicts extensive scientific evidence and historical documentation. The moon landing has been verified by multiple independent sources worldwide.",
        "published_at": datetime.utcnow() - timedelta(hours=15),
    },
]

try:
    from sqlalchemy import text
    
    print("Adding demo articles to database...\n")
    
    for i, article_data in enumerate(demo_articles, 1):
        # Check if article already exists
        result = db.execute(
            text("SELECT id FROM articles WHERE url = :url"),
            {"url": article_data["url"]}
        ).first()
        
        if result:
            print(f"  {i}. Already exists: {article_data['title'][:60]}...")
            continue
        
        # Insert article using raw SQL
        db.execute(
            text("""
                INSERT INTO articles (
                    title, content, summary, source_name, url, verdict, verdict_layer,
                    credibility_score, confidence, explanation, published_at,
                    is_analyzed, is_factcheck_post, topic_id
                ) VALUES (
                    :title, :content, :summary, :source_name, :url, :verdict, :verdict_layer,
                    :credibility_score, :confidence, :explanation, :published_at,
                    :is_analyzed, :is_factcheck_post, :topic_id
                )
            """),
            {
                "title": article_data["title"],
                "content": article_data["content"],
                "summary": article_data["summary"],
                "source_name": article_data["source_name"],
                "url": article_data["url"],
                "verdict": article_data["verdict"],
                "verdict_layer": article_data["verdict_layer"],
                "credibility_score": article_data["credibility_score"],
                "confidence": article_data["confidence"],
                "explanation": article_data["explanation"],
                "published_at": article_data["published_at"],
                "is_analyzed": 1,
                "is_factcheck_post": 0,
                "topic_id": None,
            }
        )
        
        print(f"  {i}. Added: {article_data['title'][:60]}...")
        print(f"     Score: {article_data['credibility_score']}/10 | Verdict: {article_data['verdict']}")
    
    db.commit()
    print(f"\n✓ Successfully added {len(demo_articles)} demo articles")
    print("\nThese articles will appear in the feed to demonstrate the system's")
    print("ability to detect and flag misinformation with low credibility scores.")
    
except Exception as e:
    print(f"✗ Error: {e}")
    db.rollback()
finally:
    db.close()

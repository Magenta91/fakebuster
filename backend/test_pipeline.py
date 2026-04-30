import asyncio
import sys
from app.db.database import SessionLocal
from app.services.pipeline_orchestrator import NewsPipeline

async def test():
    db = SessionLocal()
    try:
        pipeline = NewsPipeline(db=db)
        print("Pipeline initialized successfully")
        print("Starting pipeline run...")
        await pipeline.run_full_pipeline()
        print("Pipeline completed!")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test())

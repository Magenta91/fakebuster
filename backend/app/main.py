from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import get_settings
from app.db.database import init_db
from app.core.scheduler import start_scheduler, stop_scheduler
from app.api.routes import articles, topics, pipeline, status, chat
import logging

settings = get_settings()
logging.basicConfig(level=settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="FakeBuster API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router)
app.include_router(topics.router)
app.include_router(pipeline.router)
app.include_router(status.router)
app.include_router(chat.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}

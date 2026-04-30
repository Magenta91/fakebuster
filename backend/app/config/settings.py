from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./fakebuster.db"

    # API Keys
    newsapi_key: str = ""
    gemini_api_key: str = ""
    serpapi_key: str = ""
    
    # Telegram
    telegram_enabled: bool = True
    telegram_bot_token: str = ""
    telegram_api_id: int = 0
    telegram_api_hash: str = ""

    # App
    base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    log_level: str = "INFO"
    environment: str = "development"

    # Pipeline config
    max_articles_per_run: int = 50
    trend_topics_count: int = 8
    embedding_similarity_threshold: float = 0.72
    scheduler_interval_hours: int = 12

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

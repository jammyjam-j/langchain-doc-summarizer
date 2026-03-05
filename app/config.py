import os
from pathlib import Path

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    app_name: str = Field("langchain-doc-summarizer", env="APP_NAME")
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    database_url: str = Field(..., env="DATABASE_URL")
    celery_broker_url: str = Field(..., env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(..., env="CELERY_RESULT_BACKEND")
    openai_api_key: str | None = Field(None, env="OPENAI_API_KEY")
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_db: int = Field(0, env="REDIS_DB")

    @validator("log_level")
    def validate_log_level(cls, v):
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v.upper()

    @validator("database_url")
    def database_url_must_be_non_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("DATABASE_URL cannot be empty")
        return v

    @root_validator
    def check_openai_key_for_summarizer(cls, values):
        openai_key = values.get("openai_api_key")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY is required for summarization")
        return values


settings = Settings()

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

if not TEMPLATES_DIR.exists():
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
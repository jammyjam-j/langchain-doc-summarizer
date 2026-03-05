import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import BaseSettings

from .config import Settings
from .services.document_processor import DocumentProcessor
from .services.summarizer import Summarizer
from .utils.logger import get_logger

__all__ = [
    "app",
    "settings",
    "document_processor",
    "summarizer",
]

class AppConfig(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"

settings = AppConfig()

logger = get_logger(__name__)

try:
    from .main import app
except Exception as exc:
    logger.exception("Failed to import FastAPI application: %s", exc)
    raise

document_processor = DocumentProcessor()
summarizer = Summarizer()
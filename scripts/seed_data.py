#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.models import Base, Document
from app.services.document_processor import DocumentProcessor
from app.utils.logger import get_logger
from app.utils.file_handler import read_text_file

logger = get_logger(__name__)

def create_database_engine():
    from sqlalchemy import create_engine
    engine = create_engine(settings.DATABASE_URL)
    return engine

def init_db(engine):
    Base.metadata.create_all(bind=engine)

def seed_documents(session, processor: DocumentProcessor, source_dir: Path):
    for file_path in source_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in {".txt", ".md"}:
            try:
                content = read_text_file(file_path)
                processed = processor.process(content)
                doc = Document(
                    title=file_path.stem,
                    path=str(file_path),
                    raw_content=content,
                    processed_content=processed
                )
                session.add(doc)
                session.commit()
                logger.info(f"Inserted document: {file_path}")
            except Exception as exc:
                session.rollback()
                logger.error(f"Failed to insert {file_path}: {exc}")

def main():
    engine = create_database_engine()
    init_db(engine)
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        processor = DocumentProcessor()
        seed_dir = Path(settings.SEED_DATA_DIR).expanduser().resolve()
        if not seed_dir.is_dir():
            logger.error(f"Seed data directory does not exist: {seed_dir}")
            sys.exit(1)
        seed_documents(session, processor, seed_dir)
    finally:
        session.close()

if __name__ == "__main__":
    main()
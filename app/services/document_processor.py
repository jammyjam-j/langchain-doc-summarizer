import os
from pathlib import Path
from typing import List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.utils.logger import get_logger
from app.config import Settings

logger = get_logger(__name__)

class DocumentProcessor:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )

    def load_file(self, file_path: str | Path) -> str:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        try:
            return path.read_text(encoding="utf-8")
        except Exception as exc:
            logger.exception("Failed to read file %s", file_path)
            raise RuntimeError(f"Could not read file {file_path}") from exc

    def process(self, text: str) -> List[Document]:
        try:
            chunks = self.splitter.split_text(text)
            documents = [Document(page_content=chunk) for chunk in chunks]
            return documents
        except Exception as exc:
            logger.exception("Failed to split text into documents")
            raise RuntimeError("Text splitting failed") from exc

    def process_file(self, file_path: str | Path) -> List[Document]:
        raw_text = self.load_file(file_path)
        return self.process(raw_text)

    def validate_documents(self, documents: List[Document]) -> bool:
        if not documents:
            raise ValueError("No documents to validate")
        for doc in documents:
            if not isinstance(doc.page_content, str) or not doc.page_content.strip():
                raise ValueError("Invalid document content detected")
        return True

    def summarize_documents(self, documents: List[Document]) -> str:
        from app.services.summarizer import Summarizer

        summarizer = Summarizer()
        combined_text = "\n".join(doc.page_content for doc in documents)
        summary = summarizer.summarize(combined_text)
        return summary

    def process_and_summarize(self, file_path: str | Path) -> str:
        docs = self.process_file(file_path)
        self.validate_documents(docs)
        return self.summarize_documents(docs)

if __name__ == "__main__":
    processor = DocumentProcessor()
    sample_path = os.getenv("SAMPLE_DOC_PATH", "sample.txt")
    try:
        summary_text = processor.process_and_summarize(sample_path)
        print(summary_text)
    except Exception as e:
        logger.error("Error in processing: %s", e)
import argparse
import sys

from app.config import Settings
from app.services.document_processor import DocumentProcessor
from app.services.summarizer import Summarizer
from app.utils.logger import get_logger


def _ingest(args):
    logger = get_logger()
    processor = DocumentProcessor(settings=Settings())
    try:
        result = processor.ingest_file(file_path=args.file)
        print(f"Ingestion successful: {result}")
    except Exception as exc:
        logger.error("Ingestion failed", exc_info=True)
        sys.exit(1)


def _summarize(args):
    logger = get_logger()
    summarizer = Summarizer(settings=Settings())
    try:
        summary = summarizer.summarize_document(document_id=args.id, length=args.length)
        print(summary)
    except Exception as exc:
        logger.error("Summarization failed", exc_info=True)
        sys.exit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="LangChain Doc Summarizer CLI")
    subparsers = parser.add_subparsers(dest="command")

    ingest_parser = subparsers.add_parser("ingest", help="Ingest a document")
    ingest_parser.add_argument("--file", required=True, type=str, help="Path to the document file")
    ingest_parser.set_defaults(func=_ingest)

    summarize_parser = subparsers.add_parser("summarize", help="Summarize an ingested document")
    summarize_parser.add_argument("--id", required=True, type=int, help="Document ID to summarize")
    summarize_parser.add_argument("--length", default="short", choices=["short", "medium", "long"], help="Summary length")
    summarize_parser.set_defaults(func=_summarize)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
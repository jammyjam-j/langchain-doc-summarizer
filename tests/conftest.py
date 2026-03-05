import os
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app as fastapi_app
from app.services.document_processor import DocumentProcessor
from app.services.summarizer import Summarizer


@pytest.fixture(scope="session")
def base_dir() -> Path:
    return Path(__file__).parent.parent.resolve()


@pytest.fixture(scope="session")
def temp_storage(base_dir) -> Path:
    storage_path = base_dir / "temp_test_storage"
    if storage_path.exists():
        shutil.rmtree(storage_path)
    storage_path.mkdir(parents=True, exist_ok=True)
    yield storage_path
    shutil.rmtree(storage_path)


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(fastapi_app)


@pytest.fixture(scope="function")
def document_processor(temp_storage) -> DocumentProcessor:
    processor = DocumentProcessor(base_dir=Path(__file__).parent.parent.resolve())
    yield processor


@pytest.fixture(scope="function")
def summarizer() -> Summarizer:
    yield Summarizer()


@pytest.fixture(scope="module", autouse=True)
def setup_app():
    yield
    # Any global teardown can be placed here if needed

@pytest.fixture(scope="session")
def valid_pdf_path(base_dir) -> Path:
    pdf_path = base_dir / "tests" / "sample.pdf"
    assert pdf_path.exists(), f"Sample PDF not found at {pdf_path}"
    return pdf_path


@pytest.fixture(scope="session")
def valid_text_path(base_dir) -> Path:
    text_path = base_dir / "tests" / "sample.txt"
    assert text_path.exists(), f"Sample text file not found at {text_path}"
    return text_path

@pytest.fixture(scope="module")
def sample_payload(valid_pdf_path, valid_text_path):
    return {
        "pdf_url": str(valid_pdf_path),
        "text_file_url": str(valid_text_path)
    }
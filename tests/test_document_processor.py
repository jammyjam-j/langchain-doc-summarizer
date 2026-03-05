import os
import tempfile
import shutil

import pytest

from app.services.document_processor import DocumentProcessor
from app.utils.file_handler import read_file_content


@pytest.fixture
def processor():
    return DocumentProcessor()


@pytest.fixture
def sample_text():
    return "This is a test document. It contains multiple sentences for processing."


@pytest.fixture
def temp_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.4\n%...")
    return str(pdf_path)


@pytest.fixture
def temp_docx(tmp_path):
    docx_path = tmp_path / "sample.docx"
    with open(docx_path, "wb") as f:
        f.write(b"PK\x03\x04")
    return str(docx_path)


@pytest.fixture
def temp_txt(tmp_path, sample_text):
    txt_path = tmp_path / "sample.txt"
    txt_path.write_text(sample_text)
    return str(txt_path)


def test_read_file_content_with_supported_formats(processor, temp_pdf, temp_docx, temp_txt, sample_text):
    pdf_text = processor.read_file(temp_pdf)
    docx_text = processor.read_file(temp_docx)
    txt_text = processor.read_file(temp_txt)

    assert isinstance(pdf_text, str) or pdf_text is None
    assert isinstance(docx_text, str) or docx_text is None
    assert txt_text == sample_text


def test_read_file_content_with_unsupported_format(processor):
    with tempfile.NamedTemporaryFile(suffix=".exe") as tmp:
        tmp.write(b"")
        tmp.flush()
        result = processor.read_file(tmp.name)
        assert result is None


def test_process_text_returns_non_empty_summary(processor, sample_text):
    summary = processor.process_text(sample_text)
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert "test document" in summary.lower()


def test_process_text_handles_empty_input(processor):
    empty_summary = processor.process_text("")
    assert isinstance(empty_summary, str)
    assert empty_summary == ""


def test_document_processor_integration_with_file_handler(sample_text, temp_txt, processor):
    content = read_file_content(temp_txt)
    assert content == sample_text
    summary = processor.process_text(content)
    assert len(summary) > 0


def test_document_processor_handles_io_errors(processor):
    with pytest.raises(FileNotFoundError):
        processor.read_file("non_existent_file.xyz")


def test_document_processor_process_large_input(processor, sample_text):
    large_text = " ".join([sample_text] * 100)
    summary = processor.process_text(large_text)
    assert isinstance(summary, str)
    assert len(summary) > 0


@pytest.mark.parametrize(
    "text,expected_contains",
    [
        ("The quick brown fox jumps over the lazy dog.", ["quick", "brown"]),
        ("Python programming is fun and versatile.", ["python", "programming"]),
    ],
)
def test_process_text_content_check(processor, text, expected_contains):
    summary = processor.process_text(text)
    for word in expected_contains:
        assert word.lower() in summary.lower()


def test_document_processor_with_invalid_file_type(processor):
    with tempfile.NamedTemporaryFile(suffix=".invalid") as tmp:
        tmp.write(b"")
        tmp.flush()
        result = processor.read_file(tmp.name)
        assert result is None


def test_summary_length_consistency(processor, sample_text):
    summary_short = processor.process_text(sample_text[:10])
    summary_full = processor.process_text(sample_text)
    assert len(summary_full) >= len(summary_short)


def test_document_processor_error_handling_on_read_failure(monkeypatch, processor):
    def mock_open(*args, **kwargs):
        raise IOError("Mock read error")

    monkeypatch.setattr(processor, "open", mock_open)

    with pytest.raises(IOError):
        processor.read_file("anyfile.txt")
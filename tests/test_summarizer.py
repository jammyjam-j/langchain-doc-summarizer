import pytest
from unittest.mock import MagicMock

from app.services.summarizer import Summarizer
from app.config import Settings


@pytest.fixture(scope="module")
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope="module")
def summarizer(settings: Settings) -> Summarizer:
    return Summarizer(settings)


def test_summarizer_initialization(summarizer: Summarizer):
    assert hasattr(summarizer, "llm_chain"), "Summarizer should have llm_chain attribute"
    assert callable(
        getattr(summarizer.llm_chain, "run", None)
    ), "llm_chain.run should be callable"


def test_summarize_returns_string_with_mocked_chain(summarizer: Summarizer):
    mock_output = "This is a summary."
    summarizer.llm_chain.run = MagicMock(return_value=mock_output)

    input_text = (
        "Artificial intelligence (AI) refers to the simulation of human intelligence "
        "in machines that are programmed to think like humans and mimic their actions."
    )
    result = summarizer.summarize(input_text)
    assert isinstance(result, str), "Summarizer should return a string"
    assert result == mock_output, "Result should match mocked output"
    summarizer.llm_chain.run.assert_called_once_with(
        input_text,
        max_length=150,
        temperature=0.7,
    )


def test_summarize_raises_value_error_on_empty_input(summarizer: Summarizer):
    with pytest.raises(ValueError) as exc_info:
        summarizer.summarize("")
    assert "Input text must not be empty" in str(exc_info.value)


def test_summarize_propagates_chain_exceptions(summarizer: Summarizer):
    summarizer.llm_chain.run = MagicMock(side_effect=RuntimeError("Chain failure"))
    with pytest.raises(RuntimeError) as exc_info:
        summarizer.summarize("Sample text")
    assert "Chain failure" in str(exc_info.value)


def test_summarize_with_long_text(summarizer: Summarizer):
    long_text = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. " * 20
    )
    mock_output = "Long summary."
    summarizer.llm_chain.run = MagicMock(return_value=mock_output)

    result = summarizer.summarize(long_text)
    assert isinstance(result, str)
    assert result == mock_output
    summarizer.llm_chain.run.assert_called_once_with(
        long_text,
        max_length=150,
        temperature=0.7,
    )


def test_summarizer_summary_length_limit(summarizer: Summarizer):
    input_text = "Short text."
    mock_output = "This is a very long summary that exceeds the maximum length specified by the summarizer chain to ensure proper truncation behavior in downstream processing."
    summarizer.llm_chain.run = MagicMock(return_value=mock_output)

    result = summarizer.summarize(input_text)
    assert isinstance(result, str)
    assert len(result) <= 150


def test_summarizer_invalid_settings(monkeypatch):
    monkeypatch.setattr("app.services.summarizer.Settings", lambda: None)
    with pytest.raises(AttributeError):
        Summarizer(Settings())


if __name__ == "__main__":
    pytest.main()
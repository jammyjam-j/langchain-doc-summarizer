import os
from typing import Optional

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from pydantic import ValidationError

from app.config import settings


class Summarizer:
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.2):
        self.model_name = model_name
        self.temperature = temperature
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY") or settings.openai_api_key,
        )

    def summarize(self, document: str, max_tokens: Optional[int] = 200) -> str:
        if not isinstance(document, str):
            raise TypeError("document must be a string")
        if len(document.strip()) == 0:
            raise ValueError("document cannot be empty")

        prompt = (
            f"Summarize the following document in no more than {max_tokens} tokens:\n\n{document}"
        )

        try:
            response = self.llm([HumanMessage(content=prompt)])
        except Exception as exc:
            raise RuntimeError(f"LLM request failed: {exc}") from exc

        if not hasattr(response, "content") or not isinstance(response.content, str):
            raise RuntimeError("Invalid LLM response format")

        summary = response.content.strip()
        if len(summary.split()) > max_tokens:
            words = summary.split()[:max_tokens]
            summary = " ".join(words)
        return summary

    @classmethod
    def from_config(cls, config: dict) -> "Summarizer":
        try:
            model_name = config.get("model_name", "gpt-4o-mini")
            temperature = float(config.get("temperature", 0.2))
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"Invalid summarizer configuration: {exc}") from exc
        return cls(model_name=model_name, temperature=temperature)

    def __call__(self, document: str, max_tokens: Optional[int] = 200) -> str:
        return self.summarize(document, max_tokens=max_tokens)
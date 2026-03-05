from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class Document(BaseModel):
    id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    source_url: Optional[str] = Field(None, regex=r'^https?://')
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator("content")
    def strip_content(cls, v: str) -> str:
        return v.strip()


class SummarizationInput(BaseModel):
    document_id: int = Field(..., gt=0)
    summary_length: Optional[int] = Field(None, ge=10, le=500)


class SummaryChunk(BaseModel):
    chunk_index: int = Field(..., ge=0)
    text: str = Field(..., min_length=1)


class SummarizationResult(BaseModel):
    document_id: int
    summary_text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    chunks: List[SummaryChunk] = Field(default_factory=list)

    @validator("summary_text")
    def strip_summary(cls, v: str) -> str:
        return v.strip()

    @validator("chunks", each_item=True)
    def validate_chunks(cls, v: SummaryChunk) -> SummaryChunk:
        if not isinstance(v, SummaryChunk):
            raise TypeError("Each chunk must be a SummaryChunk instance")
        return v
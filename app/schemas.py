from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Optional
import datetime

class DocumentMetadata(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    @validator('created_at', 'updated_at', pre=True, always=True)
    def parse_datetime(cls, value):
        if isinstance(value, str):
            return datetime.datetime.fromisoformat(value)
        return value

class DocumentIngestRequest(BaseModel):
    source_url: HttpUrl
    metadata: Optional[DocumentMetadata] = None
    tags: List[str] = Field(default_factory=list)

    @validator('tags', each_item=True)
    def tag_non_empty(cls, v):
        if not v.strip():
            raise ValueError('Tag cannot be empty')
        return v

class DocumentIngestResponse(BaseModel):
    document_id: str
    source_url: HttpUrl
    status: str = Field(..., regex=r'^(ingested|failed)$')
    metadata: Optional[DocumentMetadata] = None
    tags: List[str]

class SummarizeRequest(BaseModel):
    document_id: str
    summary_length: int = Field(200, ge=50, le=1000)
    language: str = Field('en', regex=r'^[a-z]{2}$')

class SummarizeResponse(BaseModel):
    document_id: str
    summary: str
    generated_at: datetime.datetime

    @validator('generated_at', pre=True, always=True)
    def set_generated_at(cls, value):
        if isinstance(value, str):
            return datetime.datetime.fromisoformat(value)
        return value

class ErrorResponse(BaseModel):
    detail: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
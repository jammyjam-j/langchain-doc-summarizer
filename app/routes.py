from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import List
from uuid import UUID

from app.services.document_processor import DocumentProcessor
from app.services.summarizer import Summarizer
from app.models import Document
from app.schemas import DocumentCreateResponse, SummaryResponse
from app.serializers import DocumentSerializer, SummarySerializer
from sqlalchemy.orm import Session

router = APIRouter()


def get_db():
    from app.main import get_session  # lazily imported to avoid circular dependency
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.post("/documents", response_model=DocumentCreateResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(
    file: UploadFile = File(...),
    processor: DocumentProcessor = Depends(),
    db: Session = Depends(get_db),
):
    try:
        content = await file.read()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Failed to read uploaded file") from exc

    document_id = await processor.process_file(content, file.filename)
    if not document_id:
        raise HTTPException(status_code=500, detail="Document processing failed")

    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found after ingestion")

    return DocumentSerializer.from_orm(document)


@router.get("/summaries/{doc_id}", response_model=SummaryResponse)
async def get_summary(
    doc_id: UUID,
    summarizer: Summarizer = Depends(),
    db: Session = Depends(get_db),
):
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    summary_text = await summarizer.summarize(document.content)
    if summary_text is None:
        raise HTTPException(status_code=500, detail="Summarization failed")

    return SummarySerializer(content=summary_text)


@router.get("/documents", response_model=List[DocumentCreateResponse])
async def list_documents(
    db: Session = Depends(get_db),
):
    documents = db.query(Document).all()
    return [DocumentSerializer.from_orm(doc) for doc in documents]
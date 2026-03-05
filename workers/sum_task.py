import os
from celery import shared_task
from app.services.summarizer import Summarizer
from app.utils.file_handler import FileHandler
from app.models import DocumentSummary
from django.conf import settings

@shared_task(bind=True, name="summarize_document")
def summarize_document(self, document_id: int) -> dict:
    try:
        summary_obj = DocumentSummary.objects.get(id=document_id)
    except DocumentSummary.DoesNotExist:
        raise ValueError(f"Document with id {document_id} not found")

    file_path = os.path.join(settings.MEDIA_ROOT, summary_obj.file_name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist")

    try:
        content = FileHandler.read_text(file_path)
    except Exception as exc:
        raise RuntimeError(f"Failed to read file: {exc}") from exc

    summarizer = Summarizer()
    try:
        summary_text = summarizer.summarize(content)
    except Exception as exc:
        raise RuntimeError(f"Summarization failed: {exc}") from exc

    summary_obj.summary_text = summary_text
    summary_obj.status = "completed"
    summary_obj.save(update_fields=["summary_text", "status"])

    return {"id": document_id, "status": summary_obj.status, "summary": summary_text}
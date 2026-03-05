import os
from celery import Celery, Task
from celery.exceptions import Retry
from app.utils.logger import get_logger
from workers.sum_task import summarize_document

logger = get_logger(__name__)

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    __name__,
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "cleanup-task-every-24-hours": {
            "task": "tasks.cleanup_task",
            "schedule": 86400.0,
        },
    },
)

class BaseTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(
            f"Task {self.name} failed: {exc}. "
            f"Task ID: {task_id}, Args: {args}, Kwargs: {kwargs}"
        )

@celery_app.task(bind=True, base=BaseTask)
def run_summarization(self, document_path: str):
    try:
        result = summarize_document(document_path)
        return {"status": "success", "summary": result}
    except Exception as exc:
        logger.exception(f"Summarization failed for {document_path}")
        raise self.retry(exc=exc, countdown=30, max_retries=3)

@celery_app.task(bind=True, base=BaseTask)
def cleanup_task(self):
    try:
        from pathlib import Path
        cache_dir = Path(os.getenv("CACHE_DIR", "/tmp/summaries"))
        for file in cache_dir.glob("*"):
            if file.is_file():
                file.unlink()
        return {"status": "cleaned"}
    except Exception as exc:
        logger.exception("Cleanup task failed")
        raise Retry(exc=exc, countdown=60)

if __name__ == "__main__":
    celery_app.worker_main()
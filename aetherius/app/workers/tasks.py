from datetime import datetime, timezone

from celery.utils.log import get_task_logger

from app.db.session import SessionLocal
from app.models.entities import Clients
from app.services.drafting.service import draft_daily_brief
from app.services.ingestion.service import ingest_observation
from app.workers.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(bind=True, max_retries=3, name="app.workers.tasks.ingest_dummy")
def ingest_dummy(self):
    try:
        db = SessionLocal()
        try:
            row = ingest_observation(
                db=db,
                source_type="system",
                source_name="dummy",
                raw_text="dummy scheduled observation",
                observed_at=datetime.now(timezone.utc),
                source_confidence=1.0,
            )
            logger.info("ingest_dummy complete", extra={"created": bool(row), "task_id": self.request.id})
        finally:
            db.close()
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, name="app.workers.tasks.briefing_daily_sweep")
def briefing_daily_sweep(self):
    db = SessionLocal()
    try:
        for client in db.query(Clients).all():
            draft_daily_brief(db, str(client.id))
    except Exception as exc:
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, name="app.workers.tasks.briefing_weekly_sweep")
def briefing_weekly_sweep(self):
    logger.info("weekly sweep triggered", extra={"task_id": self.request.id})


@celery_app.task(bind=True, max_retries=3, name="app.workers.tasks.delivery_retry_failed")
def delivery_retry_failed(self):
    logger.info("delivery retry sweep triggered", extra={"task_id": self.request.id})


@celery_app.task(bind=True, name="app.workers.tasks.observability_health_alerts")
def observability_health_alerts(self):
    logger.info("health alerts sweep triggered", extra={"task_id": self.request.id})


@celery_app.task(bind=True, name="app.workers.tasks.dead_letter_requeue")
def dead_letter_requeue(self):
    logger.info("dead-letter requeue sweep triggered", extra={"task_id": self.request.id})


@celery_app.task(bind=True, name="app.workers.tasks.retention_archive_cleanup")
def retention_archive_cleanup(self, days: int = 180):
    logger.info("retention cleanup executed", extra={"days": days, "task_id": self.request.id})

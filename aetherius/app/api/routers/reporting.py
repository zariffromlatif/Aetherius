from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_client_scope, require_operator
from app.models.entities import ClientFeedback
from app.services.reporting.service import build_pilot_report, build_weekly_summary

router = APIRouter(prefix="/reporting", tags=["reporting"], dependencies=[Depends(require_operator)])


class FeedbackCreate(BaseModel):
    client_id: str
    briefing_run_id: str | None = None
    feedback_type: str
    feedback_text: str | None = None
    recorded_by: str | None = "operator"


@router.get("/weekly/{client_id}")
def weekly_summary_endpoint(client_id: str, db: Session = Depends(get_db)):
    return build_weekly_summary(db, client_id)


@router.get("/pilot/{client_id}")
def pilot_report_endpoint(client_id: str, db: Session = Depends(get_db)):
    return build_pilot_report(db, client_id)


@router.post("/feedback")
def add_feedback_endpoint(payload: FeedbackCreate, db: Session = Depends(get_db)):
    allowed = {"useful", "noisy", "too_late", "strong_flag", "generic"}
    if payload.feedback_type not in allowed:
        payload.feedback_type = "generic"
    row = ClientFeedback(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/feedback/export/{client_id}")
def export_feedback_endpoint(client_id: str, _claims: dict = Depends(require_client_scope), db: Session = Depends(get_db)):
    rows = db.query(ClientFeedback).filter(ClientFeedback.client_id == client_id).order_by(ClientFeedback.created_at.desc()).all()
    return [
        {
            "briefing_run_id": str(r.briefing_run_id) if r.briefing_run_id else None,
            "feedback_type": r.feedback_type,
            "feedback_text": r.feedback_text,
            "recorded_by": r.recorded_by,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]

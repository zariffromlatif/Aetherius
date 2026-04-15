from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.entities import BriefingRuns, ClientFeedback, RiskSignals


def build_weekly_summary(db: Session, client_id: str) -> dict:
    sent_count = db.query(func.count(BriefingRuns.id)).filter(
        BriefingRuns.client_id == client_id, BriefingRuns.run_type == "daily_brief", BriefingRuns.status == "sent"
    ).scalar()
    open_signals = db.query(func.count(RiskSignals.id)).filter(RiskSignals.client_id == client_id, RiskSignals.status == "open").scalar()
    return {"client_id": client_id, "sent_daily_briefs": sent_count or 0, "open_signals": open_signals or 0}


def build_pilot_report(db: Session, client_id: str) -> dict:
    weekly = build_weekly_summary(db, client_id)
    feedback_count = db.query(func.count(ClientFeedback.id)).filter(ClientFeedback.client_id == client_id).scalar()
    return {
        "pilot_scope": "watchlist surveillance pilot",
        "outputs_delivered": weekly["sent_daily_briefs"],
        "open_signal_count": weekly["open_signals"],
        "feedback_entries": feedback_count or 0,
    }

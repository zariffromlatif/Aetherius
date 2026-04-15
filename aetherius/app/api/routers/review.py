from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_operator
from app.models.entities import BriefingItems, BriefingRuns
from app.services.drafting.service import draft_daily_brief, draft_urgent_alerts
from app.services.review.service import set_review_action

router = APIRouter(prefix="/review", tags=["review"], dependencies=[Depends(require_operator)])


class ReviewActionPayload(BaseModel):
    action_type: str
    operator_user_id: str | None = None
    reason: str | None = None
    before_payload: dict | None = None
    after_payload: dict | None = None


@router.post("/drafts/daily/{client_id}")
def draft_daily_brief_endpoint(client_id: str, db: Session = Depends(get_db)):
    return draft_daily_brief(db, client_id)


@router.post("/drafts/urgent/{client_id}")
def draft_urgent_alerts_endpoint(client_id: str, threshold: float = 0.75, db: Session = Depends(get_db)):
    return draft_urgent_alerts(db, client_id, threshold)


@router.get("/queue")
def review_queue_endpoint(db: Session = Depends(get_db)):
    return (
        db.query(BriefingRuns)
        .filter(BriefingRuns.status.in_(["draft", "pending_review", "approved"]))
        .order_by(BriefingRuns.created_at.desc())
        .all()
    )


@router.get("/briefings/{briefing_run_id}")
def view_briefing_endpoint(briefing_run_id: str, db: Session = Depends(get_db)):
    run = db.query(BriefingRuns).filter(BriefingRuns.id == briefing_run_id).one()
    items = (
        db.query(BriefingItems)
        .filter(BriefingItems.briefing_run_id == briefing_run_id)
        .order_by(BriefingItems.display_order.asc())
        .all()
    )
    return {"run": run, "items": items}


@router.post("/briefings/{briefing_run_id}/action")
def apply_review_action_endpoint(
    briefing_run_id: str,
    payload: ReviewActionPayload,
    claims: dict = Depends(require_operator),
    db: Session = Depends(get_db),
):
    data = payload.model_dump()
    data["operator_user_id"] = data.get("operator_user_id") or claims.get("sub")
    return set_review_action(db, briefing_run_id=briefing_run_id, **data)

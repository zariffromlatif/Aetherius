from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_operator
from app.models.entities import EvidenceLinks, RiskSignals
from app.services.signals.service import create_signal_from_evidence

router = APIRouter(prefix="/signals", tags=["signals"], dependencies=[Depends(require_operator)])


@router.post("/from-evidence/{evidence_id}")
def create_signal_from_evidence_endpoint(evidence_id: str, db: Session = Depends(get_db)):
    evidence = db.query(EvidenceLinks).filter(EvidenceLinks.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    signal = create_signal_from_evidence(db, evidence)
    return signal


@router.get("")
def list_signals_endpoint(client_id: str | None = None, status: str | None = None, db: Session = Depends(get_db)):
    q = db.query(RiskSignals)
    if client_id:
        q = q.filter(RiskSignals.client_id == client_id)
    if status:
        q = q.filter(RiskSignals.status == status)
    return q.order_by(RiskSignals.generated_at.desc()).limit(200).all()

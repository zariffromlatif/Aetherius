from datetime import datetime

from sqlalchemy.orm import Session

from app.models.entities import EvidenceLinks, RiskSignals, SignalEvidenceRefs, WatchlistItems, Watchlists
from app.services.scoring.service import (
    SIGNAL_TYPES,
    ScoreInput,
    compute_brief_priority_score,
    compute_risk_score,
    compute_urgency_score,
    confidence_label,
    severity_label,
)


def infer_signal_type(relationship_type: str | None) -> str:
    if relationship_type == "sector":
        return "sector_contagion"
    if relationship_type == "direct":
        return "earnings_risk"
    return "macro_spillover"


def create_signal_from_evidence(db: Session, evidence: EvidenceLinks) -> RiskSignals:
    item = db.query(WatchlistItems).filter(WatchlistItems.id == evidence.watchlist_item_id).one()
    watchlist = db.query(Watchlists).filter(Watchlists.id == item.watchlist_id).one()

    inpt = ScoreInput(
        source_confidence=0.7,
        freshness_score=0.8,
        directness_score=float(evidence.relevance_score),
        cross_confirmation_score=0.5,
        watchlist_priority_score={"low": 0.2, "normal": 0.5, "high": 0.8, "critical": 1.0}.get(item.priority_level, 0.5),
        event_severity_score=0.6,
        relationship_strength_score=float(evidence.relevance_score),
    )
    risk_score = compute_risk_score(inpt)
    urgency_score = compute_urgency_score(inpt, risk_score)
    priority_score = compute_brief_priority_score(inpt, risk_score, urgency_score)
    sig_type = infer_signal_type(evidence.relationship_type)
    if sig_type not in SIGNAL_TYPES:
        sig_type = "macro_spillover"
    sev = severity_label(risk_score)
    if sev in {"elevated", "high"} and not evidence.id:
        raise ValueError("Elevated/high signals require evidence references.")

    signal = RiskSignals(
        client_id=watchlist.client_id,
        watchlist_item_id=item.id,
        signal_type=sig_type,
        severity_level=sev,
        confidence_level=confidence_label(risk_score),
        risk_score=risk_score,
        urgency_score=urgency_score,
        brief_priority_score=priority_score,
        headline=f"{item.ticker}: potential downside signal detected",
        why_it_matters=evidence.evidence_summary or "Mapped watchlist evidence indicates potential margin pressure.",
        pathway="Observation -> mapping -> score -> prioritization.",
        watch_next="Monitor follow-through in guidance, demand commentary, and spread behavior.",
        invalidation_trigger="Contradictory high-confidence observations within freshness window.",
        status="open",
        generated_at=datetime.utcnow(),
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)

    ref = SignalEvidenceRefs(risk_signal_id=signal.id, evidence_link_id=evidence.id, rank_order=1)
    db.add(ref)
    db.commit()
    return signal

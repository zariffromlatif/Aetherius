from app.services.scoring.service import (
    ScoreInput,
    compute_brief_priority_score,
    compute_risk_score,
    compute_urgency_score,
    severity_label,
)


def test_scoring_bounds() -> None:
    inp = ScoreInput(
        source_confidence=0.9,
        freshness_score=0.8,
        directness_score=0.8,
        cross_confirmation_score=0.7,
        watchlist_priority_score=1.0,
        event_severity_score=0.8,
        relationship_strength_score=0.6,
    )
    risk = compute_risk_score(inp)
    urgency = compute_urgency_score(inp, risk)
    priority = compute_brief_priority_score(inp, risk, urgency)
    assert 0.0 <= risk <= 1.0
    assert 0.0 <= urgency <= 1.0
    assert 0.0 <= priority <= 1.0


def test_severity_ranges() -> None:
    assert severity_label(0.2) == "low"
    assert severity_label(0.5) == "moderate"
    assert severity_label(0.7) == "elevated"
    assert severity_label(0.9) == "high"


def test_scoring_is_deterministic() -> None:
    inp = ScoreInput(
        source_confidence=0.61,
        freshness_score=0.82,
        directness_score=0.57,
        cross_confirmation_score=0.43,
        watchlist_priority_score=0.8,
        event_severity_score=0.66,
        relationship_strength_score=0.73,
    )
    a = compute_risk_score(inp)
    b = compute_risk_score(inp)
    assert a == b

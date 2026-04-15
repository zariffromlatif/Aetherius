from dataclasses import dataclass


SIGNAL_TYPES = {
    "earnings_risk",
    "guidance_risk",
    "valuation_compression",
    "macro_spillover",
    "regulatory_risk",
    "supplier_readthrough",
    "customer_readthrough",
    "liquidity_or_refinancing_risk",
    "demand_softness",
    "narrative_break",
    "sector_contagion",
    "sentiment_deterioration",
    "balance_sheet_stress",
    "policy_shock",
    "commodity_input_risk",
}


@dataclass
class ScoreInput:
    source_confidence: float
    freshness_score: float
    directness_score: float
    cross_confirmation_score: float
    watchlist_priority_score: float
    event_severity_score: float
    relationship_strength_score: float
    alert_mode_multiplier: float = 1.0
    novelty_score: float = 0.5
    affected_names_score: float = 0.5
    high_priority_boost: float = 0.0
    time_sensitivity: float = 0.5
    is_new_signal: float = 0.5
    event_window_proximity: float = 0.5
    client_threshold: float = 0.5


def clamp(v: float) -> float:
    return max(0.0, min(1.0, v))


def compute_risk_score(v: ScoreInput) -> float:
    base = (
        0.20 * v.source_confidence
        + 0.15 * v.freshness_score
        + 0.20 * v.directness_score
        + 0.15 * v.cross_confirmation_score
        + 0.10 * v.watchlist_priority_score
        + 0.10 * v.event_severity_score
        + 0.10 * v.relationship_strength_score
    )
    return clamp(base * v.alert_mode_multiplier)


def compute_urgency_score(v: ScoreInput, risk_score: float) -> float:
    urgency = (
        0.30 * v.time_sensitivity
        + 0.25 * v.event_severity_score
        + 0.15 * (1.0 - v.client_threshold)
        + 0.15 * v.is_new_signal
        + 0.15 * v.event_window_proximity
    )
    return clamp((urgency + risk_score) / 2.0)


def compute_brief_priority_score(v: ScoreInput, risk_score: float, urgency_score: float) -> float:
    priority = (
        0.40 * risk_score
        + 0.30 * urgency_score
        + 0.15 * v.novelty_score
        + 0.10 * v.affected_names_score
        + 0.05 * (v.high_priority_boost + v.watchlist_priority_score)
    )
    return clamp(priority)


def severity_label(score: float) -> str:
    if score <= 0.35:
        return "low"
    if score <= 0.55:
        return "moderate"
    if score <= 0.75:
        return "elevated"
    return "high"


def confidence_label(score: float) -> str:
    if score < 0.4:
        return "low"
    if score < 0.75:
        return "medium"
    return "high"

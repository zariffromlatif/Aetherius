from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class ForageChunk:
    source_url: str
    title: str
    content: str
    entropy_score: float
    observed_at: datetime


@dataclass(slots=True)
class ForageResult:
    run_id: str
    started_at: datetime
    completed_at: datetime
    chunks: list[ForageChunk] = field(default_factory=list)
    dropped_chunks: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class GraphNode:
    node_id: str
    label: str
    node_type: str
    attributes: dict[str, float | str] = field(default_factory=dict)


@dataclass(slots=True)
class GraphEdge:
    source_id: str
    target_id: str
    relationship: str
    weight: float


@dataclass(slots=True)
class GraphState:
    state_id: str
    generated_at: datetime
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    summary: str = ""
    metadata: dict[str, str | int | float] = field(default_factory=dict)


@dataclass(slots=True)
class Shock:
    shock_id: str
    name: str
    description: str
    magnitude: float


@dataclass(slots=True)
class ScenarioPath:
    name: str
    narrative: str
    expected_margin_delta_bps: float


@dataclass(slots=True)
class ShockResult:
    state_id: str
    shock: Shock
    confidence: float
    risk_score: float
    urgency_score: float
    pathways: list[ScenarioPath] = field(default_factory=list)
    invalidation_markers: list[str] = field(default_factory=list)
    cache_hit: bool = False
    cache_key: str = ""
    token_spend_estimate: int = 0
    provider_total_tokens: int = 0
    provider_error: str = ""


@dataclass(slots=True)
class RiskDecisionLog:
    run_id: str
    what_changed: str
    why_it_matters: str
    what_happens_next: list[ScenarioPath]
    considered_actions: list[str]
    invalidation_markers: list[str]
    evidence_refs: list[str] = field(default_factory=list)

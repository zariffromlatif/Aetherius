from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import os
import sys
from uuid import uuid4
from typing import Any

from .contracts import (
    ForageResult,
    GraphEdge,
    GraphNode,
    GraphState,
    ScenarioPath,
    Shock,
    ShockResult,
)
from .optimizer import (
    build_cache_key,
    deserialize_pathways,
    estimate_token_spend,
    get_cached_result,
    serialize_pathways,
    set_cached_result,
)
from .model_adapter import TTCProviderError, run_ttc_simulation

SHOCK_LIBRARY: tuple[Shock, ...] = (
    Shock("shock-rate-50", "Unexpected Rate Hike", "Policy rate rises 50 bps", 0.50),
    Shock("shock-supply", "Supply Chain Fracture", "Lead times expand and freight surges", 0.70),
    Shock("shock-liquidity", "Liquidity Squeeze", "Credit spreads widen abruptly", 0.60),
)


def construct_state(
    forage_result: ForageResult,
    client_id: str | None = None,
    window_start: datetime | None = None,
    window_end: datetime | None = None,
) -> GraphState:
    """Construct graph state using DB watchlist context when available."""
    db_nodes, db_edges, snapshot = _load_watchlist_graph_snapshot(
        client_id=client_id,
        window_start=window_start,
        window_end=window_end,
    )

    nodes: list[GraphNode] = [
        GraphNode("node-rates", "Rates", "macro", {"stress": 0.55}),
        GraphNode("node-input-costs", "Input Costs", "factor", {"stress": 0.62}),
        GraphNode("node-consumer-saas", "Consumer SaaS", "sector", {"margin_buffer": 0.40}),
    ]
    edges: list[GraphEdge] = [
        GraphEdge("node-rates", "node-input-costs", "financing_pressure", 0.72),
        GraphEdge("node-input-costs", "node-consumer-saas", "cost_readthrough", 0.78),
    ]
    if db_nodes:
        nodes.extend(db_nodes)
    if db_edges:
        edges.extend(db_edges)
    summary = (
        f"Built from {len(forage_result.chunks)} high-entropy chunks; "
        f"watchlist_snapshot={snapshot['summary']}."
    )
    return GraphState(
        state_id=f"state-{uuid4()}",
        generated_at=datetime.now(timezone.utc),
        nodes=nodes,
        edges=edges,
        summary=summary,
        metadata={
            "client_id": client_id or "all",
            "window_start": window_start.isoformat() if window_start else "",
            "window_end": window_end.isoformat() if window_end else "",
            "watchlist_items": int(snapshot["items"]),
            "relationships": int(snapshot["relationships"]),
            "evidence_links": int(snapshot["evidence"]),
            "observations": int(snapshot["observations"]),
        },
    )


def simulate_shock(state: GraphState, shock: Shock, model_name: str = "gpt-4o-mini") -> ShockResult:
    cache_key = build_cache_key(state, shock, model_name=model_name)
    cached = get_cached_result(cache_key)
    if cached:
        return ShockResult(
            state_id=state.state_id,
            shock=shock,
            confidence=float(cached["confidence"]),
            risk_score=float(cached["risk_score"]),
            urgency_score=float(cached["urgency_score"]),
            pathways=deserialize_pathways(cached["pathways"]),
            invalidation_markers=list(cached["invalidation_markers"]),
            cache_hit=True,
            cache_key=cache_key,
            token_spend_estimate=estimate_token_spend(state, shock, cache_hit=True),
            provider_total_tokens=int(cached.get("provider_total_tokens", 0)),
            provider_error=str(cached.get("provider_error", "")),
        )

    use_ttc = os.getenv("AETHERIUS_ENABLE_TTC", "true").lower() in {"1", "true", "yes"}
    provider_tokens = 0
    provider_error = ""
    if use_ttc:
        try:
            model_payload = run_ttc_simulation(state, shock, model_name=model_name)
            pathways = [
                ScenarioPath(
                    name=row["name"],
                    narrative=row["narrative"],
                    expected_margin_delta_bps=float(row["expected_margin_delta_bps"]),
                )
                for row in model_payload["pathways"]
            ]
            markers = [str(x) for x in model_payload["invalidation_markers"]]
            base_risk = _normalize_score(float(model_payload["risk_score"]))
            urgency = _normalize_score(float(model_payload["urgency_score"]))
            confidence = _normalize_score(float(model_payload["confidence"]))
            provider_tokens = int(model_payload.get("_provider_usage_total_tokens", 0))
        except TTCProviderError as exc:
            # Safe fallback to deterministic simulation if provider path fails.
            provider_tokens = max(provider_tokens, int(getattr(exc, "provider_tokens", 0)))
            provider_error = f"ttc_provider_failed:{exc}"
            base_risk, urgency, confidence, pathways, markers = _fallback_simulation(shock)
        except Exception as exc:
            provider_error = f"ttc_provider_failed:{exc}"
            base_risk, urgency, confidence, pathways, markers = _fallback_simulation(shock)
    else:
        provider_error = "ttc_disabled"
        base_risk, urgency, confidence, pathways, markers = _fallback_simulation(shock)

    result = ShockResult(
        state_id=state.state_id,
        shock=shock,
        confidence=confidence,
        risk_score=base_risk,
        urgency_score=urgency,
        pathways=pathways,
        invalidation_markers=markers,
        cache_hit=False,
        cache_key=cache_key,
        token_spend_estimate=estimate_token_spend(state, shock, cache_hit=False),
        provider_total_tokens=provider_tokens,
        provider_error=provider_error,
    )
    set_cached_result(
        cache_key,
        {
            "confidence": result.confidence,
            "risk_score": result.risk_score,
            "urgency_score": result.urgency_score,
            "pathways": serialize_pathways(result.pathways),
            "invalidation_markers": result.invalidation_markers,
            "provider_total_tokens": result.provider_total_tokens,
            "provider_error": result.provider_error,
        },
    )
    return result


def run_shock_suite(state: GraphState, model_name: str = "gpt-4o-mini") -> list[ShockResult]:
    return [simulate_shock(state, shock, model_name=model_name) for shock in SHOCK_LIBRARY]


def _fallback_simulation(
    shock: Shock,
) -> tuple[float, float, float, list[ScenarioPath], list[str]]:
    base_risk = min(1.0, 0.45 + shock.magnitude * 0.40)
    urgency = min(1.0, 0.40 + shock.magnitude * 0.50)
    confidence = 0.68
    pathways = [
        ScenarioPath("Base", "Moderate margin compression with selective de-rating.", -45.0 * shock.magnitude),
        ScenarioPath("Bear", "Funding and cost pressure cascade through exposed names.", -95.0 * shock.magnitude),
        ScenarioPath("Bull", "Faster pass-through and resilient demand offset shock.", -20.0 * shock.magnitude),
    ]
    markers = [
        "Credit spreads normalize within 5 trading days",
        "Input-cost indices reverse week-over-week",
        "Management commentary confirms pricing power retention",
    ]
    return base_risk, urgency, confidence, pathways, markers


def _normalize_score(value: float) -> float:
    """Normalize provider scores into [0, 1].

    Some model responses return percentile-style values (0-100) instead of
    normalized probabilities (0-1). This keeps downstream thresholds stable.
    """
    if value > 1.0:
        value = value / 100.0
    return max(0.0, min(1.0, value))


def _load_watchlist_graph_snapshot(
    client_id: str | None = None,
    window_start: datetime | None = None,
    window_end: datetime | None = None,
) -> tuple[list[GraphNode], list[GraphEdge], dict[str, Any]]:
    """Load watchlist/evidence context from existing app DB models."""
    app_root = Path(__file__).resolve().parents[1] / "aetherius"
    if str(app_root) not in sys.path:
        sys.path.append(str(app_root))

    try:
        from app.db.session import SessionLocal  # type: ignore
        from app.models.entities import (  # type: ignore
            EntityRelationships,
            EvidenceLinks,
            SourceObservations,
            WatchlistItems,
        )
    except Exception:
        return [], [], {"summary": "db-unavailable", "items": 0, "relationships": 0, "evidence": 0, "observations": 0}

    db = SessionLocal()
    try:
        from app.models.entities import Watchlists  # type: ignore

        items_query = db.query(WatchlistItems).join(Watchlists, Watchlists.id == WatchlistItems.watchlist_id).filter(
            WatchlistItems.active.is_(True), Watchlists.active.is_(True)
        )
        if client_id:
            items_query = items_query.filter(Watchlists.client_id == client_id)
        items = items_query.limit(50).all()

        item_ids = [item.id for item in items]

        if item_ids:
            rels = (
                db.query(EntityRelationships)
                .filter(EntityRelationships.watchlist_item_id.in_(item_ids))
                .limit(100)
                .all()
            )
            evidence_count = db.query(EvidenceLinks).filter(EvidenceLinks.watchlist_item_id.in_(item_ids)).count()
        else:
            rels = []
            evidence_count = 0

        obs_query = db.query(SourceObservations)
        if window_start:
            obs_query = obs_query.filter(SourceObservations.observed_at >= window_start)
        if window_end:
            obs_query = obs_query.filter(SourceObservations.observed_at <= window_end)
        obs_count = obs_query.count()

        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        for item in items:
            item_node_id = f"wl-{item.id}"
            nodes.append(
                GraphNode(
                    node_id=item_node_id,
                    label=f"{item.ticker} ({item.company_name})",
                    node_type="watchlist_item",
                    attributes={
                        "priority_score": {"low": 0.2, "normal": 0.5, "high": 0.8, "critical": 1.0}.get(
                            item.priority_level, 0.5
                        ),
                        "active": "true",
                    },
                )
            )
        for rel in rels:
            source_id = f"wl-{rel.watchlist_item_id}"
            target_id = f"rel-{(rel.related_ticker or rel.related_entity_name).lower().replace(' ', '-')}"
            edges.append(
                GraphEdge(
                    source_id=source_id,
                    target_id=target_id,
                    relationship=f"{rel.relationship_type}_readthrough",
                    weight=float(rel.strength or 0.45),
                )
            )
        summary = f"items={len(items)}, relationships={len(rels)}, evidence={evidence_count}, observations={obs_count}"
        return nodes, edges, {
            "summary": summary,
            "items": len(items),
            "relationships": len(rels),
            "evidence": evidence_count,
            "observations": obs_count,
        }
    except Exception:
        return [], [], {"summary": "db-query-failed", "items": 0, "relationships": 0, "evidence": 0, "observations": 0}
    finally:
        db.close()

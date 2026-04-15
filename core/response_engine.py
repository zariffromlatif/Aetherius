from __future__ import annotations

from .contracts import RiskDecisionLog, ScenarioPath, ShockResult


def _render_pathways(pathways: list[ScenarioPath]) -> str:
    lines = []
    for path in pathways:
        lines.append(
            f"- **{path.name}**: {path.narrative} "
            f"(expected margin delta: {path.expected_margin_delta_bps:.1f} bps)"
        )
    return "\n".join(lines)


def build_risk_decision_log(run_id: str, result: ShockResult, evidence_refs: list[str]) -> RiskDecisionLog:
    actions = [
        "Review hedge overlays for names with refinancing exposure.",
        "Re-rank watchlist names with weak pricing power.",
        "Escalate high-urgency names to same-day operator review.",
    ]
    return RiskDecisionLog(
        run_id=run_id,
        what_changed=f"Shock applied: {result.shock.name} ({result.shock.description}).",
        why_it_matters=(
            "Direct pressure on financing/input costs increases second-order risk "
            "for margin-sensitive names."
        ),
        what_happens_next=result.pathways,
        considered_actions=actions,
        invalidation_markers=result.invalidation_markers,
        evidence_refs=evidence_refs,
    )


def to_markdown(log: RiskDecisionLog) -> str:
    section_c = _render_pathways(log.what_happens_next)
    actions = "\n".join(f"- {a}" for a in log.considered_actions)
    invalidation = "\n".join(f"- {m}" for m in log.invalidation_markers)
    evidence = "\n".join(f"- {e}" for e in log.evidence_refs) if log.evidence_refs else "- No explicit refs attached"

    return f"""# Aetherius Risk Decision Log

Run ID: `{log.run_id}`

## A. What Changed
{log.what_changed}

## B. Why It Matters
{log.why_it_matters}

## C. What Happens Next
{section_c}

## D. Considered Actions
{actions}

## E. Invalidation Markers
{invalidation}

## Evidence References
{evidence}
"""

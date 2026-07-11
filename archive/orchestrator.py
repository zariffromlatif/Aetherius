from __future__ import annotations

import asyncio
import json
import os
import smtplib
import sys
import time
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from pathlib import Path
from uuid import uuid4

from core.causal_brain import run_shock_suite, construct_state
from core.response_engine import build_risk_decision_log, to_markdown
from core.sensory_forager import forage

RUN_INTERVAL_SECONDS = int(os.getenv("AETHERIUS_LOOP_SECONDS", "21600"))  # 6 hours
RISK_THRESHOLD = float(os.getenv("AETHERIUS_RISK_THRESHOLD", "0.70"))
MODE = os.getenv("AETHERIUS_MODE", "pilot_safe")
MODEL_NAME = os.getenv("AETHERIUS_MODEL_NAME", "gpt-4o-mini")
RECIPIENT = os.getenv("AETHERIUS_RECIPIENT", "")
SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@aetherius.local")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "false").lower() in {"1", "true", "yes"}
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
LOG_PATH = Path("aetherius_system.log")
OUTPUT_DIR = Path("simulations") / "generated_logs"
CLIENT_ID = os.getenv("AETHERIUS_CLIENT_ID", "").strip() or None
WINDOW_HOURS = int(os.getenv("AETHERIUS_WINDOW_HOURS", "6"))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log(event: str, payload: dict) -> None:
    record = {"ts": _now_iso(), "event": event, **payload}
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def _send_email(subject: str, body: str, recipient: str) -> None:
    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = SMTP_FROM
    message["To"] = recipient
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        if SMTP_USE_TLS:
            server.starttls()
        if SMTP_USERNAME and SMTP_PASSWORD:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM, [recipient], message.as_string())


def _resolve_window() -> tuple[datetime, datetime]:
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=WINDOW_HOURS)
    return start, end


def _fetch_evidence_refs(
    client_id: str | None,
    window_start: datetime,
    window_end: datetime,
    limit: int = 5,
) -> list[str]:
    app_root = Path(__file__).resolve().parent / "aetherius"
    if str(app_root) not in sys.path:
        sys.path.append(str(app_root))
    try:
        from app.db.session import SessionLocal  # type: ignore
        from app.models.entities import EvidenceLinks, SourceObservations, WatchlistItems, Watchlists  # type: ignore
    except Exception:
        return ["forage:fallback-context"]

    db = SessionLocal()
    try:
        query = (
            db.query(EvidenceLinks.id, SourceObservations.id, WatchlistItems.ticker)
            .join(SourceObservations, SourceObservations.id == EvidenceLinks.observation_id)
            .join(WatchlistItems, WatchlistItems.id == EvidenceLinks.watchlist_item_id)
            .join(Watchlists, Watchlists.id == WatchlistItems.watchlist_id)
            .filter(SourceObservations.observed_at >= window_start, SourceObservations.observed_at <= window_end)
            .order_by(EvidenceLinks.created_at.desc())
        )
        if client_id:
            query = query.filter(Watchlists.client_id == client_id)
        rows = query.limit(limit).all()
        refs = [f"evidence:{ev_id}|obs:{obs_id}|ticker:{ticker}" for ev_id, obs_id, ticker in rows]
        return refs or ["forage:fallback-context"]
    except Exception:
        return ["forage:fallback-context"]
    finally:
        db.close()


async def _run_once() -> None:
    run_id = f"run-{uuid4()}"
    started_at = time.perf_counter()
    window_start, window_end = _resolve_window()
    _log(
        "run_started",
        {
            "run_id": run_id,
            "mode": MODE,
            "client_id": CLIENT_ID or "all",
            "window_start": window_start.isoformat(),
            "window_end": window_end.isoformat(),
        },
    )

    forage_result = forage()
    _log(
        "forage_completed",
        {
            "run_id": run_id,
            "chunks": len(forage_result.chunks),
            "dropped_chunks": forage_result.dropped_chunks,
        },
    )

    state = construct_state(
        forage_result,
        client_id=CLIENT_ID,
        window_start=window_start,
        window_end=window_end,
    )
    _log(
        "state_constructed",
        {
            "run_id": run_id,
            "state_id": state.state_id,
            "node_count": len(state.nodes),
            "edge_count": len(state.edges),
            "state_metadata": state.metadata,
        },
    )

    shock_results = run_shock_suite(state, model_name=MODEL_NAME)
    triggered = [result for result in shock_results if result.risk_score >= RISK_THRESHOLD]
    token_spend_estimate = sum(r.token_spend_estimate for r in shock_results)
    provider_total_tokens = sum(r.provider_total_tokens for r in shock_results)
    cache_hit_count = sum(1 for r in shock_results if r.cache_hit)
    cache_hit_ratio = round(cache_hit_count / max(len(shock_results), 1), 3)
    _log(
        "shock_suite_completed",
        {
            "run_id": run_id,
            "shock_count": len(shock_results),
            "triggered_count": len(triggered),
            "model_name": MODEL_NAME,
            "token_spend_estimate": token_spend_estimate,
            "provider_total_tokens": provider_total_tokens,
            "cache_hit_count": cache_hit_count,
            "cache_hit_ratio": cache_hit_ratio,
        },
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    evidence_refs = _fetch_evidence_refs(client_id=CLIENT_ID, window_start=window_start, window_end=window_end, limit=8)
    for result in triggered:
        decision_log = build_risk_decision_log(run_id=run_id, result=result, evidence_refs=evidence_refs)
        markdown = to_markdown(decision_log)
        output_path = OUTPUT_DIR / f"{run_id}-{result.shock.shock_id}.md"
        output_path.write_text(markdown, encoding="utf-8")
        _log(
            "risk_log_generated",
            {
                "run_id": run_id,
                "shock_id": result.shock.shock_id,
                "risk_score": round(result.risk_score, 4),
                "urgency_score": round(result.urgency_score, 4),
                "output_path": str(output_path),
                "evidence_ref_count": len(evidence_refs),
                "cache_hit": result.cache_hit,
                "cache_key": result.cache_key,
                "token_spend_estimate": result.token_spend_estimate,
                "provider_total_tokens": result.provider_total_tokens,
                "provider_error": result.provider_error,
            },
        )

        if MODE == "autonomous_research" and RECIPIENT:
            _send_email(
                subject=f"Aetherius Risk Decision Log [{result.shock.name}]",
                body=markdown,
                recipient=RECIPIENT,
            )
            _log("autonomous_delivery_sent", {"run_id": run_id, "recipient": RECIPIENT, "shock_id": result.shock.shock_id})
        else:
            _log(
                "pilot_safe_review_required",
                {"run_id": run_id, "shock_id": result.shock.shock_id, "reason": "autonomous send disabled"},
            )

    elapsed_ms = int((time.perf_counter() - started_at) * 1000)
    _log(
        "run_completed",
        {
            "run_id": run_id,
            "elapsed_ms": elapsed_ms,
            "token_spend_estimate": token_spend_estimate,
            "provider_total_tokens": provider_total_tokens,
            "cache_hit_ratio": cache_hit_ratio,
        },
    )


async def _run_loop() -> None:
    backoff_seconds = 10
    while True:
        try:
            await _run_once()
            backoff_seconds = 10
            await asyncio.sleep(RUN_INTERVAL_SECONDS)
        except Exception as exc:  # broad catch for daemon stability
            _log("run_failed", {"error": str(exc), "retry_in_seconds": backoff_seconds})
            await asyncio.sleep(backoff_seconds)
            backoff_seconds = min(backoff_seconds * 2, 300)


def main() -> None:
    asyncio.run(_run_loop())


if __name__ == "__main__":
    main()

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .contracts import GraphState, ScenarioPath, Shock

CACHE_FILE = Path(".aetherius_prompt_cache.json")
CACHE_TTL_HOURS = 24
CACHE_SCHEMA_VERSION = 2


def _load_cache() -> dict[str, Any]:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cache(cache: dict[str, Any]) -> None:
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def build_cache_key(state: GraphState, shock: Shock, model_name: str) -> str:
    static_prefix = json.dumps(
        {
            "cache_schema_version": CACHE_SCHEMA_VERSION,
            "model": model_name,
            "state_summary": state.summary,
            "state_metadata": state.metadata,
            "node_count": len(state.nodes),
            "edge_count": len(state.edges),
            "shock_id": shock.shock_id,
            "shock_magnitude": shock.magnitude,
        },
        sort_keys=True,
    )
    return hashlib.sha256(static_prefix.encode("utf-8")).hexdigest()


def get_cached_result(cache_key: str) -> dict[str, Any] | None:
    cache = _load_cache()
    payload = cache.get(cache_key)
    if not payload:
        return None
    try:
        created = datetime.fromisoformat(payload["created_at"])
    except Exception:
        return None
    if _now() - created > timedelta(hours=CACHE_TTL_HOURS):
        return None
    return payload.get("result")


def set_cached_result(cache_key: str, result_payload: dict[str, Any]) -> None:
    cache = _load_cache()
    cache[cache_key] = {
        "created_at": _now().isoformat(),
        "result": result_payload,
    }
    _save_cache(cache)


def estimate_token_spend(state: GraphState, shock: Shock, cache_hit: bool) -> int:
    base = 280 + len(state.nodes) * 3 + len(state.edges) * 2 + int(shock.magnitude * 100)
    if cache_hit:
        return max(60, int(base * 0.2))
    return base


def serialize_pathways(pathways: list[ScenarioPath]) -> list[dict[str, Any]]:
    return [asdict(path) for path in pathways]


def deserialize_pathways(payload: list[dict[str, Any]]) -> list[ScenarioPath]:
    return [ScenarioPath(**row) for row in payload]

from __future__ import annotations

import json
import os
from typing import Any

import httpx

from .contracts import GraphState, Shock


class TTCProviderError(RuntimeError):
    def __init__(self, message: str, provider_tokens: int = 0) -> None:
        super().__init__(message)
        self.provider_tokens = provider_tokens


def _extract_json_block(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[1]
        if stripped.endswith("```"):
            stripped = stripped[:-3]
    return json.loads(stripped)


def _build_messages(state: GraphState, shock: Shock) -> list[dict[str, str]]:
    system = (
        "You are Aetherius causal simulation core. "
        "Return strict JSON only with keys: confidence, risk_score, urgency_score, pathways, invalidation_markers. "
        "Pathways must contain Base, Bear, Bull with keys name, narrative, expected_margin_delta_bps."
    )
    payload = {
        "state_id": state.state_id,
        "state_summary": state.summary,
        "state_metadata": state.metadata,
        "node_count": len(state.nodes),
        "edge_count": len(state.edges),
        "shock": {
            "shock_id": shock.shock_id,
            "name": shock.name,
            "description": shock.description,
            "magnitude": shock.magnitude,
        },
        "task": "simulate next-state downside pathways and provide causal transmission summary",
    }
    user = json.dumps(payload, ensure_ascii=True)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _post_completion(
    url: str,
    headers: dict[str, str],
    model_name: str,
    messages: list[dict[str, str]],
    timeout: float,
) -> dict[str, Any]:
    body = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }
    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()


def _extract_usage_tokens(payload: dict[str, Any]) -> tuple[int, int, int]:
    usage = payload.get("usage", {}) or {}
    return (
        int(usage.get("total_tokens", 0) or 0),
        int(usage.get("prompt_tokens", 0) or 0),
        int(usage.get("completion_tokens", 0) or 0),
    )


def _validate_payload(parsed: dict[str, Any]) -> None:
    required = ("confidence", "risk_score", "urgency_score", "pathways", "invalidation_markers")
    for key in required:
        if key not in parsed:
            raise ValueError(f"missing required key: {key}")
    for key in ("confidence", "risk_score", "urgency_score"):
        value = parsed.get(key)
        if value is None:
            raise ValueError(f"{key} must not be null")
        float(value)
    pathways = parsed.get("pathways")
    if not isinstance(pathways, list) or len(pathways) < 3:
        raise ValueError("pathways must include at least Base/Bear/Bull entries")
    markers = parsed.get("invalidation_markers")
    if not isinstance(markers, list) or not markers:
        raise ValueError("invalidation_markers must be a non-empty list")


def _to_float(value: Any, default: float) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _normalize_pathways(pathways: Any, shock_magnitude: float) -> list[dict[str, Any]]:
    defaults = {
        "Base": {
            "name": "Base",
            "narrative": "Moderate margin compression with selective de-rating.",
            "expected_margin_delta_bps": -45.0 * shock_magnitude,
        },
        "Bear": {
            "name": "Bear",
            "narrative": "Funding and cost pressure cascade through exposed names.",
            "expected_margin_delta_bps": -95.0 * shock_magnitude,
        },
        "Bull": {
            "name": "Bull",
            "narrative": "Faster pass-through and resilient demand offset shock.",
            "expected_margin_delta_bps": -20.0 * shock_magnitude,
        },
    }
    mapped: dict[str, dict[str, Any]] = {}
    if isinstance(pathways, list):
        for row in pathways:
            if not isinstance(row, dict):
                continue
            name = str(row.get("name", "")).strip().title()
            if name not in {"Base", "Bear", "Bull"}:
                continue
            mapped[name] = {
                "name": name,
                "narrative": str(row.get("narrative", defaults[name]["narrative"])),
                "expected_margin_delta_bps": _to_float(
                    row.get("expected_margin_delta_bps"), defaults[name]["expected_margin_delta_bps"]
                ),
            }
    normalized = [mapped.get("Base", defaults["Base"]), mapped.get("Bear", defaults["Bear"]), mapped.get("Bull", defaults["Bull"])]
    return normalized


def _normalize_payload(parsed: dict[str, Any], shock_magnitude: float) -> dict[str, Any]:
    normalized = dict(parsed)
    normalized["confidence"] = _to_float(parsed.get("confidence"), 0.68)
    normalized["risk_score"] = _to_float(parsed.get("risk_score"), 0.65)
    normalized["urgency_score"] = _to_float(parsed.get("urgency_score"), 0.65)
    normalized["pathways"] = _normalize_pathways(parsed.get("pathways"), shock_magnitude)
    markers = parsed.get("invalidation_markers")
    if not isinstance(markers, list) or not markers:
        markers = [
            "Credit spreads normalize within 5 trading days",
            "Input-cost indices reverse week-over-week",
            "Management commentary confirms pricing power retention",
        ]
    normalized["invalidation_markers"] = [str(x) for x in markers]
    return normalized


def run_ttc_simulation(state: GraphState, shock: Shock, model_name: str) -> dict[str, Any]:
    """Run OpenAI-compatible chat completion call for causal simulation.

    Works with OpenAI-style providers by changing AETHERIUS_API_BASE_URL.
    """
    api_key = os.getenv("AETHERIUS_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("AETHERIUS_API_KEY is not set")

    base_url = os.getenv("AETHERIUS_API_BASE_URL", "https://api.openai.com/v1")
    timeout = float(os.getenv("AETHERIUS_API_TIMEOUT_SECONDS", "45"))
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    messages = _build_messages(state, shock)
    total_tokens_acc = 0
    prompt_tokens_acc = 0
    completion_tokens_acc = 0

    for attempt in (1, 2):
        try:
            payload = _post_completion(url, headers, model_name, messages, timeout)
            total_tokens, prompt_tokens, completion_tokens = _extract_usage_tokens(payload)
            total_tokens_acc += total_tokens
            prompt_tokens_acc += prompt_tokens
            completion_tokens_acc += completion_tokens

            content = payload["choices"][0]["message"]["content"]
            parsed = _extract_json_block(content)
            normalized = _normalize_payload(parsed, shock.magnitude)
            _validate_payload(normalized)
            normalized["_provider_usage_total_tokens"] = total_tokens_acc
            normalized["_provider_usage_prompt_tokens"] = prompt_tokens_acc
            normalized["_provider_usage_completion_tokens"] = completion_tokens_acc
            return normalized
        except Exception as exc:
            if attempt == 2:
                raise TTCProviderError(str(exc), provider_tokens=total_tokens_acc) from exc
            messages = messages + [
                {
                    "role": "user",
                    "content": (
                        "Retry and return strict JSON with non-null numeric confidence/risk_score/urgency_score, "
                        "exactly three pathways (Base, Bear, Bull), and non-empty invalidation_markers."
                    ),
                }
            ]

    raise TTCProviderError("unreachable provider retry flow", provider_tokens=total_tokens_acc)

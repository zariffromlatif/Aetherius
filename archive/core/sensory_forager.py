from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from .contracts import ForageChunk, ForageResult

TARGETS: tuple[tuple[str, str], ...] = (
    ("https://www.federalreserve.gov/newsevents.htm", "Federal Reserve Events"),
    ("https://www.cmegroup.com/markets/interest-rates.html", "Rates Dashboard"),
    ("https://www.bls.gov/", "US Macro Data"),
)


def semantic_entropy_score(text: str) -> float:
    """Simple placeholder score: favors dense, non-repetitive chunks."""
    if not text.strip():
        return 0.0
    words = [w for w in text.lower().split() if w.isalpha()]
    if not words:
        return 0.0
    unique_ratio = len(set(words)) / max(len(words), 1)
    length_bonus = min(len(words) / 400.0, 1.0)
    return max(0.0, min(1.0, 0.65 * unique_ratio + 0.35 * length_bonus))


async def _crawl_target(url: str) -> tuple[str, str]:
    """Attempt Crawl4AI extraction and return (content, error)."""
    try:
        from crawl4ai import AsyncWebCrawler  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency at runtime
        return "", f"crawl4ai import failed: {exc}"

    try:
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(url=url)
            content = (
                getattr(result, "fit_markdown", None)
                or getattr(result, "markdown", None)
                or getattr(result, "cleaned_html", None)
                or getattr(result, "html", None)
                or ""
            )
            if not isinstance(content, str):
                content = str(content)
            if not content.strip():
                return "", "crawl4ai returned empty content"
            return content, ""
    except Exception as exc:  # pragma: no cover - network/runtime variability
        return "", f"crawl4ai crawl failed: {exc}"


async def forage_async() -> ForageResult:
    """Forage target pages using Crawl4AI, with deterministic fallback.

    Targets are crawled concurrently. This is the async core; callers in a
    synchronous context should use ``forage()``.
    """
    started_at = datetime.now(timezone.utc)
    chunks: list[ForageChunk] = []
    dropped = 0
    errors: list[str] = []

    crawl_results = await asyncio.gather(*(_crawl_target(url) for url, _ in TARGETS))

    for (url, title), (content, error) in zip(TARGETS, crawl_results):
        if error:
            errors.append(f"{title}: {error}")
            content = (
                f"Source: {title}."
                " Yield curve steepening and refinancing spreads widened in pockets."
                " Supplier commentary implies potential cost pass-through lag."
            )
        score = semantic_entropy_score(content)
        if score < 0.35:
            dropped += 1
            continue
        chunks.append(
            ForageChunk(
                source_url=url,
                title=title,
                content=content,
                entropy_score=score,
                observed_at=datetime.now(timezone.utc),
            )
        )

    completed_at = datetime.now(timezone.utc)
    return ForageResult(
        run_id=f"forage-{uuid4()}",
        started_at=started_at,
        completed_at=completed_at,
        chunks=chunks,
        dropped_chunks=dropped,
        errors=errors,
    )


def forage() -> ForageResult:
    """Synchronous entry point for non-async callers.

    Must NOT be called from within a running event loop (it would raise
    ``RuntimeError``). Async callers should ``await forage_async()`` directly.
    """
    return asyncio.run(forage_async())

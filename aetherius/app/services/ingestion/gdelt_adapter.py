"""GDELT DOC 2.0 news ingestion adapter.

Queries the GDELT DOC 2.0 API for news articles mentioning a ticker or company
name in a given date window, and feeds them into the ingestion pipeline as
SourceObservations.

GDELT DOC 2.0 is free, requires no API key, and returns global news coverage
indexed from ~65,000 sources with 15-minute latency. Historical coverage back
to 2015 makes it the right primary-source archive for the SVB / Wirecard / FTX
backtests that anchor the detection track record.

Docs: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/

Rate limits are not published but empirically ~1-2 req/s is safe. The API caps
each response at 250 articles, so callers walking a wide window should page by
narrowing the timespan.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.models.entities import SourceObservations
from app.services.ingestion.service import ingest_observation

_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

# Sources that publish substantive financial/downside-risk reporting. GDELT
# indexes tens of thousands of domains including press-release wires, syndicated
# aggregators, and translation mirrors; a domain whitelist is the fastest way
# to drop that noise without needing a per-article classifier.
DOWNSIDE_DOMAINS: frozenset[str] = frozenset(
    {
        # Primary financial wires
        "reuters.com",
        "bloomberg.com",
        "wsj.com",
        "ft.com",
        "cnbc.com",
        "nytimes.com",
        "marketwatch.com",
        "barrons.com",
        "finance.yahoo.com",
        "news.yahoo.com",
        # Regulatory / ratings
        "sec.gov",
        "moodys.com",
        "spglobal.com",
        "fitchratings.com",
        "fdic.gov",
        "federalreserve.gov",
        # Sector / analysis (substantive coverage)
        "americanbanker.com",
        "axios.com",
        "businessinsider.com",
        "theinformation.com",
        "techcrunch.com",
        "streetinsider.com",
        "investors.com",
        "fool.com",
        "seekingalpha.com",
        "investing.com",
    }
)


def _headers() -> dict[str, str]:
    return {"User-Agent": "Aetherius Research zarif.latif.biz@gmail.com", "Accept": "application/json"}


def _fmt_gdelt_datetime(dt: datetime) -> str:
    """GDELT expects YYYYMMDDHHMMSS in UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y%m%d%H%M%S")


def build_query(company_name: str, aliases: list[str] | None = None) -> str:
    """Build a GDELT DOC query string.

    Uses a phrase-OR block for company name plus aliases. GDELT quoting rules:
    multi-word phrases must be double-quoted. Domain filtering is intentionally
    NOT done in the query — GDELT caps query length, and a 12-domain OR block
    plus a 3-alias phrase block trips it. Instead, filter domains in Python
    after the fetch (see ``fetch_articles`` ``domain_whitelist`` parameter).
    """
    names = [company_name] + list(aliases or [])
    phrases = " OR ".join(f'"{n}"' if " " in n else n for n in names if n)
    return f"({phrases})" if len(names) > 1 else phrases


def fetch_articles(
    company_name: str,
    window_start: datetime,
    window_end: datetime,
    aliases: list[str] | None = None,
    max_records: int = 250,
    client: httpx.Client | None = None,
    domain_whitelist: frozenset[str] | None = None,
) -> list[dict]:
    """Fetch article records from GDELT DOC 2.0 for a company in a time window.

    Returns article dicts, optionally filtered to a domain whitelist in Python
    after the network call (GDELT's own query length limit rules out doing this
    server-side for whitelists larger than a few domains).
    """
    params = {
        "query": build_query(company_name, aliases=aliases),
        "mode": "ArtList",
        "format": "json",
        "maxrecords": str(min(max_records, 250)),
        "startdatetime": _fmt_gdelt_datetime(window_start),
        "enddatetime": _fmt_gdelt_datetime(window_end),
        "sort": "DateAsc",
    }
    owns_client = client is None
    if owns_client:
        client = httpx.Client(timeout=30.0)
    try:
        # GDELT throttles hard on rapid successive calls (undocumented). Retry
        # with exponential backoff — the 5s / 15s / 45s ladder is empirically
        # enough for the corpus-builder flow that iterates over 6-10 targets.
        resp = None
        for delay in (0.0, 5.0, 15.0, 45.0):
            if delay:
                time.sleep(delay)
            resp = client.get(_DOC_URL, params=params, headers=_headers())
            if resp.status_code != 429:
                break
        assert resp is not None
        resp.raise_for_status()
        # GDELT returns text/plain on query errors ("Your query was too short
        # or too long."); guard against that before decoding JSON.
        content_type = resp.headers.get("content-type", "")
        if "json" not in content_type.lower():
            return []
        payload = resp.json()
    finally:
        if owns_client:
            client.close()
    articles = parse_articles(payload)
    if domain_whitelist:
        articles = [a for a in articles if (a.get("domain") or "").lower() in domain_whitelist]
    return articles


def parse_articles(payload: dict) -> list[dict]:
    """Parse a GDELT DOC 2.0 JSON payload into a flat list of article dicts.

    Pure function so it is unit-testable with a recorded sample.
    """
    return list(payload.get("articles", []) or [])


def _parse_gdelt_seendate(value: str) -> datetime:
    """GDELT ``seendate`` is ``YYYYMMDDTHHMMSSZ`` in UTC."""
    try:
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def _article_to_text(company_name: str, article: dict) -> str:
    """Compose the observation raw_text from a GDELT article record.

    ``company_name`` is retained only to prefix the source-provenance line —
    it is NOT injected into the text that entity_mapping runs against. That
    matters because a query for company X may return articles that mention X
    only in the body while the title is about Y; if we labeled the raw_text
    "News mention of X: ..." we would false-positive X on any adverse Y-story.
    """
    title = (article.get("title") or "").strip()
    domain = (article.get("domain") or "").strip()
    url = (article.get("url") or "").strip()
    seendate = (article.get("seendate") or "").strip()
    return f"{title} [Source: {domain}. Seen at {seendate}. URL: {url}]"


def ingest_articles_for_target(
    db: Session,
    company_name: str,
    window_start: datetime,
    window_end: datetime,
    aliases: list[str] | None = None,
    max_records: int = 250,
    domain_whitelist: frozenset[str] | None = None,
) -> list[SourceObservations]:
    """Fetch GDELT articles for a target in a window and ingest as observations.

    Dedupe key is the article URL so repeat runs are idempotent. Returns only
    newly-created observations.
    """
    articles = fetch_articles(
        company_name=company_name,
        window_start=window_start,
        window_end=window_end,
        aliases=aliases,
        max_records=max_records,
        domain_whitelist=domain_whitelist,
    )
    created: list[SourceObservations] = []
    for article in articles:
        url = (article.get("url") or "").strip()
        if not url:
            continue
        obs = ingest_observation(
            db=db,
            source_type="news",
            source_name=(article.get("domain") or "GDELT news"),
            raw_text=_article_to_text(company_name, article),
            observed_at=_parse_gdelt_seendate(article.get("seendate") or ""),
            source_url=url,
            title=article.get("title"),
            source_confidence=0.75,
            dedupe_key=f"gdelt:{url}",
        )
        if obs is not None:
            created.append(obs)
    return created

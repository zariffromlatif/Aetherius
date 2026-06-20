"""SEC EDGAR ingestion adapter.

Pulls recent filings for a ticker from SEC's free JSON API (no key required)
and feeds them into the existing ingestion pipeline as SourceObservations.

SEC requires a descriptive User-Agent on every request (see settings.sec_user_agent)
or it returns 403. Be polite: SEC asks for <= 10 requests/second.
"""
from __future__ import annotations

from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import SourceObservations
from app.services.ingestion.service import ingest_observation

# Filing forms most relevant to downside risk.
DOWNSIDE_FORMS: frozenset[str] = frozenset({"8-K", "10-Q", "10-K", "8-K/A", "10-Q/A", "10-K/A", "NT 10-Q", "NT 10-K"})

_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"


def _headers() -> dict[str, str]:
    return {"User-Agent": settings.sec_user_agent, "Accept": "application/json"}


def resolve_cik(ticker: str, client: httpx.Client) -> str | None:
    """Resolve a ticker symbol to a 10-digit zero-padded SEC CIK."""
    resp = client.get(_TICKERS_URL, headers=_headers())
    resp.raise_for_status()
    data = resp.json()
    target = ticker.strip().upper()
    for row in data.values():
        if str(row.get("ticker", "")).upper() == target:
            return str(row["cik_str"]).zfill(10)
    return None


def fetch_recent_filings(cik: str, client: httpx.Client, limit: int = 20) -> list[dict]:
    """Return recent downside-relevant filings for a CIK, newest first."""
    resp = client.get(_SUBMISSIONS_URL.format(cik=cik), headers=_headers())
    resp.raise_for_status()
    return parse_submissions(resp.json(), cik, limit=limit)


def parse_submissions(payload: dict, cik: str, limit: int = 20) -> list[dict]:
    """Parse SEC submissions JSON into a flat list of filing dicts.

    Pure function (no network) so it is unit-testable with a recorded sample.
    """
    recent = (payload.get("filings", {}) or {}).get("recent", {}) or {}
    forms = recent.get("form", []) or []
    dates = recent.get("filingDate", []) or []
    accessions = recent.get("accessionNumber", []) or []
    docs = recent.get("primaryDocument", []) or []
    primary_desc = recent.get("primaryDocDescription", []) or []

    out: list[dict] = []
    for i, form in enumerate(forms):
        if form not in DOWNSIDE_FORMS:
            continue
        accession = accessions[i] if i < len(accessions) else ""
        accession_nodash = accession.replace("-", "")
        doc = docs[i] if i < len(docs) else ""
        url = (
            f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_nodash}/{doc}"
            if accession_nodash and doc
            else f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}"
        )
        out.append(
            {
                "form": form,
                "filing_date": dates[i] if i < len(dates) else "",
                "accession": accession,
                "description": primary_desc[i] if i < len(primary_desc) else "",
                "url": url,
            }
        )
        if len(out) >= limit:
            break
    return out


def _filing_to_text(ticker: str, filing: dict) -> str:
    return (
        f"SEC {filing['form']} filing for {ticker.upper()} "
        f"dated {filing['filing_date']}. "
        f"{filing.get('description') or 'Filing'}. "
        f"Accession {filing['accession']}. Source: {filing['url']}"
    )


def _parse_filing_date(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def ingest_filings_for_ticker(db: Session, ticker: str, limit: int = 20) -> list[SourceObservations]:
    """Fetch recent EDGAR filings for a ticker and ingest them as observations.

    Returns only the newly-created observations (dedupe drops repeats).
    """
    with httpx.Client(timeout=30.0) as client:
        cik = resolve_cik(ticker, client)
        if not cik:
            return []
        filings = fetch_recent_filings(cik, client, limit=limit)

    created: list[SourceObservations] = []
    for filing in filings:
        obs = ingest_observation(
            db=db,
            source_type="sec_edgar",
            source_name=f"SEC EDGAR {filing['form']}",
            raw_text=_filing_to_text(ticker, filing),
            observed_at=_parse_filing_date(filing["filing_date"]),
            source_url=filing["url"],
            title=f"{ticker.upper()} {filing['form']} {filing['filing_date']}",
            source_confidence=0.95,  # official filings: high source confidence
            dedupe_key=f"edgar:{filing['accession']}",
        )
        if obs is not None:
            created.append(obs)
    return created


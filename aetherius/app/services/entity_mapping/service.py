import re

from sqlalchemy.orm import Session

from app.models.entities import CompanyAliases, EntityRelationships, EvidenceLinks, ObservationEntities, SourceObservations, WatchlistItems

# Common all-caps tokens that look like tickers but are not securities.
# Prevents "CEO", "USD", "GDP", "FED", "AI" etc. from being extracted as companies.
UPPERCASE_STOPLIST: frozenset[str] = frozenset(
    {
        # Roles / org
        "CEO", "CFO", "COO", "CTO", "CIO", "VP", "SVP", "EVP", "IR", "PR", "HR", "MD", "GM",
        # Macro / econ
        "GDP", "CPI", "PPI", "PCE", "PMI", "FED", "FOMC", "ECB", "BOE", "BOJ", "IMF", "OECD",
        "GAAP", "EPS", "EBIT", "EBITDA", "YOY", "QOQ", "YTD", "FY", "Q1", "Q2", "Q3", "Q4",
        "ROE", "ROI", "ROIC", "APR", "APY", "BPS", "NAV", "AUM", "IPO",
        # Currencies
        "USD", "EUR", "GBP", "JPY", "CNY", "CHF", "CAD", "AUD", "HKD", "INR",
        # Agencies / regulators
        "SEC", "FTC", "DOJ", "FDA", "FCC", "FAA", "EPA", "IRS", "CFTC", "FINRA", "OFAC",
        # Tech / general
        "AI", "ML", "API", "B2B", "B2C", "IT", "OS", "PC", "US", "USA", "UK", "EU", "UN",
        "COVID", "ESG", "KPI", "TAM", "SAM", "ARR", "MRR", "YOLO", "FAQ",
    }
)

# A plausible US equity ticker: 1-5 uppercase letters, optionally with a class suffix (e.g. BRK.B).
_TICKER_RE = re.compile(r"^[A-Z]{1,5}(?:\.[A-Z])?$")


def _looks_like_ticker(token: str) -> bool:
    """Heuristic gate for ticker-shaped tokens, excluding common non-ticker acronyms.

    This is intentionally conservative: it filters obvious noise. Authoritative
    confirmation happens in ``map_to_watchlist`` against the watchlist/alias tables.
    """
    if token in UPPERCASE_STOPLIST:
        return False
    return bool(_TICKER_RE.match(token))


def extract_entities(raw_text: str) -> list[dict]:
    """Extract candidate ticker-like entities from text.

    Conservative by design: it strips surrounding punctuation, requires a
    ticker-shaped token, and excludes a stoplist of common acronyms
    (CEO, USD, GDP, FED, AI, ...) so they are not mislabeled as companies.
    Deduplicates within a single observation.
    """
    entities: list[dict] = []
    seen: set[str] = set()
    for word in raw_text.split():
        # "$AAPL" cashtags are a strong ticker signal; note it, then strip the $.
        is_cashtag = word.lstrip(",.([{\"'").startswith("$")
        token = word.strip(",.()[]{}:;!?\"'").lstrip("$")
        if not token or token in seen:
            continue
        if _looks_like_ticker(token):
            seen.add(token)
            confidence = 0.85 if is_cashtag else 0.6
            entities.append(
                {"entity_name": token, "ticker": token, "entity_type": "company", "match_confidence": confidence}
            )
    return entities[:20]


def persist_entities(db: Session, observation_id: str, entities: list[dict]) -> list[ObservationEntities]:
    rows: list[ObservationEntities] = []
    for entity in entities:
        row = ObservationEntities(observation_id=observation_id, **entity)
        db.add(row)
        rows.append(row)
    db.commit()
    return rows


def _contains_phrase(text_upper: str, phrase: str | None) -> bool:
    """Word-boundary-aware containment check.

    Avoids false positives from naive substring matching, e.g. ticker ``AI``
    matching inside ``CHAIN`` / ``SAID``, or ``CAT`` inside ``CATALYST``.
    """
    if not phrase:
        return False
    phrase = phrase.strip().upper()
    if not phrase:
        return False
    return re.search(rf"(?<![A-Z0-9]){re.escape(phrase)}(?![A-Z0-9])", text_upper) is not None


def map_to_watchlist(db: Session, observation: SourceObservations) -> list[EvidenceLinks]:
    """Map an observation to active watchlist items using word-boundary matching.

    Match precedence per item: direct (ticker/company/alias) > sector >
    relationship readthrough. Word-boundary matching prevents short tickers
    from matching inside unrelated words.
    """
    text_upper = observation.raw_text.upper()
    matches: list[EvidenceLinks] = []
    aliases = db.query(CompanyAliases).all()
    # A ticker can have multiple aliases; collect them all.
    aliases_by_ticker: dict[str, list[str]] = {}
    for a in aliases:
        if a.ticker:
            aliases_by_ticker.setdefault(a.ticker.upper(), []).append(a.alias.upper())

    watch_items = db.query(WatchlistItems).filter(WatchlistItems.active.is_(True)).all()
    for item in watch_items:
        rel = None
        score = 0.0
        ticker_up = item.ticker.upper()
        item_aliases = aliases_by_ticker.get(ticker_up, [])

        direct_hit = (
            _contains_phrase(text_upper, ticker_up)
            or _contains_phrase(text_upper, item.company_name)
            or any(_contains_phrase(text_upper, alias) for alias in item_aliases)
        )
        if direct_hit:
            rel = "direct"
            score = 0.9
        elif item.sector and _contains_phrase(text_upper, item.sector):
            rel = "sector"
            score = 0.55
        else:
            links = db.query(EntityRelationships).filter(EntityRelationships.watchlist_item_id == item.id).all()
            for link in links:
                if _contains_phrase(text_upper, link.related_entity_name) or (
                    link.related_ticker and _contains_phrase(text_upper, link.related_ticker)
                ):
                    rel = f"{link.relationship_type}_readthrough"
                    score = float(link.strength or 0.45)
                    break
        if rel:
            ev = EvidenceLinks(
                observation_id=observation.id,
                watchlist_item_id=item.id,
                relationship_type=rel,
                relevance_score=score,
                evidence_summary=f"{item.ticker} matched via {rel} mapping.",
            )
            db.add(ev)
            matches.append(ev)
    db.commit()
    return matches

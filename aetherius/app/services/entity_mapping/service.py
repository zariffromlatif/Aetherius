from sqlalchemy.orm import Session

from app.models.entities import CompanyAliases, EntityRelationships, EvidenceLinks, ObservationEntities, SourceObservations, WatchlistItems


def extract_entities(raw_text: str) -> list[dict]:
    entities: list[dict] = []
    words = raw_text.split()
    for w in words:
        token = w.strip(",.()[]")
        if 1 < len(token) <= 5 and token.isupper():
            entities.append({"entity_name": token, "ticker": token, "entity_type": "company", "match_confidence": 0.75})
    return entities[:20]


def persist_entities(db: Session, observation_id: str, entities: list[dict]) -> list[ObservationEntities]:
    rows: list[ObservationEntities] = []
    for entity in entities:
        row = ObservationEntities(observation_id=observation_id, **entity)
        db.add(row)
        rows.append(row)
    db.commit()
    return rows


def map_to_watchlist(db: Session, observation: SourceObservations) -> list[EvidenceLinks]:
    text = observation.raw_text.upper()
    matches: list[EvidenceLinks] = []
    aliases = db.query(CompanyAliases).all()
    alias_by_ticker = {a.ticker.upper(): a.alias.upper() for a in aliases if a.ticker}
    watch_items = db.query(WatchlistItems).filter(WatchlistItems.active.is_(True)).all()
    for item in watch_items:
        rel = None
        score = 0.0
        alias = alias_by_ticker.get(item.ticker.upper())
        if item.ticker.upper() in text or item.company_name.upper() in text or (alias and alias in text):
            rel = "direct"
            score = 0.9
        elif item.sector and item.sector.upper() in text:
            rel = "sector"
            score = 0.55
        else:
            links = db.query(EntityRelationships).filter(EntityRelationships.watchlist_item_id == item.id).all()
            for link in links:
                if link.related_entity_name.upper() in text or (link.related_ticker and link.related_ticker.upper() in text):
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

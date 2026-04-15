from sqlalchemy.orm import Session

from app.models.entities import EntityRelationships, WatchlistItems, Watchlists
from app.schemas.watchlists import WatchlistCreate, WatchlistItemCreate


def create_watchlist(db: Session, payload: WatchlistCreate) -> Watchlists:
    obj = Watchlists(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_watchlists(db: Session, client_id: str | None = None) -> list[Watchlists]:
    q = db.query(Watchlists)
    if client_id:
        q = q.filter(Watchlists.client_id == client_id)
    return q.order_by(Watchlists.created_at.desc()).all()


def create_watchlist_item(db: Session, payload: WatchlistItemCreate) -> WatchlistItems:
    obj = WatchlistItems(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_watchlist_items(db: Session, watchlist_id: str) -> list[WatchlistItems]:
    return db.query(WatchlistItems).filter(WatchlistItems.watchlist_id == watchlist_id).all()


def create_relationship(
    db: Session,
    watchlist_item_id: str,
    related_entity_name: str,
    relationship_type: str,
    related_ticker: str | None = None,
    strength: float | None = None,
    notes: str | None = None,
) -> EntityRelationships:
    obj = EntityRelationships(
        watchlist_item_id=watchlist_item_id,
        related_entity_name=related_entity_name,
        related_ticker=related_ticker,
        relationship_type=relationship_type,
        strength=strength,
        notes=notes,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

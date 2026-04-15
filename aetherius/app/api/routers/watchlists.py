from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_operator
from app.schemas.watchlists import WatchlistCreate, WatchlistItemCreate, WatchlistItemOut, WatchlistOut
from app.services.watchlists.service import (
    create_relationship,
    create_watchlist,
    create_watchlist_item,
    list_watchlist_items,
    list_watchlists,
)

router = APIRouter(prefix="/watchlists", tags=["watchlists"], dependencies=[Depends(require_operator)])


class RelationshipCreate(BaseModel):
    watchlist_item_id: str
    related_entity_name: str
    relationship_type: str
    related_ticker: str | None = None
    strength: float | None = None
    notes: str | None = None


@router.post("", response_model=WatchlistOut)
def create_watchlist_endpoint(payload: WatchlistCreate, db: Session = Depends(get_db)):
    return create_watchlist(db, payload)


@router.get("", response_model=list[WatchlistOut])
def list_watchlists_endpoint(client_id: str | None = None, db: Session = Depends(get_db)):
    return list_watchlists(db, client_id)


@router.post("/items", response_model=WatchlistItemOut)
def create_watchlist_item_endpoint(payload: WatchlistItemCreate, db: Session = Depends(get_db)):
    return create_watchlist_item(db, payload)


@router.get("/{watchlist_id}/items", response_model=list[WatchlistItemOut])
def list_watchlist_items_endpoint(watchlist_id: str, db: Session = Depends(get_db)):
    return list_watchlist_items(db, watchlist_id)


@router.post("/relationships")
def create_relationship_endpoint(payload: RelationshipCreate, db: Session = Depends(get_db)):
    return create_relationship(db, **payload.model_dump())

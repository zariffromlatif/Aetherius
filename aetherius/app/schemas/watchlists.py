from uuid import UUID

from pydantic import BaseModel


class WatchlistCreate(BaseModel):
    client_id: UUID
    name: str
    active: bool = True


class WatchlistOut(BaseModel):
    id: UUID
    client_id: UUID
    name: str
    active: bool

    class Config:
        from_attributes = True


class WatchlistItemCreate(BaseModel):
    watchlist_id: UUID
    ticker: str
    company_name: str
    sector: str | None = None
    industry: str | None = None
    priority_level: str = "normal"
    book_context: str = "near_book"
    notes: str | None = None
    custom_tags: list[str] | None = None
    active: bool = True


class WatchlistItemOut(BaseModel):
    id: UUID
    watchlist_id: UUID
    ticker: str
    company_name: str
    priority_level: str
    book_context: str
    active: bool

    class Config:
        from_attributes = True

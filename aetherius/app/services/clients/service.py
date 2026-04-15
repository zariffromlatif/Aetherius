from sqlalchemy.orm import Session

from app.models.entities import ClientConfigs, Clients
from app.schemas.clients import ClientConfigCreate, ClientCreate


def create_client(db: Session, payload: ClientCreate) -> Clients:
    obj = Clients(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_clients(db: Session) -> list[Clients]:
    return db.query(Clients).order_by(Clients.created_at.desc()).all()


def create_client_config(db: Session, payload: ClientConfigCreate) -> ClientConfigs:
    obj = ClientConfigs(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

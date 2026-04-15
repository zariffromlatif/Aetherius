from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_operator
from app.schemas.clients import ClientConfigCreate, ClientConfigOut, ClientCreate, ClientOut
from app.services.clients.service import create_client, create_client_config, list_clients

router = APIRouter(prefix="/clients", tags=["clients"], dependencies=[Depends(require_operator)])


@router.post("", response_model=ClientOut)
def create_client_endpoint(payload: ClientCreate, db: Session = Depends(get_db)):
    return create_client(db, payload)


@router.get("", response_model=list[ClientOut])
def list_clients_endpoint(db: Session = Depends(get_db)):
    return list_clients(db)


@router.post("/configs", response_model=ClientConfigOut)
def create_client_config_endpoint(payload: ClientConfigCreate, db: Session = Depends(get_db)):
    return create_client_config(db, payload)


@router.post("/quick-create")
def quick_create_client_endpoint(payload: ClientCreate, db: Session = Depends(get_db)):
    client = create_client(db, payload)
    cfg = create_client_config(
        db,
        ClientConfigCreate(
            client_id=client.id,
            alert_mode="balanced",
            daily_brief_delivery_channel="email",
            urgent_alert_channel="email",
        ),
    )
    return {"client": client, "config": cfg}

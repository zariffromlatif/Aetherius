from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.schemas.auth import LoginRequest, OperatorCreate, OperatorOut, TokenResponse
from app.services.auth.service import authenticate_operator, create_access_token, create_operator

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_operator(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(user))


@router.post("/operators", response_model=OperatorOut, dependencies=[Depends(require_admin)])
def create_operator_endpoint(payload: OperatorCreate, db: Session = Depends(get_db)):
    return create_operator(db, email=payload.email, password=payload.password, role=payload.role, full_name=payload.full_name)


@router.post("/bootstrap-admin", response_model=OperatorOut)
def bootstrap_admin(payload: OperatorCreate, db: Session = Depends(get_db)):
    from app.models.entities import OperatorUsers

    existing = db.query(OperatorUsers).count()
    if existing > 0:
        raise HTTPException(status_code=403, detail="Bootstrap disabled after first operator exists")
    return create_operator(db, email=payload.email, password=payload.password, role="admin", full_name=payload.full_name)

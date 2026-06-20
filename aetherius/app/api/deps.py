import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db


def db_dep() -> Session:
    return Depends(get_db)


def _decode_bearer(authorization: str) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {exc}") from exc


def require_operator(authorization: str = Header(default="")) -> dict:
    return _decode_bearer(authorization)


def require_admin(claims: dict = Depends(require_operator)) -> dict:
    if claims.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return claims


def require_client_scope(client_id: str, claims: dict = Depends(require_operator)) -> dict:
    # Authority is derived from the authenticated operator, never from a
    # client-supplied header. Admins may act across all clients.
    #
    # NOTE: This is correct for a single trusted operator team. When outside
    # analysts are onboarded, replace the role check below with a lookup
    # against an operator_client_assignments table (operator_id, client_id)
    # and verify membership here.
    if claims.get("role") == "admin":
        return claims
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Cross-client action requires admin role",
    )

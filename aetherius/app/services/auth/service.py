from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import OperatorUsers

# Use PBKDF2 for portability in minimal containers.
# bcrypt requires native backends which can be brittle in slim images.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_operator(db: Session, email: str, password: str, role: str, full_name: str | None = None) -> OperatorUsers:
    op = OperatorUsers(email=email, password_hash=hash_password(password), role=role, full_name=full_name, active=True)
    db.add(op)
    db.commit()
    db.refresh(op)
    return op


def authenticate_operator(db: Session, email: str, password: str) -> OperatorUsers | None:
    user = db.query(OperatorUsers).filter(OperatorUsers.email == email, OperatorUsers.active.is_(True)).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(user: OperatorUsers) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.access_token_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

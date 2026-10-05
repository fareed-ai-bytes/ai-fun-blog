"""Registration and authentication rules (FR-01, FR-02, BR-11, BR-12). No FastAPI here."""

import uuid

from sqlalchemy.orm import Session

from app.core import security
from app.core.errors import Unauthorized
from app.modules import users
from app.modules.users.models import User

INVALID_CREDENTIALS = "Invalid email or password"


def register(db: Session, *, email: str, username: str, display_name: str, password: str) -> User:
    user = users.create_user(
        db,
        email=email,
        username=username,
        display_name=display_name,
        password_hash=security.hash_password(password),
    )
    db.commit()
    return user


def authenticate(db: Session, *, email: str, password: str) -> User:
    """Same 401 whether the email or the password is wrong (BR-12)."""
    user = users.get_user_by_email(db, email)
    # Always run a hash verification, even for unknown emails, so timing reveals nothing.
    password_ok = security.verify_password(password, user.password_hash if user else None)
    if user is None or not password_ok:
        raise Unauthorized("INVALID_CREDENTIALS", INVALID_CREDENTIALS)
    return user


def issue_token(user: User) -> str:
    return security.create_access_token(user.id)


def user_from_token(db: Session, token: str | None) -> User | None:
    """Resolve the user behind an access token; None if absent, invalid, expired or deleted."""
    if not token:
        return None
    user_id: uuid.UUID | None = security.decode_access_token(token)
    if user_id is None:
        return None
    return users.get_user(db, user_id)

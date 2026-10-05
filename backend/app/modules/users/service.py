"""Public interface of the users module (used by auth, posts, comments)."""

import uuid

from sqlalchemy.orm import Session

from app.core.errors import Conflict
from app.modules.users import repository
from app.modules.users.models import User


def get_user(db: Session, user_id: uuid.UUID) -> User | None:
    return repository.get_by_id(db, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return repository.get_by_email(db, email)


def get_user_by_username(db: Session, username: str) -> User | None:
    return repository.get_by_username(db, username)


def create_user(
    db: Session, *, email: str, username: str, display_name: str, password_hash: str
) -> User:
    """Create a user. Email/username are expected normalised (lowercase) by the caller."""
    if repository.get_by_email(db, email) is not None:
        raise Conflict(
            "EMAIL_TAKEN", "An account with this email already exists", {"field": "email"}
        )
    if repository.get_by_username(db, username) is not None:
        raise Conflict("USERNAME_TAKEN", "This username is taken", {"field": "username"})
    user = User(
        email=email, username=username, display_name=display_name, password_hash=password_hash
    )
    return repository.add(db, user)

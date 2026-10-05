"""Data access for users. All SQL for the users table lives here."""

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import Conflict
from app.modules.users.models import User

_UNIQUE_CONFLICTS = {
    "uq_users_email": ("EMAIL_TAKEN", "email", "An account with this email already exists"),
    "uq_users_username": ("USERNAME_TAKEN", "username", "This username is taken"),
}


def get_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username))


def add(db: Session, user: User) -> User:
    """Insert a user; a unique-constraint race is reported as the matching Conflict."""
    try:
        with db.begin_nested():
            db.add(user)
            db.flush()
    except IntegrityError as exc:
        for constraint, (code, field, message) in _UNIQUE_CONFLICTS.items():
            if constraint in str(exc.orig):
                raise Conflict(code, message, {"field": field}) from exc
        raise
    return user

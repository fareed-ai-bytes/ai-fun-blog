"""Data access for likes. All SQL for the likes table lives here."""

import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.modules.likes.models import Like


def add_if_absent(db: Session, *, user_id: uuid.UUID, post_id: uuid.UUID) -> None:
    """Idempotent insert: a second like by the same user is a no-op (BR-04)."""
    stmt = insert(Like).values(user_id=user_id, post_id=post_id).on_conflict_do_nothing()
    db.execute(stmt)


def remove(db: Session, *, user_id: uuid.UUID, post_id: uuid.UUID) -> None:
    db.execute(delete(Like).where(Like.user_id == user_id, Like.post_id == post_id))


def count_for_post(db: Session, post_id: uuid.UUID) -> int:
    return db.scalar(select(func.count()).select_from(Like).where(Like.post_id == post_id)) or 0

"""Data access for comments. All SQL for the comments table lives here."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.modules.comments.models import Comment


def get_by_id(db: Session, comment_id: uuid.UUID) -> Comment | None:
    return db.get(Comment, comment_id)


def list_for_post(
    db: Session, post_id: uuid.UUID, *, limit: int, offset: int
) -> tuple[list[Comment], int]:
    """Oldest first (BR-13), authors loaded in the same query."""
    condition = Comment.post_id == post_id
    total = db.scalar(select(func.count()).select_from(Comment).where(condition)) or 0
    stmt = (
        select(Comment)
        .options(joinedload(Comment.author))
        .where(condition)
        .order_by(Comment.created_at.asc(), Comment.id.asc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(stmt)), total


def add(db: Session, comment: Comment) -> Comment:
    db.add(comment)
    db.flush()
    return comment


def remove(db: Session, comment: Comment) -> None:
    db.delete(comment)
    db.flush()

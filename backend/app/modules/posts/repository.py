"""Data access for posts. All SQL for the posts table lives here.

Read-model exception (memory.md, 2026-10-05): list/detail queries also read the likes and
comments tables to compute counts and `liked_by_me` in ONE query per page (NFR: no N+1).
This module never writes to those tables.
"""

import uuid
from dataclasses import dataclass

from sqlalchemy import ColumnElement, Select, exists, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.modules.comments.models import Comment
from app.modules.likes.models import Like
from app.modules.posts.models import Post, PostStatus
from app.modules.users.models import User


class SlugTaken(Exception):
    """Raised when a concurrent insert grabbed the slug first; the caller retries."""


@dataclass(frozen=True)
class PostWithCounts:
    post: Post
    like_count: int
    comment_count: int


def _like_count() -> ColumnElement[int]:
    return (
        select(func.count())
        .where(Like.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
        .label("like_count")
    )


def _comment_count() -> ColumnElement[int]:
    return (
        select(func.count())
        .where(Comment.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
        .label("comment_count")
    )


def _with_counts() -> Select[tuple[Post, int, int]]:
    return select(Post, _like_count(), _comment_count()).options(joinedload(Post.author))


def _rows(db: Session, stmt: Select[tuple[Post, int, int]]) -> list[PostWithCounts]:
    return [PostWithCounts(post, likes, comments) for post, likes, comments in db.execute(stmt)]


def get_by_id(db: Session, post_id: uuid.UUID) -> Post | None:
    return db.get(Post, post_id)


def get_with_counts_by_id(db: Session, post_id: uuid.UUID) -> PostWithCounts | None:
    rows = _rows(db, _with_counts().where(Post.id == post_id))
    return rows[0] if rows else None


def get_with_counts_by_slug(db: Session, slug: str) -> PostWithCounts | None:
    rows = _rows(db, _with_counts().where(Post.slug == slug))
    return rows[0] if rows else None


def list_published(
    db: Session, *, author_username: str | None, limit: int, offset: int
) -> tuple[list[PostWithCounts], int]:
    """Feed: published posts, newest first, `id` as tie-breaker (BR-13)."""
    conditions: list[ColumnElement[bool]] = [Post.status == PostStatus.PUBLISHED]
    if author_username is not None:
        conditions.append(
            Post.author_id.in_(select(User.id).where(User.username == author_username))
        )
    total = db.scalar(select(func.count()).select_from(Post).where(*conditions)) or 0
    stmt = (
        _with_counts()
        .where(*conditions)
        .order_by(Post.published_at.desc(), Post.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return _rows(db, stmt), total


def list_by_author(
    db: Session, author_id: uuid.UUID, *, limit: int, offset: int
) -> tuple[list[PostWithCounts], int]:
    """My posts: every status, most recently updated first."""
    condition = Post.author_id == author_id
    total = db.scalar(select(func.count()).select_from(Post).where(condition)) or 0
    stmt = (
        _with_counts()
        .where(condition)
        .order_by(Post.updated_at.desc(), Post.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return _rows(db, stmt), total


def is_liked_by(db: Session, post_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    stmt = select(exists().where(Like.post_id == post_id, Like.user_id == user_id))
    return bool(db.scalar(stmt))


def slugs_taken(db: Session, base: str) -> set[str]:
    """Existing slugs equal to `base` or of the form `base-N`. Slugs are [a-z0-9-] only,
    so LIKE needs no escaping."""
    stmt = select(Post.slug).where(or_(Post.slug == base, Post.slug.like(f"{base}-%")))
    return set(db.scalars(stmt))


def add(db: Session, post: Post) -> Post:
    try:
        with db.begin_nested():
            db.add(post)
            db.flush()
    except IntegrityError as exc:
        if "uq_posts_slug" in str(exc.orig):
            raise SlugTaken from exc
        raise
    return post


def flush(db: Session) -> None:
    db.flush()


def remove(db: Session, post: Post) -> None:
    """Delete a post; likes and comments go with it via ON DELETE CASCADE (BR-15)."""
    db.delete(post)
    db.flush()

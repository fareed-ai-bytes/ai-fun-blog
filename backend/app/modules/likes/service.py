"""Like rules: FR-10, BR-03 (no self-likes), BR-04 (idempotent), BR-05 (published only)."""

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.errors import Forbidden
from app.modules import posts
from app.modules.likes import repository
from app.modules.users.models import User


@dataclass(frozen=True)
class LikeStateView:
    like_count: int
    liked_by_me: bool


def like_post(db: Session, user: User, post_id: uuid.UUID) -> LikeStateView:
    post = posts.get_published_post(db, post_id)  # draft or missing → 404 (BR-05)
    if post.author_id == user.id:
        raise Forbidden("CANNOT_LIKE_OWN_POST", "You can't like your own post")
    repository.add_if_absent(db, user_id=user.id, post_id=post.id)
    db.commit()
    return LikeStateView(like_count=repository.count_for_post(db, post.id), liked_by_me=True)


def unlike_post(db: Session, user: User, post_id: uuid.UUID) -> LikeStateView:
    post = posts.get_published_post(db, post_id)
    repository.remove(db, user_id=user.id, post_id=post.id)
    db.commit()
    return LikeStateView(like_count=repository.count_for_post(db, post.id), liked_by_me=False)

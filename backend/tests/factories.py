"""Plain factory functions for test data. They flush (not commit) so the per-test
rollback in conftest.py removes everything."""

import itertools
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.modules.comments.models import Comment
from app.modules.likes.models import Like
from app.modules.posts.models import Post, PostStatus
from app.modules.users.models import User

DEFAULT_PASSWORD = "correct-horse-battery"
_DEFAULT_HASH = hash_password(DEFAULT_PASSWORD)  # hash once; argon2 is deliberately slow
_seq = itertools.count(1)


def make_user(db: Session, username: str | None = None, **overrides: object) -> User:
    n = next(_seq)
    username = username or f"user{n}"
    user = User(
        email=str(overrides.pop("email", f"{username}@example.com")).lower(),
        username=username,
        display_name=str(overrides.pop("display_name", f"User {n}")),
        password_hash=str(overrides.pop("password_hash", _DEFAULT_HASH)),
    )
    db.add(user)
    db.flush()
    return user


def make_post(
    db: Session,
    author: User,
    *,
    title: str | None = None,
    body_md: str = "Some **markdown** body text.",
    status: PostStatus = PostStatus.PUBLISHED,
    published_at: datetime | None = None,
) -> Post:
    n = next(_seq)
    title = title or f"Post {n}"
    if status is PostStatus.PUBLISHED and published_at is None:
        published_at = datetime.now(UTC)
    post = Post(
        author_id=author.id,
        title=title,
        slug=f"post-{n}",
        body_md=body_md,
        excerpt=body_md[:280],
        status=status,
        published_at=published_at,
    )
    db.add(post)
    db.flush()
    return post


def make_like(db: Session, user: User, post: Post) -> Like:
    like = Like(user_id=user.id, post_id=post.id)
    db.add(like)
    db.flush()
    return like


def make_comment(db: Session, author: User, post: Post, body: str = "Nice post!") -> Comment:
    comment = Comment(post_id=post.id, author_id=author.id, body=body)
    db.add(comment)
    db.flush()
    return comment

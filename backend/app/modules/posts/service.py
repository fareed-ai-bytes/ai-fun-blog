"""Post business rules: ownership, visibility, slugs, excerpts, publishing.
Covers FR-03–FR-09, FR-14 and BR-01, BR-02, BR-08–BR-10, BR-13–BR-15."""

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.core.errors import Forbidden, NotFound
from app.core.pagination import POSTS_PAGE_SIZE, offset_for
from app.db.timestamps import utcnow
from app.modules.posts import repository
from app.modules.posts.models import Post, PostStatus
from app.modules.posts.repository import PostWithCounts, SlugTaken
from app.modules.posts.text import make_excerpt, next_free_slug, slugify
from app.modules.users.models import User

_SLUG_RETRIES = 3


@dataclass(frozen=True)
class PostDetailView:
    row: PostWithCounts
    liked_by_me: bool
    is_owner: bool


@dataclass(frozen=True)
class PostPage:
    rows: list[PostWithCounts]
    page: int
    page_size: int
    total: int


def _not_found() -> NotFound:
    return NotFound("POST_NOT_FOUND", "Post not found")


def is_visible_to(post: Post, viewer: User | None) -> bool:
    """BR-01: published posts are public; drafts only to their author."""
    return post.status is PostStatus.PUBLISHED or (
        viewer is not None and post.author_id == viewer.id
    )


def _load_owned(db: Session, user: User, post_id: uuid.UUID) -> Post:
    """404 if missing or a draft the user can't see (BR-01); 403 if visible but not theirs."""
    post = repository.get_by_id(db, post_id)
    if post is None or not is_visible_to(post, user):
        raise _not_found()
    if post.author_id != user.id:
        raise Forbidden("NOT_POST_OWNER", "Only the author can change this post")
    return post


def _apply_status(post: Post, status: PostStatus) -> None:
    post.status = status
    if status is PostStatus.PUBLISHED and post.published_at is None:
        post.published_at = utcnow()  # BR-08: first publish only


def _detail(db: Session, post_id: uuid.UUID, viewer: User | None) -> PostDetailView:
    row = repository.get_with_counts_by_id(db, post_id)
    if row is None:
        raise _not_found()
    return _detail_from_row(db, row, viewer)


def _detail_from_row(db: Session, row: PostWithCounts, viewer: User | None) -> PostDetailView:
    is_owner = viewer is not None and row.post.author_id == viewer.id
    liked = viewer is not None and repository.is_liked_by(db, row.post.id, viewer.id)
    return PostDetailView(row=row, liked_by_me=liked, is_owner=is_owner)


def create_post(
    db: Session, author: User, *, title: str, body_md: str, status: PostStatus
) -> PostDetailView:
    base = slugify(title)
    for _attempt in range(_SLUG_RETRIES):
        post = Post(
            author_id=author.id,
            title=title,
            slug=next_free_slug(base, repository.slugs_taken(db, base)),
            body_md=body_md,
            excerpt=make_excerpt(body_md),
        )
        _apply_status(post, status)
        try:
            repository.add(db, post)
            break
        except SlugTaken:
            continue  # a concurrent request took the slug; recompute and retry
    else:
        raise RuntimeError("Could not allocate a unique slug")
    db.commit()
    return _detail(db, post.id, author)


def update_post(
    db: Session, user: User, post_id: uuid.UUID, changes: dict[str, Any]
) -> PostDetailView:
    """Apply any of title/body_md/status. The slug never changes (BR-10)."""
    post = _load_owned(db, user, post_id)
    if "title" in changes:
        post.title = changes["title"]
    if "body_md" in changes:
        post.body_md = changes["body_md"]
        post.excerpt = make_excerpt(post.body_md)
    if "status" in changes:
        _apply_status(post, PostStatus(changes["status"]))
    repository.flush(db)
    db.commit()
    return _detail(db, post.id, user)


def delete_post(db: Session, user: User, post_id: uuid.UUID) -> None:
    post = _load_owned(db, user, post_id)
    repository.remove(db, post)
    db.commit()


def list_my_posts(db: Session, user: User, page: int) -> PostPage:
    rows, total = repository.list_by_author(
        db, user.id, limit=POSTS_PAGE_SIZE, offset=offset_for(page, POSTS_PAGE_SIZE)
    )
    return PostPage(rows=rows, page=page, page_size=POSTS_PAGE_SIZE, total=total)


def list_feed(db: Session, page: int, author_username: str | None = None) -> PostPage:
    rows, total = repository.list_published(
        db,
        author_username=author_username,
        limit=POSTS_PAGE_SIZE,
        offset=offset_for(page, POSTS_PAGE_SIZE),
    )
    return PostPage(rows=rows, page=page, page_size=POSTS_PAGE_SIZE, total=total)


def get_post_by_slug(db: Session, slug: str, viewer: User | None) -> PostDetailView:
    row = repository.get_with_counts_by_slug(db, slug)
    if row is None or not is_visible_to(row.post, viewer):
        raise _not_found()
    return _detail_from_row(db, row, viewer)


def get_visible_post(db: Session, post_id: uuid.UUID, viewer: User | None) -> Post:
    """For other modules: the post if the viewer may see it, else 404."""
    post = repository.get_by_id(db, post_id)
    if post is None or not is_visible_to(post, viewer):
        raise _not_found()
    return post


def get_published_post(db: Session, post_id: uuid.UUID) -> Post:
    """For likes/comments: only published posts accept engagement (BR-05), else 404."""
    post = repository.get_by_id(db, post_id)
    if post is None or post.status is not PostStatus.PUBLISHED:
        raise _not_found()
    return post

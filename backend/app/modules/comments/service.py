"""Comment rules: FR-11–FR-13, BR-05 (published only), BR-06, BR-07, BR-09."""

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.errors import Forbidden, NotFound
from app.core.pagination import COMMENTS_PAGE_SIZE, offset_for
from app.modules import posts
from app.modules.comments import repository
from app.modules.comments.models import Comment
from app.modules.users.models import User


@dataclass(frozen=True)
class CommentView:
    comment: Comment
    can_delete: bool


@dataclass(frozen=True)
class CommentPage:
    items: list[CommentView]
    page: int
    page_size: int
    total: int


def _can_delete(comment: Comment, post_author_id: uuid.UUID, viewer: User | None) -> bool:
    """BR-07: the comment's author or the post's author."""
    return viewer is not None and viewer.id in (comment.author_id, post_author_id)


def add_comment(db: Session, user: User, post_id: uuid.UUID, body: str) -> CommentView:
    post = posts.get_published_post(db, post_id)  # drafts → 404 (BR-05); own post OK (BR-06)
    comment = Comment(post_id=post.id, author_id=user.id, body=body, author=user)
    repository.add(db, comment)
    db.commit()
    return CommentView(comment=comment, can_delete=True)


def list_comments(db: Session, post_id: uuid.UUID, viewer: User | None, page: int) -> CommentPage:
    post = posts.get_visible_post(db, post_id, viewer)  # unpublished → author only (BR-09)
    comments, total = repository.list_for_post(
        db, post.id, limit=COMMENTS_PAGE_SIZE, offset=offset_for(page, COMMENTS_PAGE_SIZE)
    )
    items = [CommentView(c, _can_delete(c, post.author_id, viewer)) for c in comments]
    return CommentPage(items=items, page=page, page_size=COMMENTS_PAGE_SIZE, total=total)


def delete_comment(db: Session, user: User, comment_id: uuid.UUID) -> None:
    comment = repository.get_by_id(db, comment_id)
    if comment is None:
        raise NotFound("COMMENT_NOT_FOUND", "Comment not found")
    post = posts.get_visible_post(db, comment.post_id, user)
    if not _can_delete(comment, post.author_id, user):
        raise Forbidden(
            "NOT_ALLOWED_TO_DELETE_COMMENT",
            "Only the comment's author or the post's author can delete it",
        )
    repository.remove(db, comment)
    db.commit()

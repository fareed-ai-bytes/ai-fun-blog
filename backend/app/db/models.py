"""Imports every ORM model so Base.metadata is complete (used by Alembic and tests)."""

from app.db.base import Base
from app.modules.comments.models import Comment
from app.modules.likes.models import Like
from app.modules.posts.models import Post, PostStatus
from app.modules.users.models import User

__all__ = ["Base", "Comment", "Like", "Post", "PostStatus", "User"]

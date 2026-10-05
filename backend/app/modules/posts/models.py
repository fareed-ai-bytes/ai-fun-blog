import enum
import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.users.models import User


class PostStatus(enum.StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (
        CheckConstraint("char_length(title) BETWEEN 1 AND 200", name="title_length"),
        CheckConstraint("char_length(body_md) BETWEEN 1 AND 50000", name="body_md_length"),
        CheckConstraint("char_length(excerpt) <= 280", name="excerpt_length"),
        CheckConstraint(
            "status <> 'published' OR published_at IS NOT NULL", name="published_has_date"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(220), unique=True)
    body_md: Mapped[str] = mapped_column(Text)
    excerpt: Mapped[str] = mapped_column(String(280))
    status: Mapped[PostStatus] = mapped_column(
        Enum(PostStatus, name="post_status", values_callable=lambda e: [m.value for m in e]),
        default=PostStatus.DRAFT,
    )
    published_at: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    # lazy="raise": every load must be explicit (rules.md, Performance).
    author: Mapped[User] = relationship(lazy="raise")


# Declared outside __table_args__ so DESC is a column expression Alembic can compare.
Index("ix_posts_status_published_at", Post.status, Post.published_at.desc())
Index("ix_posts_author_id_updated_at", Post.author_id, Post.updated_at.desc())

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.posts.repository import PostWithCounts
from app.modules.posts.service import PostDetailView

StatusValue = Literal["draft", "published"]


def _strip_and_require(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("Must not be empty")
    return stripped


class PostCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    body_md: str = Field(min_length=1, max_length=50_000)
    status: StatusValue = "draft"

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        return _strip_and_require(value)

    @field_validator("body_md")
    @classmethod
    def body_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Must not be empty")
        return value


class PostUpdate(BaseModel):
    """Partial update: send any of title, body_md, status (at least one)."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    body_md: str | None = Field(default=None, min_length=1, max_length=50_000)
    status: StatusValue | None = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str | None) -> str | None:
        return None if value is None else _strip_and_require(value)

    @field_validator("body_md")
    @classmethod
    def body_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Must not be empty")
        return value

    @model_validator(mode="after")
    def at_least_one_non_null_field(self) -> "PostUpdate":
        provided = self.model_dump(exclude_unset=True)
        if not provided:
            raise ValueError("Provide at least one of title, body_md, status")
        if any(value is None for value in provided.values()):
            raise ValueError("Fields may not be null")
        return self


class Author(BaseModel):
    """Public author info — never includes email."""

    username: str
    display_name: str


class PostSummary(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    excerpt: str
    status: StatusValue
    author: Author
    published_at: datetime | None
    updated_at: datetime
    like_count: int
    comment_count: int

    @classmethod
    def from_row(cls, row: PostWithCounts) -> "PostSummary":
        post = row.post
        return cls(
            id=post.id,
            slug=post.slug,
            title=post.title,
            excerpt=post.excerpt,
            status=post.status.value,
            author=Author(username=post.author.username, display_name=post.author.display_name),
            published_at=post.published_at,
            updated_at=post.updated_at,
            like_count=row.like_count,
            comment_count=row.comment_count,
        )


class PostDetail(PostSummary):
    body_md: str
    liked_by_me: bool
    is_owner: bool

    @classmethod
    def from_view(cls, view: PostDetailView) -> "PostDetail":
        summary = PostSummary.from_row(view.row)
        return cls(
            **summary.model_dump(),
            body_md=view.row.post.body_md,
            liked_by_me=view.liked_by_me,
            is_owner=view.is_owner,
        )

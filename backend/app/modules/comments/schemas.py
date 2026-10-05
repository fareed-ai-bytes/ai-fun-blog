import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.comments.service import CommentView
from app.modules.posts.schemas import Author


class CommentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body: str = Field(min_length=1, max_length=2000)

    @field_validator("body")
    @classmethod
    def strip_body(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Must not be empty")
        return stripped


class CommentOut(BaseModel):
    id: uuid.UUID
    body: str
    author: Author
    created_at: datetime
    can_delete: bool

    @classmethod
    def from_view(cls, view: CommentView) -> "CommentOut":
        comment = view.comment
        return cls(
            id=comment.id,
            body=comment.body,
            author=Author(
                username=comment.author.username, display_name=comment.author.display_name
            ),
            created_at=comment.created_at,
            can_delete=view.can_delete,
        )

from pydantic import BaseModel

from app.modules.likes.service import LikeStateView


class LikeState(BaseModel):
    like_count: int
    liked_by_me: bool

    @classmethod
    def from_view(cls, view: LikeStateView) -> "LikeState":
        return cls(like_count=view.like_count, liked_by_me=view.liked_by_me)

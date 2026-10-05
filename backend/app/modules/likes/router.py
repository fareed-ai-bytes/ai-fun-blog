import uuid

from fastapi import APIRouter

from app.modules.auth.dependencies import CurrentUser, DbSession
from app.modules.likes import service
from app.modules.likes.schemas import LikeState

router = APIRouter(tags=["likes"])

_ERRORS = {
    401: {"description": "Not logged in"},
    404: {"description": "Post not found or not published"},
}


@router.put(
    "/posts/{post_id}/like",
    response_model=LikeState,
    status_code=200,
    operation_id="likes_put",
    summary="Like a post (idempotent)",
    responses=_ERRORS | {403: {"description": "You can't like your own post"}},
)
def like_post(post_id: uuid.UUID, user: CurrentUser, db: DbSession) -> LikeState:
    return LikeState.from_view(service.like_post(db, user, post_id))


@router.delete(
    "/posts/{post_id}/like",
    response_model=LikeState,
    status_code=200,
    operation_id="likes_delete",
    summary="Remove your like (idempotent)",
    responses=_ERRORS,
)
def unlike_post(post_id: uuid.UUID, user: CurrentUser, db: DbSession) -> LikeState:
    return LikeState.from_view(service.unlike_post(db, user, post_id))

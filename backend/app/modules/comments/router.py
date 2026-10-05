import uuid

from fastapi import APIRouter, Response

from app.core.pagination import Page
from app.core.params import PageNumber
from app.modules.auth.dependencies import CurrentUser, DbSession, OptionalUser
from app.modules.comments import service
from app.modules.comments.schemas import CommentCreate, CommentOut

router = APIRouter(tags=["comments"])

_AUTH = {401: {"description": "Not logged in"}}
_NOT_FOUND = {404: {"description": "Post or comment not found, or not visible to you"}}


@router.get(
    "/posts/{post_id}/comments",
    response_model=Page[CommentOut],
    status_code=200,
    operation_id="comments_list",
    summary="Comments on a post, oldest first",
    responses=_NOT_FOUND,
)
def list_comments(
    post_id: uuid.UUID, viewer: OptionalUser, db: DbSession, page: PageNumber = 1
) -> Page[CommentOut]:
    result = service.list_comments(db, post_id, viewer, page)
    return Page[CommentOut](
        items=[CommentOut.from_view(view) for view in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


@router.post(
    "/posts/{post_id}/comments",
    response_model=CommentOut,
    status_code=201,
    operation_id="comments_create",
    summary="Comment on a published post",
    responses=_AUTH | _NOT_FOUND,
)
def create_comment(
    post_id: uuid.UUID, body: CommentCreate, user: CurrentUser, db: DbSession
) -> CommentOut:
    return CommentOut.from_view(service.add_comment(db, user, post_id, body.body))


@router.delete(
    "/comments/{comment_id}",
    status_code=204,
    operation_id="comments_delete",
    summary="Delete a comment (its author or the post's author)",
    responses=_AUTH | _NOT_FOUND | {403: {"description": "Not allowed to delete"}},
)
def delete_comment(comment_id: uuid.UUID, user: CurrentUser, db: DbSession) -> Response:
    service.delete_comment(db, user, comment_id)
    return Response(status_code=204)

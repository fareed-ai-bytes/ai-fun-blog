import uuid
from typing import Annotated

from fastapi import APIRouter, Query, Response

from app.core.pagination import Page
from app.core.params import PageNumber
from app.modules.auth.dependencies import CurrentUser, DbSession, OptionalUser
from app.modules.posts import service
from app.modules.posts.models import PostStatus
from app.modules.posts.schemas import PostCreate, PostDetail, PostSummary, PostUpdate
from app.modules.posts.service import PostPage

router = APIRouter(tags=["posts"])

_NOT_FOUND = {404: {"description": "Post not found or not visible to you"}}
_AUTH = {401: {"description": "Not logged in"}}
_OWNER = {403: {"description": "Not the author of this post"}}


def _page(result: PostPage) -> Page[PostSummary]:
    return Page[PostSummary](
        items=[PostSummary.from_row(row) for row in result.rows],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


@router.post(
    "/posts",
    response_model=PostDetail,
    status_code=201,
    operation_id="posts_create",
    summary="Create a post (draft by default)",
    responses=_AUTH,
)
def create_post(body: PostCreate, user: CurrentUser, db: DbSession) -> PostDetail:
    view = service.create_post(
        db, user, title=body.title, body_md=body.body_md, status=PostStatus(body.status)
    )
    return PostDetail.from_view(view)


@router.patch(
    "/posts/{post_id}",
    response_model=PostDetail,
    status_code=200,
    operation_id="posts_update",
    summary="Edit, publish or unpublish your post",
    responses=_AUTH | _OWNER | _NOT_FOUND,
)
def update_post(
    post_id: uuid.UUID, body: PostUpdate, user: CurrentUser, db: DbSession
) -> PostDetail:
    view = service.update_post(db, user, post_id, body.model_dump(exclude_unset=True))
    return PostDetail.from_view(view)


@router.delete(
    "/posts/{post_id}",
    status_code=204,
    operation_id="posts_delete",
    summary="Delete your post (and its likes and comments)",
    responses=_AUTH | _OWNER | _NOT_FOUND,
)
def delete_post(post_id: uuid.UUID, user: CurrentUser, db: DbSession) -> Response:
    service.delete_post(db, user, post_id)
    return Response(status_code=204)


@router.get(
    "/me/posts",
    response_model=Page[PostSummary],
    status_code=200,
    operation_id="me_posts_list",
    summary="Your posts, drafts included, most recently updated first",
    responses=_AUTH,
)
def list_my_posts(user: CurrentUser, db: DbSession, page: PageNumber = 1) -> Page[PostSummary]:
    return _page(service.list_my_posts(db, user, page))


@router.get(
    "/posts",
    response_model=Page[PostSummary],
    status_code=200,
    operation_id="posts_list",
    summary="Public feed of published posts, newest first",
)
def list_feed(
    db: DbSession,
    page: PageNumber = 1,
    author: Annotated[str | None, Query(max_length=30, description="Author username")] = None,
) -> Page[PostSummary]:
    return _page(service.list_feed(db, page, author.lower() if author else None))


@router.get(
    "/posts/{slug}",
    response_model=PostDetail,
    status_code=200,
    operation_id="posts_get",
    summary="Read a post (drafts only by their author)",
    responses=_NOT_FOUND,
)
def get_post(slug: str, viewer: OptionalUser, db: DbSession) -> PostDetail:
    return PostDetail.from_view(service.get_post_by_slug(db, slug, viewer))

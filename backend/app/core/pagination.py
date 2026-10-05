"""v1 offset pagination: Page<T> = {items, page, page_size, total}. No FastAPI imports
here (services use it); the query-parameter type lives in core/params.py."""

from pydantic import BaseModel

POSTS_PAGE_SIZE = 10  # BR-13
COMMENTS_PAGE_SIZE = 20  # BR-13


class Page[T](BaseModel):
    items: list[T]
    page: int
    page_size: int
    total: int


def offset_for(page: int, page_size: int) -> int:
    return (page - 1) * page_size

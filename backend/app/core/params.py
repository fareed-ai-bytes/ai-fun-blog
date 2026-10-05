"""Reusable FastAPI query-parameter types for routers."""

from typing import Annotated

from fastapi import Query

PageNumber = Annotated[int, Query(ge=1, le=100_000, description="1-based page number")]

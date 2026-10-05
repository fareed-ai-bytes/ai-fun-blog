"""Auth dependencies shared by every router: get_current_user (401) / get_optional_user."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyCookie
from sqlalchemy.orm import Session

from app.core.errors import Unauthorized
from app.core.security import ACCESS_COOKIE_NAME
from app.db.session import get_db
from app.modules.auth import service
from app.modules.users.models import User

# Declared as a security scheme so OpenAPI shows which routes need the session cookie.
cookie_scheme = APIKeyCookie(name=ACCESS_COOKIE_NAME, auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def get_optional_user(
    db: DbSession, token: Annotated[str | None, Depends(cookie_scheme)]
) -> User | None:
    return service.user_from_token(db, token)


def get_current_user(user: Annotated[User | None, Depends(get_optional_user)]) -> User:
    if user is None:
        raise Unauthorized("NOT_AUTHENTICATED", "Log in to continue")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]

from fastapi import APIRouter, Response

from app.core.config import get_settings
from app.core.security import ACCESS_COOKIE_NAME
from app.modules.auth import service
from app.modules.auth.dependencies import CurrentUser, DbSession
from app.modules.auth.schemas import LoginRequest, Me, RegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        ACCESS_COOKIE_NAME,
        token,
        max_age=settings.jwt_expire_minutes * 60,
        path="/",
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )


@router.post(
    "/register",
    response_model=Me,
    status_code=201,
    operation_id="auth_register",
    summary="Create an account and log in",
    responses={409: {"description": "Email or username taken"}},
)
def register(body: RegisterRequest, response: Response, db: DbSession) -> Me:
    user = service.register(db, **body.model_dump())
    _set_session_cookie(response, service.issue_token(user))
    return Me.model_validate(user)


@router.post(
    "/login",
    response_model=Me,
    status_code=200,
    operation_id="auth_login",
    summary="Log in with email and password",
    responses={401: {"description": "Invalid email or password"}},
)
def login(body: LoginRequest, response: Response, db: DbSession) -> Me:
    user = service.authenticate(db, email=body.email, password=body.password)
    _set_session_cookie(response, service.issue_token(user))
    return Me.model_validate(user)


@router.post(
    "/logout",
    status_code=204,
    operation_id="auth_logout",
    summary="Log out (clears the session cookie)",
    responses={401: {"description": "Not logged in"}},
)
def logout(_user: CurrentUser) -> Response:
    response = Response(status_code=204)
    response.delete_cookie(
        ACCESS_COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="lax",
        secure=get_settings().cookie_secure,
    )
    return response


@router.get(
    "/me",
    response_model=Me,
    status_code=200,
    operation_id="auth_me",
    summary="Current user",
    responses={401: {"description": "Not logged in"}},
)
def me(user: CurrentUser) -> Me:
    return Me.model_validate(user)

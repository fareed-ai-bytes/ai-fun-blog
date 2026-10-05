"""FR-01 register, FR-02 login/logout/me, BR-11, BR-12."""

from datetime import UTC, datetime, timedelta

import jwt
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import ACCESS_COOKIE_NAME, JWT_ALGORITHM
from app.modules.users.models import User
from tests.factories import DEFAULT_PASSWORD, make_user

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
LOGOUT = "/api/v1/auth/logout"
ME = "/api/v1/auth/me"


def _payload(**overrides):
    body = {
        "email": "ada@example.com",
        "username": "ada",
        "display_name": "Ada Lovelace",
        "password": "analytical-engine",
    }
    return body | overrides


# --- FR-01 register -----------------------------------------------------------------


def test_fr01_register_returns_201_me_and_sets_session_cookie(client):
    response = client.post(REGISTER, json=_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "ada@example.com"
    assert body["username"] == "ada"
    assert set(body) == {"id", "email", "username", "display_name"}  # never a password hash
    set_cookie = response.headers["set-cookie"].lower()
    assert ACCESS_COOKIE_NAME in set_cookie
    assert "httponly" in set_cookie
    assert "samesite=lax" in set_cookie


def test_fr01_registered_user_is_logged_in(client):
    client.post(REGISTER, json=_payload())
    assert client.get(ME).json()["username"] == "ada"


def test_fr01_password_is_stored_hashed(client, db):
    client.post(REGISTER, json=_payload())
    user = db.scalar(select(User).where(User.username == "ada"))
    assert user.password_hash != "analytical-engine"
    assert user.password_hash.startswith("$argon2id$")


def test_fr01_duplicate_email_returns_409(client, db):
    make_user(db, "existing", email="ada@example.com")
    response = client.post(REGISTER, json=_payload())
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EMAIL_TAKEN"


def test_fr01_duplicate_username_returns_409(client, db):
    make_user(db, "ada")
    response = client.post(REGISTER, json=_payload(email="other@example.com"))
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "USERNAME_TAKEN"


def test_fr01_short_password_returns_422(client):
    response = client.post(REGISTER, json=_payload(password="short"))
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"][0]["field"] == "password"


def test_fr01_invalid_username_returns_422(client):
    for username in ["ab", "has space", "dash-ed", "x" * 31]:
        response = client.post(REGISTER, json=_payload(username=username))
        assert response.status_code == 422, username


def test_fr01_invalid_email_returns_422(client):
    response = client.post(REGISTER, json=_payload(email="not-an-email"))
    assert response.status_code == 422


def test_fr01_unknown_field_returns_422(client):
    response = client.post(REGISTER, json=_payload(is_admin=True))
    assert response.status_code == 422


# --- BR-11 email/username normalisation ---------------------------------------------


def test_br11_email_stored_lowercased(client):
    response = client.post(REGISTER, json=_payload(email="Ada@Example.COM"))
    assert response.json()["email"] == "ada@example.com"


def test_br11_email_duplicate_is_case_insensitive(client):
    client.post(REGISTER, json=_payload(email="Fareed@X.com", username="fareed"))
    response = client.post(REGISTER, json=_payload(email="fareed@x.com", username="fareed2"))
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EMAIL_TAKEN"


def test_br11_username_is_lowercased(client):
    response = client.post(REGISTER, json=_payload(username="Ada_99"))
    assert response.status_code == 201
    assert response.json()["username"] == "ada_99"


# --- FR-02 login / logout / me ------------------------------------------------------


def test_fr02_login_with_correct_credentials_returns_200_and_cookie(client, db):
    make_user(db, "grace", email="grace@example.com")
    response = client.post(LOGIN, json={"email": "Grace@Example.com", "password": DEFAULT_PASSWORD})
    assert response.status_code == 200
    assert response.json()["username"] == "grace"
    assert ACCESS_COOKIE_NAME in response.headers["set-cookie"]
    assert client.get(ME).status_code == 200


def test_br12_wrong_password_and_unknown_email_give_same_401(client, db):
    make_user(db, "grace", email="grace@example.com")
    wrong_password = client.post(LOGIN, json={"email": "grace@example.com", "password": "nope"})
    unknown_email = client.post(LOGIN, json={"email": "who@example.com", "password": "nope"})
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()
    assert wrong_password.json()["error"]["message"] == "Invalid email or password"


def test_fr02_login_missing_fields_returns_422(client):
    assert client.post(LOGIN, json={"email": "a@b.co"}).status_code == 422


def test_fr02_logout_returns_204_clears_cookie_and_me_is_401(client):
    client.post(REGISTER, json=_payload())
    response = client.post(LOGOUT)
    assert response.status_code == 204
    assert f'{ACCESS_COOKIE_NAME}=""' in response.headers["set-cookie"]
    assert client.get(ME).status_code == 401


def test_fr02_logout_when_anonymous_returns_401(client):
    assert client.post(LOGOUT).status_code == 401


def test_fr02_me_returns_current_user_with_email(auth_client, db):
    user = make_user(db, "linus", email="linus@example.com")
    body = auth_client(user).get(ME).json()
    assert body == {
        "id": str(user.id),
        "email": "linus@example.com",
        "username": "linus",
        "display_name": user.display_name,
    }


def test_fr02_me_anonymous_returns_401_envelope(client):
    response = client.get(ME)
    assert response.status_code == 401
    assert response.json() == {
        "error": {"code": "NOT_AUTHENTICATED", "message": "Log in to continue", "details": None}
    }


def test_fr02_me_with_tampered_or_expired_token_returns_401(client, db):
    user = make_user(db)
    secret = get_settings().jwt_secret.get_secret_value()
    now = datetime.now(UTC)
    expired = jwt.encode(
        {"sub": str(user.id), "iat": now - timedelta(days=2), "exp": now - timedelta(days=1)},
        secret,
        algorithm=JWT_ALGORITHM,
    )
    forged = jwt.encode(
        {"sub": str(user.id), "iat": now, "exp": now + timedelta(hours=1)},
        "not-the-real-secret-but-long-enough-0123",
        algorithm=JWT_ALGORITHM,
    )
    unsigned = jwt.encode(
        {"sub": str(user.id), "iat": now, "exp": now + timedelta(hours=1)}, None, algorithm="none"
    )
    for token in (expired, forged, unsigned, "garbage"):
        client.cookies.set(ACCESS_COOKIE_NAME, token)
        assert client.get(ME).status_code == 401, token


def test_unknown_route_returns_404_envelope(client):
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"

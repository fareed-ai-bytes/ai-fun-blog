"""FR-10 like/unlike; BR-03, BR-04, BR-05."""

import uuid

from app.modules.posts.models import PostStatus
from tests.factories import make_post, make_user


def _like_url(post_id: uuid.UUID) -> str:
    return f"/api/v1/posts/{post_id}/like"


def test_fr10_like_returns_count_and_liked_by_me(auth_client, db):
    post = make_post(db, make_user(db))
    response = auth_client(make_user(db)).put(_like_url(post.id))
    assert response.status_code == 200
    assert response.json() == {"like_count": 1, "liked_by_me": True}


def test_br04_repeat_like_leaves_count_unchanged(auth_client, db):
    post = make_post(db, make_user(db))
    reader = auth_client(make_user(db))
    reader.put(_like_url(post.id))
    assert reader.put(_like_url(post.id)).json() == {"like_count": 1, "liked_by_me": True}


def test_br04_likes_from_different_users_add_up(auth_client, db):
    post = make_post(db, make_user(db))
    auth_client(make_user(db)).put(_like_url(post.id))
    assert auth_client(make_user(db)).put(_like_url(post.id)).json()["like_count"] == 2


def test_fr10_unlike_reverses_and_is_idempotent(auth_client, db):
    post = make_post(db, make_user(db))
    reader = auth_client(make_user(db))
    reader.put(_like_url(post.id))
    first = reader.delete(_like_url(post.id))
    second = reader.delete(_like_url(post.id))
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json() == {"like_count": 0, "liked_by_me": False}


def test_br03_cannot_like_own_post(auth_client, db):
    author = make_user(db)
    post = make_post(db, author)
    response = auth_client(author).put(_like_url(post.id))
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "CANNOT_LIKE_OWN_POST"


def test_br05_cannot_like_draft_404(auth_client, db):
    author = make_user(db)
    draft = make_post(db, author, status=PostStatus.DRAFT)
    assert auth_client(make_user(db)).put(_like_url(draft.id)).status_code == 404
    assert auth_client(author).put(_like_url(draft.id)).status_code == 404


def test_fr10_like_missing_post_404(auth_client, db):
    assert auth_client(make_user(db)).put(_like_url(uuid.uuid4())).status_code == 404


def test_fr10_like_anonymous_401(client, db):
    post = make_post(db, make_user(db))
    assert client.put(_like_url(post.id)).status_code == 401
    assert client.delete(_like_url(post.id)).status_code == 401


def test_fr10_invalid_post_id_422(auth_client, db):
    assert auth_client(make_user(db)).put("/api/v1/posts/not-a-uuid/like").status_code == 422

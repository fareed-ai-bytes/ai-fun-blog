"""FR-11 create, FR-12 list, FR-13 delete; BR-05, BR-06, BR-07, BR-09, BR-13."""

import uuid

from app.modules.posts.models import PostStatus
from tests.factories import make_comment, make_post, make_user


def _comments_url(post_id: uuid.UUID) -> str:
    return f"/api/v1/posts/{post_id}/comments"


def _comment_url(comment_id: uuid.UUID) -> str:
    return f"/api/v1/comments/{comment_id}"


# --- FR-11 create -------------------------------------------------------------------


def test_fr11_comment_on_published_post_returns_201(auth_client, db):
    post = make_post(db, make_user(db))
    reader = make_user(db, "reader")
    response = auth_client(reader).post(_comments_url(post.id), json={"body": "  Great read!  "})
    assert response.status_code == 201
    body = response.json()
    assert body["body"] == "Great read!"
    assert body["author"] == {"username": "reader", "display_name": reader.display_name}
    assert body["can_delete"] is True


def test_fr11_comment_validation_422(auth_client, db):
    post = make_post(db, make_user(db))
    reader = auth_client(make_user(db))
    for body in ["", "   ", "x" * 2001]:
        assert reader.post(_comments_url(post.id), json={"body": body}).status_code == 422
    assert reader.post(_comments_url(post.id), json={"body": "x" * 2000}).status_code == 201


def test_br05_comment_on_draft_404(auth_client, db):
    author = make_user(db)
    draft = make_post(db, author, status=PostStatus.DRAFT)
    assert (
        auth_client(make_user(db)).post(_comments_url(draft.id), json={"body": "hi"}).status_code
        == 404
    )
    assert auth_client(author).post(_comments_url(draft.id), json={"body": "hi"}).status_code == 404


def test_fr11_comment_anonymous_401(client, db):
    post = make_post(db, make_user(db))
    assert client.post(_comments_url(post.id), json={"body": "hi"}).status_code == 401


def test_br06_author_may_comment_on_own_post(auth_client, db):
    author = make_user(db)
    post = make_post(db, author)
    assert (
        auth_client(author).post(_comments_url(post.id), json={"body": "Thanks"}).status_code == 201
    )


# --- FR-12 / BR-13 list -------------------------------------------------------------


def test_fr12_anonymous_lists_comments_oldest_first(client, db):
    post = make_post(db, make_user(db))
    reader = make_user(db)
    first = make_comment(db, reader, post, body="first")
    second = make_comment(db, reader, post, body="second")
    response = client.get(_comments_url(post.id))
    assert response.status_code == 200
    body = response.json()
    assert [item["id"] for item in body["items"]] == [str(first.id), str(second.id)]
    assert body["page_size"] == 20
    assert all(item["can_delete"] is False for item in body["items"])
    assert all(set(item["author"]) == {"username", "display_name"} for item in body["items"])


def test_br13_comments_paginated_twenty_per_page(client, db):
    post = make_post(db, make_user(db))
    reader = make_user(db)
    for n in range(23):
        make_comment(db, reader, post, body=f"c{n}")
    first = client.get(_comments_url(post.id)).json()
    second = client.get(_comments_url(post.id), params={"page": 2}).json()
    assert (first["total"], len(first["items"]), len(second["items"])) == (23, 20, 3)
    assert second["items"][-1]["body"] == "c22"


def test_br09_comments_of_unpublished_post_hidden_except_from_author(client, auth_client, db):
    author = make_user(db)
    draft = make_post(db, author, status=PostStatus.DRAFT)
    assert client.get(_comments_url(draft.id)).status_code == 404
    assert auth_client(make_user(db)).get(_comments_url(draft.id)).status_code == 404
    assert auth_client(author).get(_comments_url(draft.id)).status_code == 200


def test_fr12_missing_post_404(client):
    assert client.get(_comments_url(uuid.uuid4())).status_code == 404


def test_fr12_can_delete_per_viewer(auth_client, db):
    post_author, commenter, other = make_user(db), make_user(db), make_user(db)
    post = make_post(db, post_author)
    make_comment(db, commenter, post)
    for viewer, expected in [(post_author, True), (commenter, True), (other, False)]:
        items = auth_client(viewer).get(_comments_url(post.id)).json()["items"]
        assert items[0]["can_delete"] is expected


def test_fr12_comments_query_count_constant(client, db, count_queries):
    post = make_post(db, make_user(db))
    make_comment(db, make_user(db), post)
    with count_queries() as one:
        client.get(_comments_url(post.id))
    for _ in range(19):
        make_comment(db, make_user(db), post)
    with count_queries() as twenty:
        client.get(_comments_url(post.id))
    assert twenty.count == one.count


# --- FR-13 / BR-07 delete -----------------------------------------------------------


def test_br07_comment_author_can_delete(auth_client, db):
    commenter = make_user(db)
    comment = make_comment(db, commenter, make_post(db, make_user(db)))
    assert auth_client(commenter).delete(_comment_url(comment.id)).status_code == 204


def test_br07_post_author_can_delete_others_comment(auth_client, db):
    post_author = make_user(db)
    comment = make_comment(db, make_user(db), make_post(db, post_author))
    assert auth_client(post_author).delete(_comment_url(comment.id)).status_code == 204


def test_br07_anyone_else_gets_403(auth_client, db):
    comment = make_comment(db, make_user(db), make_post(db, make_user(db)))
    response = auth_client(make_user(db)).delete(_comment_url(comment.id))
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "NOT_ALLOWED_TO_DELETE_COMMENT"


def test_fr13_delete_anonymous_401_and_missing_404(client, auth_client, db):
    comment = make_comment(db, make_user(db), make_post(db, make_user(db)))
    assert client.delete(_comment_url(comment.id)).status_code == 401
    assert auth_client(make_user(db)).delete(_comment_url(uuid.uuid4())).status_code == 404


def test_fr13_deleted_comment_disappears_from_list(auth_client, client, db):
    commenter = make_user(db)
    post = make_post(db, make_user(db))
    comment = make_comment(db, commenter, post)
    auth_client(commenter).delete(_comment_url(comment.id))
    assert client.get(_comments_url(post.id)).json()["total"] == 0

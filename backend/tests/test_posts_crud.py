"""FR-05 create, FR-06 edit, FR-08 delete, FR-09 my posts; BR-02, BR-10, BR-14, BR-15."""

import uuid

from sqlalchemy import func, select

from app.modules.comments.models import Comment
from app.modules.likes.models import Like
from app.modules.posts.models import PostStatus
from app.modules.posts.text import make_excerpt, next_free_slug, slugify
from tests.factories import make_comment, make_like, make_post, make_user

POSTS = "/api/v1/posts"
MY_POSTS = "/api/v1/me/posts"


# --- FR-05 create -------------------------------------------------------------------


def test_fr05_create_post_defaults_to_draft_owned_by_current_user(auth_client, db):
    author = make_user(db, "writer")
    response = auth_client(author).post(POSTS, json={"title": "Hello World", "body_md": "Hi"})
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "draft"
    assert body["published_at"] is None
    assert body["author"] == {"username": "writer", "display_name": author.display_name}
    assert body["slug"] == "hello-world"
    assert body["is_owner"] is True
    assert body["liked_by_me"] is False
    assert body["like_count"] == body["comment_count"] == 0


def test_fr05_create_published_post_sets_published_at(auth_client, db):
    author = make_user(db)
    body = (
        auth_client(author)
        .post(POSTS, json={"title": "Live", "body_md": "Now", "status": "published"})
        .json()
    )
    assert body["status"] == "published"
    assert body["published_at"] is not None


def test_fr05_create_post_anonymous_returns_401(client):
    assert client.post(POSTS, json={"title": "T", "body_md": "B"}).status_code == 401


def test_fr05_create_post_validation_returns_422(auth_client, db):
    writer = auth_client(make_user(db))
    assert writer.post(POSTS, json={"title": "", "body_md": "B"}).status_code == 422
    assert writer.post(POSTS, json={"title": "   ", "body_md": "B"}).status_code == 422
    assert writer.post(POSTS, json={"title": "T", "body_md": "  \n "}).status_code == 422
    assert writer.post(POSTS, json={"title": "x" * 201, "body_md": "B"}).status_code == 422
    assert writer.post(POSTS, json={"title": "T", "body_md": "x" * 50_001}).status_code == 422
    assert (
        writer.post(POSTS, json={"title": "T", "body_md": "B", "status": "live"}).status_code == 422
    )


def test_fr05_client_cannot_set_author_or_slug(auth_client, db):
    writer = auth_client(make_user(db))
    response = writer.post(POSTS, json={"title": "T", "body_md": "B", "slug": "mine"})
    assert response.status_code == 422


# --- BR-10 slugs --------------------------------------------------------------------


def test_br10_slug_collisions_get_numeric_suffix(auth_client, db):
    writer = auth_client(make_user(db))
    slugs = [
        writer.post(POSTS, json={"title": "Hello World", "body_md": "B"}).json()["slug"]
        for _ in range(3)
    ]
    assert slugs == ["hello-world", "hello-world-2", "hello-world-3"]


def test_br10_slug_never_changes_when_title_changes(auth_client, db):
    writer = auth_client(make_user(db))
    post = writer.post(POSTS, json={"title": "First Title", "body_md": "B"}).json()
    updated = writer.patch(f"{POSTS}/{post['id']}", json={"title": "Second Title"}).json()
    assert updated["title"] == "Second Title"
    assert updated["slug"] == "first-title"


def test_br10_slugify_unit():
    assert slugify("Hello, World!") == "hello-world"
    assert slugify("  Café   Crème  ") == "cafe-creme"
    assert slugify("!!!") == "post"
    assert len(slugify("word " * 100)) <= 200
    assert next_free_slug("a", {"a", "a-2"}) == "a-3"
    assert next_free_slug("a", {"a-2"}) == "a"


# --- BR-14 excerpt ------------------------------------------------------------------


def test_br14_excerpt_strips_markdown():
    body = "# Title\n\nSome **bold** and _italic_ text with a [link](http://x.y) and `code`.\n"
    assert make_excerpt(body) == "Title Some bold and italic text with a link and code."


def test_br14_excerpt_cut_at_word_boundary_within_280_chars():
    body = ("word " * 100).strip()
    excerpt = make_excerpt(body)
    assert len(excerpt) <= 280
    assert excerpt.endswith("word")
    assert not excerpt.endswith(" ")


def test_br14_excerpt_recomputed_when_body_changes(auth_client, db):
    writer = auth_client(make_user(db))
    post = writer.post(POSTS, json={"title": "T", "body_md": "Old body"}).json()
    updated = writer.patch(f"{POSTS}/{post['id']}", json={"body_md": "**New** body"}).json()
    assert updated["excerpt"] == "New body"
    assert updated["body_md"] == "**New** body"


# --- FR-06 / BR-02 edit -------------------------------------------------------------


def test_fr06_author_can_edit_own_post(auth_client, db):
    author = make_user(db)
    post = make_post(db, author)
    response = auth_client(author).patch(f"{POSTS}/{post.id}", json={"title": "Edited"})
    assert response.status_code == 200
    assert response.json()["title"] == "Edited"


def test_br02_other_user_cannot_edit_published_post_403(auth_client, db):
    post = make_post(db, make_user(db))
    response = auth_client(make_user(db)).patch(f"{POSTS}/{post.id}", json={"title": "Hacked"})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "NOT_POST_OWNER"


def test_br01_other_user_editing_a_draft_gets_404_not_403(auth_client, db):
    draft = make_post(db, make_user(db), status=PostStatus.DRAFT)
    response = auth_client(make_user(db)).patch(f"{POSTS}/{draft.id}", json={"title": "X"})
    assert response.status_code == 404


def test_fr06_edit_anonymous_returns_401(client, db):
    post = make_post(db, make_user(db))
    assert client.patch(f"{POSTS}/{post.id}", json={"title": "X"}).status_code == 401


def test_fr06_edit_validation_returns_422(auth_client, db):
    author = make_user(db)
    post = make_post(db, author)
    writer = auth_client(author)
    assert writer.patch(f"{POSTS}/{post.id}", json={}).status_code == 422
    assert writer.patch(f"{POSTS}/{post.id}", json={"title": None}).status_code == 422
    assert writer.patch(f"{POSTS}/{post.id}", json={"title": ""}).status_code == 422


def test_fr06_edit_missing_post_returns_404(auth_client, db):
    response = auth_client(make_user(db)).patch(f"{POSTS}/{uuid.uuid4()}", json={"title": "X"})
    assert response.status_code == 404


# --- FR-08 / BR-15 delete -----------------------------------------------------------


def test_fr08_br15_author_delete_removes_post_likes_and_comments(auth_client, db):
    author, reader = make_user(db), make_user(db)
    post = make_post(db, author)
    make_like(db, reader, post)
    make_comment(db, reader, post)
    response = auth_client(author).delete(f"{POSTS}/{post.id}")
    assert response.status_code == 204
    assert db.scalar(select(func.count()).select_from(Like)) == 0
    assert db.scalar(select(func.count()).select_from(Comment)) == 0


def test_fr08_other_user_cannot_delete_403(auth_client, db):
    post = make_post(db, make_user(db))
    assert auth_client(make_user(db)).delete(f"{POSTS}/{post.id}").status_code == 403


def test_fr08_delete_anonymous_401_and_missing_404(client, auth_client, db):
    post = make_post(db, make_user(db))
    assert client.delete(f"{POSTS}/{post.id}").status_code == 401
    assert auth_client(make_user(db)).delete(f"{POSTS}/{uuid.uuid4()}").status_code == 404


# --- FR-09 my posts -----------------------------------------------------------------


def test_fr09_my_posts_includes_drafts_newest_update_first_and_only_mine(auth_client, db):
    me, other = make_user(db), make_user(db)
    old = make_post(db, me, title="Old")
    draft = make_post(db, me, title="Draft", status=PostStatus.DRAFT)
    make_post(db, other, title="Not mine")
    old.title = "Old, edited later"  # bumps updated_at
    db.flush()
    body = auth_client(me).get(MY_POSTS).json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["page_size"] == 10
    assert [item["id"] for item in body["items"]] == [str(old.id), str(draft.id)]
    assert {item["status"] for item in body["items"]} == {"published", "draft"}
    assert all("body_md" not in item for item in body["items"])


def test_fr09_my_posts_anonymous_returns_401(client):
    assert client.get(MY_POSTS).status_code == 401


def test_fr09_my_posts_query_count_is_constant(auth_client, db, count_queries):
    me = make_user(db)
    reader = make_user(db)
    writer = auth_client(me)
    make_post(db, me)
    with count_queries() as one_post:
        writer.get(MY_POSTS)
    for _ in range(9):
        make_like(db, reader, make_post(db, me))
    with count_queries() as ten_posts:
        writer.get(MY_POSTS)
    assert ten_posts.count == one_post.count

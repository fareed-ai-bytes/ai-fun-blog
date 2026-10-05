"""FR-03 feed, FR-04 read, FR-07 publish/unpublish, FR-14 author page;
BR-01, BR-08, BR-09, BR-13."""

from datetime import UTC, datetime, timedelta

from app.modules.posts.models import PostStatus
from tests.factories import make_comment, make_like, make_post, make_user

POSTS = "/api/v1/posts"
SUMMARY_FIELDS = {
    "id",
    "slug",
    "title",
    "excerpt",
    "status",
    "author",
    "published_at",
    "updated_at",
    "like_count",
    "comment_count",
}


def _at(days_ago: int) -> datetime:
    return datetime.now(UTC) - timedelta(days=days_ago)


# --- FR-03 / BR-13 feed -------------------------------------------------------------


def test_fr03_anonymous_feed_lists_only_published_posts(client, db):
    author = make_user(db)
    published = make_post(db, author)
    make_post(db, author, status=PostStatus.DRAFT)
    body = client.get(POSTS).json()
    assert body["total"] == 1
    assert [item["id"] for item in body["items"]] == [str(published.id)]


def test_fr03_feed_items_have_summary_fields_and_counts(client, db):
    author, reader = make_user(db), make_user(db)
    post = make_post(db, author)
    make_like(db, reader, post)
    make_comment(db, reader, post)
    make_comment(db, author, post)
    item = client.get(POSTS).json()["items"][0]
    assert set(item) == SUMMARY_FIELDS  # no body_md in the feed
    assert item["like_count"] == 1
    assert item["comment_count"] == 2
    assert set(item["author"]) == {"username", "display_name"}  # never email


def test_br13_feed_ordered_by_published_at_desc_then_id(client, db):
    author = make_user(db)
    oldest = make_post(db, author, published_at=_at(3))
    newest = make_post(db, author, published_at=_at(1))
    tie_a = make_post(db, author, published_at=_at(2))
    tie_b = make_post(db, author, published_at=tie_a.published_at)
    ties = sorted([str(tie_a.id), str(tie_b.id)], reverse=True)
    ids = [item["id"] for item in client.get(POSTS).json()["items"]]
    assert ids == [str(newest.id), *ties, str(oldest.id)]


def test_br13_feed_pages_of_ten(client, db):
    author = make_user(db)
    for days in range(12):
        make_post(db, author, published_at=_at(days))
    first = client.get(POSTS).json()
    second = client.get(POSTS, params={"page": 2}).json()
    assert (first["total"], first["page_size"], len(first["items"])) == (12, 10, 10)
    assert len(second["items"]) == 2
    assert not {i["id"] for i in first["items"]} & {i["id"] for i in second["items"]}


def test_fr03_invalid_page_returns_422(client):
    assert client.get(POSTS, params={"page": 0}).status_code == 422


def test_fr03_feed_query_count_constant_regardless_of_page_size(client, db, count_queries):
    author, reader = make_user(db), make_user(db)
    make_post(db, author)
    with count_queries() as one_post:
        client.get(POSTS)
    for _ in range(9):
        post = make_post(db, author)
        make_like(db, reader, post)
        make_comment(db, reader, post)
    with count_queries() as ten_posts:
        client.get(POSTS)
    assert ten_posts.count == one_post.count <= 2


# --- FR-04 / BR-01 read -------------------------------------------------------------


def test_fr04_anonymous_reads_published_post_with_body(client, db):
    post = make_post(db, make_user(db), body_md="# Full body")
    response = client.get(f"{POSTS}/{post.slug}")
    assert response.status_code == 200
    body = response.json()
    assert body["body_md"] == "# Full body"
    assert body["liked_by_me"] is False
    assert body["is_owner"] is False


def test_br01_draft_is_404_for_anonymous_and_other_users(client, auth_client, db):
    draft = make_post(db, make_user(db), status=PostStatus.DRAFT)
    assert client.get(f"{POSTS}/{draft.slug}").status_code == 404
    response = auth_client(make_user(db)).get(f"{POSTS}/{draft.slug}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "POST_NOT_FOUND"


def test_br01_author_can_read_own_draft(auth_client, db):
    author = make_user(db)
    draft = make_post(db, author, status=PostStatus.DRAFT)
    body = auth_client(author).get(f"{POSTS}/{draft.slug}").json()
    assert body["status"] == "draft"
    assert body["is_owner"] is True


def test_fr04_unknown_slug_returns_404(client):
    assert client.get(f"{POSTS}/no-such-post").status_code == 404


def test_fr04_liked_by_me_reflects_viewer(auth_client, db):
    author, reader = make_user(db), make_user(db)
    post = make_post(db, author)
    make_like(db, reader, post)
    assert auth_client(reader).get(f"{POSTS}/{post.slug}").json()["liked_by_me"] is True
    assert auth_client(author).get(f"{POSTS}/{post.slug}").json()["liked_by_me"] is False


# --- FR-07 / BR-08 / BR-09 publish & unpublish --------------------------------------


def test_fr07_publish_draft_makes_it_public(auth_client, client, db):
    author = make_user(db)
    draft = make_post(db, author, status=PostStatus.DRAFT)
    body = auth_client(author).patch(f"{POSTS}/{draft.id}", json={"status": "published"}).json()
    assert body["status"] == "published"
    assert body["published_at"] is not None
    assert client.get(f"{POSTS}/{draft.slug}").status_code == 200
    assert client.get(POSTS).json()["total"] == 1


def test_br08_republish_keeps_original_published_at(auth_client, db):
    author = make_user(db)
    original = _at(10)
    post = make_post(db, author, published_at=original)
    writer = auth_client(author)
    writer.patch(f"{POSTS}/{post.id}", json={"status": "draft"})
    body = writer.patch(f"{POSTS}/{post.id}", json={"status": "published"}).json()
    assert datetime.fromisoformat(body["published_at"]) == original


def test_br09_unpublish_hides_post_but_keeps_likes_and_comments(auth_client, client, db):
    author, reader = make_user(db), make_user(db)
    post = make_post(db, author)
    make_like(db, reader, post)
    make_comment(db, reader, post)
    writer = auth_client(author)
    writer.patch(f"{POSTS}/{post.id}", json={"status": "draft"})
    assert client.get(POSTS).json()["total"] == 0
    assert client.get(f"{POSTS}/{post.slug}").status_code == 404
    own_view = writer.get(f"{POSTS}/{post.slug}").json()  # author still sees it
    assert (own_view["like_count"], own_view["comment_count"]) == (1, 1)
    writer.patch(f"{POSTS}/{post.id}", json={"status": "published"})
    item = client.get(POSTS).json()["items"][0]  # counts reappear on republish
    assert (item["like_count"], item["comment_count"]) == (1, 1)


# --- FR-14 author page --------------------------------------------------------------


def test_fr14_author_filter_returns_only_that_authors_published_posts(client, db):
    alice, bob = make_user(db, "alice"), make_user(db, "bob")
    alice_post = make_post(db, alice)
    make_post(db, alice, status=PostStatus.DRAFT)
    make_post(db, bob)
    body = client.get(POSTS, params={"author": "Alice"}).json()
    assert [item["id"] for item in body["items"]] == [str(alice_post.id)]
    assert client.get(POSTS, params={"author": "nobody"}).json()["total"] == 0

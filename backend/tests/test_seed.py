"""FR-15: demo seed is realistic and idempotent."""

from sqlalchemy import func, select

from app.modules.comments.models import Comment
from app.modules.likes.models import Like
from app.modules.posts.models import Post, PostStatus
from app.modules.users.models import User
from scripts.seed import DEMO_PASSWORD, seed

LOGIN = "/api/v1/auth/login"


def _counts(db):
    return tuple(
        db.scalar(select(func.count()).select_from(model)) for model in (User, Post, Like, Comment)
    )


def test_fr15_seed_creates_users_posts_drafts_likes_and_comments(db):
    seed(db)
    users, posts, likes, comments = _counts(db)
    assert users == 3
    assert posts >= 8
    assert likes > 0
    assert comments > 0
    drafts_per_author = db.execute(
        select(Post.author_id, func.count())
        .where(Post.status == PostStatus.DRAFT)
        .group_by(Post.author_id)
    ).all()
    assert len(drafts_per_author) == 3
    assert all(count >= 1 for _author, count in drafts_per_author)


def test_fr15_seed_twice_creates_no_duplicates(db):
    seed(db)
    first = _counts(db)
    seed(db)
    assert _counts(db) == first


def test_fr15_documented_demo_logins_work(client, db):
    seed(db)
    for email in ("alice@example.com", "bob@example.com", "carol@example.com"):
        response = client.post(LOGIN, json={"email": email, "password": DEMO_PASSWORD})
        assert response.status_code == 200, email

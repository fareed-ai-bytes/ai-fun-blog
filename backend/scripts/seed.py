"""Demo data for the video and reviewers (FR-15). Idempotent: running it twice creates
nothing new. Run with `make seed`.

Logins (documented in README.md) — all share the password DEMO_PASSWORD:
  alice@example.com · bob@example.com · carol@example.com
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.modules.comments.models import Comment
from app.modules.likes.models import Like
from app.modules.posts.models import Post, PostStatus
from app.modules.posts.text import make_excerpt, slugify
from app.modules.users.models import User

logger = logging.getLogger(__name__)

DEMO_PASSWORD = "demo-password-1"  # noqa: S105 - documented demo login, not a secret


@dataclass(frozen=True)
class SeedPost:
    author: str
    title: str
    body: str
    days_ago: int | None  # None = draft


USERS = [
    ("alice", "alice@example.com", "Alice Moreno"),
    ("bob", "bob@example.com", "Bob Okafor"),
    ("carol", "carol@example.com", "Carol Lindqvist"),
]

POSTS = [
    SeedPost(
        "alice",
        "Why I Switched to Writing in Markdown",
        "For years I drafted everything in a word processor. Then I lost a chapter to a "
        "corrupted file.\n\n## What changed\n\nMarkdown is **plain text**, so it survives "
        "anything: version control, email, a phone with no apps installed.\n\n"
        "- Headings are just `#`\n- Emphasis is just `*`\n- Links stay readable\n\n"
        "> Write first, format later.\n\nIf you're on the fence, try it for one week.",
        2,
    ),
    SeedPost(
        "alice",
        "A Beginner's Guide to Sourdough Starters",
        "A starter is just flour, water and patience.\n\n1. Mix 50 g flour with 50 g water.\n"
        "2. Leave it somewhere warm.\n3. Feed it daily and discard half.\n\n"
        "By day five you should see bubbles. By day seven it should double in four hours. "
        "If it smells like nail polish, it's hungry — feed it more often.",
        9,
    ),
    SeedPost(
        "alice",
        "Notes From My First Half Marathon",
        "I finished. Slowly, but I finished.\n\n## Things I got right\n\nI trained for twelve "
        "weeks and never skipped the long run.\n\n## Things I got wrong\n\nI started too fast "
        "and paid for it at kilometre 15. Next time: negative splits.",
        20,
    ),
    SeedPost(
        "alice",
        "Draft: Ideas for a Reading Challenge",
        "Twelve books, twelve genres, one year. Still working out the list.",
        None,
    ),
    SeedPost(
        "bob",
        "Five Lessons From Ten Years of Code Review",
        "Code review is a conversation, not a gate.\n\n1. **Review the design first**, the "
        "semicolons last.\n2. Ask questions instead of issuing orders.\n3. Small pull requests "
        "get better reviews.\n4. Praise good work out loud.\n5. Automate the nitpicks.\n\n"
        "The best reviewers I've worked with made me want to ask for their review.",
        1,
    ),
    SeedPost(
        "bob",
        "Understanding Database Indexes Without the Jargon",
        "An index is a sorted copy of some columns plus a pointer back to the row.\n\n"
        "Think of the index at the back of a textbook: you don't read every page to find "
        "*photosynthesis*, you jump to the page number.\n\n```sql\nCREATE INDEX ON posts "
        "(published_at DESC);\n```\n\nIndexes speed up reads and slow down writes. Measure first.",
        6,
    ),
    SeedPost(
        "bob",
        "Draft: Thoughts on Remote Work Rituals",
        "Standups, demos, and the surprisingly important Friday call with no agenda.",
        None,
    ),
    SeedPost(
        "carol",
        "Exploring Stockholm on a Budget",
        "Stockholm has a reputation for being expensive. It doesn't have to be.\n\n"
        "## Free things worth your time\n\n- The subway stations are an art gallery\n"
        "- Walk around Djurgården at sunset\n- Bring a picnic to Monteliusvägen\n\n"
        "Buy a 72-hour transit card and you can see most of the city for the price of dinner.",
        3,
    ),
    SeedPost(
        "carol",
        "How I Organise My Week With Paper Notebooks",
        "Every Sunday I spend twenty minutes with a pen and a notebook.\n\n"
        "I write down three things that would make the week a success, then block time for "
        "them before anything else. Everything else fits around them.\n\n"
        "It's low-tech, and that's the point: no notifications.",
        13,
    ),
    SeedPost(
        "carol",
        "Draft: Houseplants That Survive Neglect",
        "Snake plant, ZZ plant, pothos. More to come.",
        None,
    ),
]

LIKES = [
    ("bob", "Why I Switched to Writing in Markdown"),
    ("carol", "Why I Switched to Writing in Markdown"),
    ("carol", "A Beginner's Guide to Sourdough Starters"),
    ("alice", "Five Lessons From Ten Years of Code Review"),
    ("carol", "Five Lessons From Ten Years of Code Review"),
    ("alice", "Understanding Database Indexes Without the Jargon"),
    ("alice", "Exploring Stockholm on a Budget"),
    ("bob", "Exploring Stockholm on a Budget"),
    ("bob", "How I Organise My Week With Paper Notebooks"),
]

COMMENTS = [
    ("bob", "Why I Switched to Writing in Markdown", "Same here — plain text saved my thesis."),
    ("alice", "Why I Switched to Writing in Markdown", "Glad it's not just me!"),
    ("carol", "A Beginner's Guide to Sourdough Starters", "Mine smelled like nail polish. Fed!"),
    ("carol", "Five Lessons From Ten Years of Code Review", "Number 4 is so underrated."),
    ("alice", "Understanding Database Indexes Without the Jargon", "The textbook analogy clicked."),
    ("bob", "Exploring Stockholm on a Budget", "Adding Monteliusvägen to my list."),
    ("alice", "How I Organise My Week With Paper Notebooks", "Three things a week — stealing it."),
]


def _seed_users(db: Session) -> dict[str, User]:
    users: dict[str, User] = {}
    password_hash: str | None = None
    for username, email, display_name in USERS:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            password_hash = password_hash or hash_password(DEMO_PASSWORD)
            user = User(
                email=email,
                username=username,
                display_name=display_name,
                password_hash=password_hash,
            )
            db.add(user)
        users[username] = user
    db.flush()
    return users


def _seed_posts(db: Session, users: dict[str, User]) -> dict[str, Post]:
    now = datetime.now(UTC)
    posts: dict[str, Post] = {}
    for spec in POSTS:
        slug = slugify(spec.title)
        post = db.scalar(select(Post).where(Post.slug == slug))
        if post is None:
            published = spec.days_ago is not None
            post = Post(
                author_id=users[spec.author].id,
                title=spec.title,
                slug=slug,
                body_md=spec.body,
                excerpt=make_excerpt(spec.body),
                status=PostStatus.PUBLISHED if published else PostStatus.DRAFT,
                published_at=now - timedelta(days=spec.days_ago) if published else None,
            )
            db.add(post)
        posts[spec.title] = post
    db.flush()
    return posts


def _seed_engagement(db: Session, users: dict[str, User], posts: dict[str, Post]) -> None:
    for username, title in LIKES:
        key = (users[username].id, posts[title].id)
        if db.get(Like, key) is None:
            db.add(Like(user_id=key[0], post_id=key[1]))
    for username, title, body in COMMENTS:
        author_id, post_id = users[username].id, posts[title].id
        exists = db.scalar(
            select(Comment.id).where(
                Comment.author_id == author_id, Comment.post_id == post_id, Comment.body == body
            )
        )
        if exists is None:
            db.add(Comment(author_id=author_id, post_id=post_id, body=body))
    db.flush()


def seed(db: Session) -> None:
    users = _seed_users(db)
    posts = _seed_posts(db, users)
    _seed_engagement(db, users, posts)
    db.commit()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    with SessionLocal() as db:
        seed(db)
    logger.info(
        "Seed complete: %d users, %d posts, %d likes, %d comments",
        len(USERS),
        len(POSTS),
        len(LIKES),
        len(COMMENTS),
    )


if __name__ == "__main__":
    main()

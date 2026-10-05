"""initial schema: users, posts, likes, comments (T-002)

Revision ID: 0001
Revises:
Create Date: 2026-10-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

post_status = postgresql.ENUM("draft", "published", name="post_status", create_type=False)


def upgrade() -> None:
    post_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("username", sa.String(30), nullable=False),
        sa.Column("display_name", sa.String(60), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.CheckConstraint("email = lower(email)", name=op.f("ck_users_email_lowercase")),
        sa.CheckConstraint("username ~ '^[a-z0-9_]{3,30}$'", name=op.f("ck_users_username_format")),
        sa.CheckConstraint(
            "char_length(display_name) BETWEEN 1 AND 60", name=op.f("ck_users_display_name_length")
        ),
    )

    op.create_table(
        "posts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(220), nullable=False),
        sa.Column("body_md", sa.Text(), nullable=False),
        sa.Column("excerpt", sa.String(280), nullable=False),
        sa.Column("status", post_status, nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_posts"),
        sa.ForeignKeyConstraint(
            ["author_id"], ["users.id"], name="fk_posts_author_id_users", ondelete="CASCADE"
        ),
        sa.UniqueConstraint("slug", name="uq_posts_slug"),
        sa.CheckConstraint(
            "char_length(title) BETWEEN 1 AND 200", name=op.f("ck_posts_title_length")
        ),
        sa.CheckConstraint(
            "char_length(body_md) BETWEEN 1 AND 50000", name=op.f("ck_posts_body_md_length")
        ),
        sa.CheckConstraint("char_length(excerpt) <= 280", name=op.f("ck_posts_excerpt_length")),
        sa.CheckConstraint(
            "status <> 'published' OR published_at IS NOT NULL",
            name=op.f("ck_posts_published_has_date"),
        ),
    )
    op.create_index(
        "ix_posts_status_published_at",
        "posts",
        ["status", sa.text("published_at DESC")],
    )
    op.create_index(
        "ix_posts_author_id_updated_at",
        "posts",
        ["author_id", sa.text("updated_at DESC")],
    )

    op.create_table(
        "likes",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("user_id", "post_id", name="pk_likes"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_likes_user_id_users", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["post_id"], ["posts.id"], name="fk_likes_post_id_posts", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_likes_post_id", "likes", ["post_id"])

    op.create_table(
        "comments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("author_id", sa.Uuid(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name="pk_comments"),
        sa.ForeignKeyConstraint(
            ["post_id"], ["posts.id"], name="fk_comments_post_id_posts", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["author_id"], ["users.id"], name="fk_comments_author_id_users", ondelete="CASCADE"
        ),
        sa.CheckConstraint(
            "char_length(body) BETWEEN 1 AND 2000", name=op.f("ck_comments_body_length")
        ),
    )
    op.create_index("ix_comments_post_id_created_at", "comments", ["post_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_comments_post_id_created_at", table_name="comments")
    op.drop_table("comments")
    op.drop_index("ix_likes_post_id", table_name="likes")
    op.drop_table("likes")
    op.drop_index("ix_posts_author_id_updated_at", table_name="posts")
    op.drop_index("ix_posts_status_published_at", table_name="posts")
    op.drop_table("posts")
    op.drop_table("users")
    post_status.drop(op.get_bind(), checkfirst=True)

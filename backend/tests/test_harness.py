"""Proves the harness itself: Postgres-backed, rolled back per test, migrations reversible."""

import pytest
from sqlalchemy import func, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from alembic import command
from app.modules.users.models import User
from tests.conftest import alembic_config
from tests.factories import make_comment, make_like, make_post, make_user


def test_factories_write_to_postgres(db: Session):
    author = make_user(db, "harness_author")
    reader = make_user(db, "harness_reader")
    post = make_post(db, author)
    make_like(db, reader, post)
    make_comment(db, reader, post)
    assert db.scalar(select(func.count()).select_from(User)) == 2


def test_each_test_starts_with_an_empty_database(db: Session):
    # The previous test's users were rolled back.
    assert db.scalar(select(func.count()).select_from(User)) == 0


def test_database_constraints_are_enforced(db: Session):
    with pytest.raises(IntegrityError):
        make_user(db, "Not Valid!")  # violates ck_users_username_format


def test_migrations_downgrade_to_base_and_upgrade_again(engine):
    config = alembic_config()
    command.downgrade(config, "base")
    assert set(inspect(engine).get_table_names()) == {"alembic_version"}
    command.upgrade(config, "head")
    assert {"users", "posts", "likes", "comments"} <= set(inspect(engine).get_table_names())

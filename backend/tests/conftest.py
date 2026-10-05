"""Test harness: real Postgres (TEST_DATABASE_URL), schema built by Alembic once per run,
every test wrapped in a transaction that is rolled back."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, event, make_url, text
from sqlalchemy.orm import Session

from alembic import command
from alembic.config import Config
from app.core.config import get_settings
from app.core.security import ACCESS_COOKIE_NAME, create_access_token
from app.db.session import get_db
from app.main import app
from app.modules.users.models import User

TEST_DATABASE_URL = get_settings().test_database_url


def _ensure_database_exists(url: str) -> None:
    target = make_url(url)
    admin = create_engine(target.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": target.database}
        )
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{target.database}"'))  # noqa: S608 - test DB name from settings
    admin.dispose()


def alembic_config(url: str = TEST_DATABASE_URL) -> Config:
    config = Config("alembic.ini")
    config.attributes["database_url"] = url
    config.attributes["configure_logger"] = False
    return config


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    _ensure_database_exists(TEST_DATABASE_URL)
    eng = create_engine(TEST_DATABASE_URL)
    with eng.begin() as conn:  # start every run from an empty schema
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public"))
    command.upgrade(alembic_config(), "head")
    yield eng
    eng.dispose()


@pytest.fixture
def db(engine: Engine) -> Iterator[Session]:
    connection = engine.connect()
    transaction = connection.begin()
    # Service-level commits become SAVEPOINT releases; the outer transaction is rolled back.
    session = Session(
        bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False
    )
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def auth_client(db: Session) -> Iterator[Callable[[User], TestClient]]:
    """`auth_client(user)` → a TestClient logged in as that user (own cookie jar per user)."""
    app.dependency_overrides[get_db] = lambda: db
    clients: list[TestClient] = []

    def make(user: User) -> TestClient:
        test_client = TestClient(app)
        test_client.cookies.set(ACCESS_COOKIE_NAME, create_access_token(user.id))
        clients.append(test_client)
        return test_client

    yield make
    for test_client in clients:
        test_client.close()
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def count_queries(engine: Engine) -> Callable[[], "QueryCounter"]:
    """`with count_queries() as counter: ...` then assert on `counter.count`."""

    @contextmanager
    def _count() -> Iterator[QueryCounter]:
        counter = QueryCounter()
        event.listen(engine, "before_cursor_execute", counter.on_execute)
        try:
            yield counter
        finally:
            event.remove(engine, "before_cursor_execute", counter.on_execute)

    return _count


class QueryCounter:
    def __init__(self) -> None:
        self.count = 0
        self.statements: list[str] = []

    def on_execute(self, _conn: object, _cursor: object, statement: str, *_args: object) -> None:
        if statement.lstrip().upper().startswith(("SAVEPOINT", "RELEASE", "ROLLBACK")):
            return
        self.count += 1
        self.statements.append(statement)

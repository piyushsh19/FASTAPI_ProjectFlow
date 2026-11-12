
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import Base
from app.db.dependencies import get_db
from app.main import app
import redis



# Safety check: never run tests against the development database.
assert "test" in settings.test_database_url.split("/")[-1], (
    "TEST_DATABASE_URL must point to a test database"
)

test_engine = create_engine(
    settings.test_database_url,
    pool_pre_ping=True,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create tables once for the entire test session."""

    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Provide an isolated database transaction for each test."""

    connection = test_engine.connect()
    transaction = connection.begin()

    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
        autoflush=False,
        autocommit=False,
    )

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session):
    """Provide a FastAPI test client using the test database."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def clean_rate_limit_counters():
    """
    Clean Redis rate-limit counters before and after
    every test to prevent test interference.
    """

    sync_redis = redis.Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )

    def clear_counters():
        keys = list(
            sync_redis.scan_iter(
                match="rate_limit:auth:*"
            )
        )

        if keys:
            sync_redis.delete(*keys)

    clear_counters()

    yield

    clear_counters()
    sync_redis.close()
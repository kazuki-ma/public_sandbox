"""Pytest configuration with testcontainers for PostgreSQL."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from config import Base
from models import User, Post, Comment, Tag


@pytest.fixture(scope="session")
def postgres_container():
    """Create a PostgreSQL container for testing."""
    with PostgresContainer("postgres:15") as postgres:
        yield postgres


@pytest.fixture(scope="function")
def db_engine(postgres_container):
    """Create a database engine for the test container."""
    engine = create_engine(
        postgres_container.get_connection_url(),
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a database session for testing."""
    # Create all tables
    Base.metadata.create_all(bind=db_engine)

    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=db_engine)


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        username="test_user",
        email="test@example.com",
        hashed_password="hashed_test_password",
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_post(db_session, sample_user):
    """Create a sample post for testing."""
    post = Post(
        title="Test Post",
        slug="test-post",
        content="This is a test post content.",
        summary="Test summary",
        author_id=sample_user.id
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post


@pytest.fixture
def sample_tag(db_session):
    """Create a sample tag for testing."""
    tag = Tag(
        name="Test Tag",
        slug="test-tag",
        description="A tag for testing"
    )
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag


@pytest.fixture
def sample_comment(db_session, sample_user, sample_post):
    """Create a sample comment for testing."""
    comment = Comment(
        content="This is a test comment.",
        author_id=sample_user.id,
        post_id=sample_post.id
    )
    db_session.add(comment)
    db_session.commit()
    db_session.refresh(comment)
    return comment
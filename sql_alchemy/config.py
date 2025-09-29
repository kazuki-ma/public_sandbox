"""Database configuration module."""

import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class DatabaseConfig:
    """Database configuration class."""

    def __init__(self, database_url: Optional[str] = None):
        """Initialize database configuration.

        Args:
            database_url: Database URL string. If not provided, will use environment variable.
        """
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "sqlite:///./sql_alchemy/test.db"
        )

        # Create engine with appropriate settings for different databases
        engine_kwargs = {}
        if "sqlite" in self.database_url:
            engine_kwargs["connect_args"] = {"check_same_thread": False}
        elif "postgresql" in self.database_url:
            engine_kwargs["pool_pre_ping"] = True
            engine_kwargs["pool_size"] = 10
            engine_kwargs["max_overflow"] = 20

        self.engine = create_engine(self.database_url, **engine_kwargs)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def get_session(self):
        """Get a new database session."""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def create_tables(self):
        """Create all tables defined in models."""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all tables."""
        Base.metadata.drop_all(bind=self.engine)


# Default configuration instance
db_config = DatabaseConfig()


def get_db():
    """Dependency for FastAPI or other frameworks to get database session."""
    return db_config.get_session()


# Example connection strings for different databases
EXAMPLE_CONNECTIONS = {
    "sqlite": "sqlite:///./sql_alchemy/test.db",
    "postgresql": "postgresql://user:password@localhost/dbname",
    "mysql": "mysql+pymysql://user:password@localhost/dbname",
    "postgresql_async": "postgresql+asyncpg://user:password@localhost/dbname",
}
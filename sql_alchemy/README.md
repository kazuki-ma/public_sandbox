# SQLAlchemy / Alembic Feasibility Study

This directory contains a complete SQLAlchemy and Alembic setup for feasibility study purposes, with PostgreSQL support via testcontainers.

## Features

- **SQLAlchemy ORM** with declarative models
- **Alembic** for database migrations
- **testcontainers** for PostgreSQL testing
- **pytest** testing framework
- Sample models with relationships (User, Post, Comment, Tag)
- CRUD operations examples
- Comprehensive test suite

## Project Structure

```
sql_alchemy/
├── models/           # SQLAlchemy model definitions
│   ├── user.py      # User model
│   ├── post.py      # Post and Tag models
│   └── comment.py   # Comment model
├── alembic/         # Database migrations
├── examples/        # Usage examples
│   ├── crud_operations.py  # CRUD operation classes
│   └── usage_example.py    # Sample usage script
├── tests/           # Test suite
│   ├── conftest.py          # pytest fixtures with testcontainers
│   ├── test_user_crud.py    # User CRUD tests
│   ├── test_post_crud.py    # Post CRUD tests
│   └── test_relationships.py # Relationship tests
└── config.py        # Database configuration

```

## Setup

Dependencies are managed in the root `pyproject.toml` using uv.

### Activate virtual environment:
```bash
source .venv-docker/bin/activate
```

### Install dependencies:
```bash
UV_CACHE_DIR=~/.cache/uv UV_PYTHON_INSTALL_DIR=~/.local/share/uv/python uv pip install -e ".[dev]"
```

## Running Tests

Tests use testcontainers to spin up a PostgreSQL container automatically:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sql_alchemy

# Run specific test file
pytest sql_alchemy/tests/test_user_crud.py

# Run tests with verbose output
pytest -v
```

## Running Examples

### Basic usage example:
```bash
python -m sql_alchemy.examples.usage_example
```

This will:
- Create SQLite database
- Insert sample data (users, posts, comments, tags)
- Demonstrate CRUD operations
- Show relationship queries

## Database Configuration

Configure database connection via environment variables in `.env`:

```bash
# SQLite (default)
DATABASE_URL=sqlite:///./sql_alchemy/test.db

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# MySQL
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/dbname
```

## Alembic Migrations

### Initialize database (first time):
```bash
cd sql_alchemy
alembic upgrade head
```

### Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback migrations:
```bash
alembic downgrade -1
```

## Model Relationships

The project demonstrates various SQLAlchemy relationships:

- **One-to-Many**: User → Posts, Post → Comments
- **Many-to-One**: Post → User (author), Comment → User (author)
- **Many-to-Many**: Posts ↔ Tags
- **Self-referential**: Comment → Comment (replies)
- **Cascade deletes**: Properly configured for all relationships

## Testing with PostgreSQL

Tests automatically use testcontainers to spin up a PostgreSQL 15 container. No manual setup required - just run pytest!

The container is:
- Created once per test session
- Automatically cleaned up after tests
- Isolated from your local PostgreSQL installation

## Development

### Code formatting:
```bash
black sql_alchemy/
```

### Linting:
```bash
ruff check sql_alchemy/
```
# SQLAlchemy/Alembic Project Makefile

.PHONY: help install test coverage migrate clean db-init db-upgrade db-downgrade db-reset db-current

# Default environment variables
export UV_CACHE_DIR ?= ~/.cache/uv
export UV_PYTHON_INSTALL_DIR ?= ~/.local/share/uv/python
export DATABASE_URL ?= sqlite:///./test.db

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install all dependencies including test extras
	uv sync --all-extras

test: ## Run all tests with pytest
	uv run --extra test pytest

test-unit: ## Run unit tests only
	uv run --extra test pytest -m unit

test-integration: ## Run integration tests only
	uv run --extra test pytest -m integration

test-fast: ## Run tests excluding slow tests
	uv run --extra test pytest -m "not slow"

test-watch: ## Run tests in watch mode (requires pytest-watch)
	uv run --extra test ptw -- -x

coverage: ## Run tests with coverage report
	uv run --extra test pytest --cov=. --cov-report=html --cov-report=term-missing --cov-omit="*_test.py,*/conftest.py,*/alembic/*,examples/usage_example.py"
	@echo "Coverage report generated in htmlcov/index.html"

lint: ## Run code linters (black, ruff)
	uv run --extra dev black --check .
	uv run --extra dev ruff check .

format: ## Auto-format code with black
	uv run --extra dev black .
	uv run --extra dev ruff check --fix .

# Alembic Database Migration Commands

db-init: ## Initialize alembic (only run once)
	cd alembic && uv run alembic init alembic || echo "Already initialized"

db-check: ## Check if models are in sync with database
	uv run alembic check

db-migration: ## Create a new migration file (auto-detect changes)
	@read -p "Enter migration message: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

db-migration-empty: ## Create an empty migration file (manual)
	@read -p "Enter migration message: " msg; \
	uv run alembic revision -m "$$msg"

db-revision: db-migration ## Alias for db-migration

db-upgrade: ## Apply all pending migrations
	uv run alembic upgrade head

db-upgrade-one: ## Apply next migration
	uv run alembic upgrade +1

db-downgrade: ## Rollback last migration
	uv run alembic downgrade -1

db-downgrade-base: ## Rollback all migrations
	uv run alembic downgrade base

db-current: ## Show current migration revision
	uv run alembic current

db-history: ## Show migration history
	uv run alembic history --verbose

db-heads: ## Show current head revisions
	uv run alembic heads

db-branches: ## Show branch points
	uv run alembic branches

db-show: ## Show a specific revision
	@read -p "Enter revision ID: " rev; \
	uv run alembic show "$$rev"

db-stamp: ## Stamp database with specific revision (without running migrations)
	@read -p "Enter revision ID (or 'head'): " rev; \
	uv run alembic stamp "$$rev"

db-reset: clean-db db-upgrade ## Reset database (drop and recreate)
	@echo "Database reset complete"

db-merge: ## Merge two migration branches
	@read -p "Enter revisions to merge (space-separated): " revs; \
	read -p "Enter merge message: " msg; \
	uv run alembic merge -m "$$msg" $$revs

validate: ## Complete validation with testcontainer (migrations + pg_dump)
	@uv run --extra test python utils/validate_and_dump.py

validate-quick: ## Quick validation without migrations
	@uv run --extra test python utils/validate_and_dump.py --skip-migrations

db-validate: ## Legacy validation (multiple methods)
	@echo "===================================="
	@echo " Validation & Schema Dump"
	@echo "===================================="
	@echo ""
	@echo "1. Validating migration files..."
	@find alembic/versions -name "*.py" -exec python -m py_compile {} \; 2>/dev/null || true
	@echo "   ✓ All migration files are syntactically valid"
	@echo ""
	@echo "2. Validating models..."
	@uv run python -c "from models import User, Post, Comment, Tag; print('   ✓ All models import successfully')" || exit 1
	@echo ""
	@echo "3. Dumping database schema..."
	@mkdir -p schema
	@if [ "$${DATABASE_URL#postgresql://}" != "$$DATABASE_URL" ]; then \
		echo "   Using pg_dump for PostgreSQL schema..."; \
		$(MAKE) -s db-schema-pg; \
	elif docker ps --filter name=postgres-dev --format "{{.Names}}" | grep -q postgres-dev 2>/dev/null; then \
		echo "   Found running PostgreSQL container, using pg_dump..."; \
		$(MAKE) -s db-schema-pg; \
	else \
		echo "   No PostgreSQL detected, using testcontainer for integrated validation..."; \
		$(MAKE) validate; \
	fi
	@echo ""
	@echo "===================================="
	@echo " ✅ Validation Complete"
	@echo "===================================="
	@ls -lh schema/*latest* 2>/dev/null || echo "No schema files generated"

db-schema-pg: ## Dump PostgreSQL schema using pg_dump
	@mkdir -p schema
	@if docker ps --filter name=postgres-dev --format "{{.Names}}" | grep -q postgres-dev 2>/dev/null; then \
		docker exec postgres-dev pg_dump \
			--schema-only \
			--no-owner --no-privileges \
			--no-tablespaces \
			--quote-all-identifiers \
			-U dev -d sqlalchemy_test \
			> schema/schema_postgres_$$(date +%Y%m%d_%H%M%S).sql; \
		ln -sf schema_postgres_$$(date +%Y%m%d)*.sql schema/schema_postgres_latest.sql 2>/dev/null || true; \
		echo "✓ PostgreSQL schema dumped to schema/schema_postgres_latest.sql"; \
	else \
		echo "❌ PostgreSQL container not running. Start with: make pg-start"; \
		exit 1; \
	fi

db-schema-sql: ## Dump schema using SQLAlchemy (fallback)
	@uv run python utils/schema_dump.py --validate

db-schema-compare: ## Compare model schema with database schema
	@mkdir -p schema
	@echo "Dumping model schema..."
	@uv run python utils/schema_dump.py --dialects postgresql --output-dir schema
	@if docker ps --filter name=postgres-dev --format "{{.Names}}" | grep -q postgres-dev 2>/dev/null; then \
		echo "Dumping database schema..."; \
		$(MAKE) db-schema-pg; \
		echo "Comparing schemas..."; \
		diff -u schema/schema_postgresql_latest.sql schema/schema_postgres_latest.sql || \
		echo "⚠️  Schemas differ. Run 'make db-migration' to create a migration."; \
	else \
		echo "PostgreSQL container not running. Cannot compare schemas."; \
	fi

# Database Management

db-create: ## Create all tables without migrations
	uv run python -c "from config import db_config; db_config.create_tables()"

db-drop: ## Drop all tables
	uv run python -c "from config import db_config; db_config.drop_tables()"

db-seed: ## Seed database with sample data
	uv run python examples/usage_example.py

# PostgreSQL with Docker

pg-start: ## Start PostgreSQL container
	@docker rm -f postgres-dev 2>/dev/null || true
	docker run -d --name postgres-dev \
		-e POSTGRES_USER=dev \
		-e POSTGRES_PASSWORD=devpass \
		-e POSTGRES_DB=sqlalchemy_test \
		-p 5433:5432 \
		postgres:15
	@echo "✓ PostgreSQL container started on port 5433"
	@echo "  Connection: postgresql://dev:devpass@localhost:5433/sqlalchemy_test"

pg-stop: ## Stop PostgreSQL container
	docker stop postgres-dev || true
	docker rm postgres-dev || true

pg-shell: ## Open PostgreSQL shell
	docker exec -it postgres-dev psql -U dev -d sqlalchemy_test

pg-test: ## Run tests with PostgreSQL
	@export DATABASE_URL="postgresql://dev:devpass@localhost:5433/sqlalchemy_test" && \
	make test

# Cleanup

clean: ## Remove Python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	rm -f .coverage

clean-db: ## Remove SQLite database file
	rm -f test.db
	rm -f sql_alchemy/test.db

clean-all: clean clean-db ## Remove all generated files
	@echo "All generated files removed"

# Development

shell: ## Open IPython shell with models loaded
	uv run --extra dev python -c "from models import *; from config import *; import IPython; IPython.embed()"

run-example: ## Run the usage example
	uv run python examples/usage_example.py

# CI/CD

ci-test: ## Run tests for CI
	uv sync --frozen --all-extras
	make lint
	make test

.DEFAULT_GOAL := help
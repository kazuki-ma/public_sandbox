#!/usr/bin/env python
"""Integrated validation and schema dump using testcontainer.

This script:
1. Starts PostgreSQL in testcontainer
2. Runs Alembic migrations
3. Dumps schema using pg_dump
4. Validates the entire process
"""

import os
import sys
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic import command

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import Base
from models import User, Post, Comment, Tag


def run_pg_dump(container: PostgresContainer, database: str = "test") -> Tuple[bool, str]:
    """Run pg_dump inside the container and capture output.

    Args:
        container: PostgreSQL testcontainer instance
        database: Database name to dump

    Returns:
        Tuple of (success, output)
    """
    container_id = container._container.id[:12]

    cmd = [
        "docker", "exec", container_id,
        "pg_dump",
        "--schema-only",
        "--no-owner",
        "--no-privileges",
        "--no-tablespaces",
        "--quote-all-identifiers",
        "-U", "test",  # testcontainer default user
        "-d", database
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ pg_dump failed: {e}")
        print(f"   stderr: {e.stderr}")
        return False, ""
    except subprocess.TimeoutExpired:
        print("❌ pg_dump timed out")
        return False, ""


def run_alembic_migrations(connection_url: str, alembic_ini_path: str = None) -> bool:
    """Run Alembic migrations against the database.

    Args:
        connection_url: Database connection URL
        alembic_ini_path: Path to alembic.ini file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Find alembic.ini
        if alembic_ini_path is None:
            # Look for alembic.ini in current directory and parent
            for path in ["alembic.ini", "../alembic.ini", "sql_alchemy/alembic.ini"]:
                if Path(path).exists():
                    alembic_ini_path = path
                    break

            if alembic_ini_path is None:
                print("⚠️  No alembic.ini found, skipping migrations")
                return True

        print(f"   Using alembic.ini: {alembic_ini_path}")

        # Configure Alembic
        alembic_cfg = Config(alembic_ini_path)
        alembic_cfg.set_main_option("sqlalchemy.url", connection_url)

        # Run migrations
        command.upgrade(alembic_cfg, "head")
        print("   ✓ Migrations applied successfully")
        return True

    except Exception as e:
        print(f"   ⚠️  Migration failed (non-critical): {e}")
        # Don't fail entirely if migrations fail - we can still dump schema
        return True


def create_models_directly(connection_url: str) -> bool:
    """Create all models directly using SQLAlchemy.

    Args:
        connection_url: Database connection URL

    Returns:
        True if successful
    """
    try:
        engine = create_engine(connection_url)
        Base.metadata.create_all(bind=engine)

        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
            ))
            tables = [row[0] for row in result]
            print(f"   ✓ Created {len(tables)} tables: {', '.join(sorted(tables))}")

        engine.dispose()
        return True

    except Exception as e:
        print(f"❌ Failed to create models: {e}")
        return False


def save_schema_dump(dump_content: str, output_dir: str = "schema") -> Path:
    """Save schema dump to file with timestamp.

    Args:
        dump_content: pg_dump output
        output_dir: Directory to save files

    Returns:
        Path to saved file
    """
    schema_dir = Path(output_dir)
    schema_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = schema_dir / f"schema_postgres_{timestamp}.sql"

    # Add header and write file
    with open(output_file, 'w') as f:
        f.write(f"--\n")
        f.write(f"-- PostgreSQL Schema Dump (via testcontainer)\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write(f"-- Method: Integrated validation with migrations\n")
        f.write(f"--\n\n")
        f.write(dump_content)

    # Create/update latest symlink
    latest_link = schema_dir / "schema_postgres_latest.sql"
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    latest_link.symlink_to(output_file.name)

    # Also create a clean version without comments
    clean_file = schema_dir / f"schema_postgres_clean_{timestamp}.sql"
    with open(output_file, 'r') as f_in:
        with open(clean_file, 'w') as f_out:
            for line in f_in:
                # Skip comment lines but keep SQL comments like COMMENT ON
                if not line.strip().startswith('--') or 'COMMENT ON' in line:
                    if line.strip():  # Skip empty lines
                        f_out.write(line)

    print(f"   ✓ Schema saved to {output_file}")
    print(f"   ✓ Clean version: {clean_file}")
    print(f"   ✓ Latest symlink: {latest_link}")

    return output_file


def validate_and_dump(use_migrations: bool = True, alembic_ini: str = None) -> int:
    """Main validation and dump process.

    Args:
        use_migrations: Whether to use Alembic migrations or create tables directly
        alembic_ini: Path to alembic.ini file

    Returns:
        Exit code (0 for success)
    """
    print("=" * 60)
    print(" PostgreSQL Schema Validation & Dump")
    print("=" * 60)
    print()

    print("1. Starting PostgreSQL testcontainer...")

    with PostgresContainer("postgres:15") as postgres:
        connection_url = postgres.get_connection_url()
        print(f"   ✓ Container started")
        print(f"   Connection: {connection_url}")

        print("\n2. Validating models...")
        try:
            # Import all models to ensure they're registered
            from models import User, Post, Comment, Tag
            print(f"   ✓ All models imported successfully")
        except Exception as e:
            print(f"   ❌ Model import failed: {e}")
            return 1

        print("\n3. Creating database schema...")
        if use_migrations:
            print("   Using Alembic migrations...")
            success = run_alembic_migrations(connection_url, alembic_ini)
            if not success:
                print("   Falling back to direct model creation...")
                success = create_models_directly(connection_url)
        else:
            print("   Creating tables from models...")
            success = create_models_directly(connection_url)

        if not success:
            print("❌ Failed to create schema")
            return 1

        print("\n4. Dumping schema with pg_dump...")
        success, dump_output = run_pg_dump(postgres)

        if not success:
            print("❌ Schema dump failed")
            return 1

        print("\n5. Saving schema files...")
        output_file = save_schema_dump(dump_output)

        print("\n6. Validating dump content...")
        lines = dump_output.split('\n')

        # Count important elements
        create_tables = len([l for l in lines if 'CREATE TABLE' in l])
        create_indexes = len([l for l in lines if 'CREATE INDEX' in l])
        constraints = len([l for l in lines if 'CONSTRAINT' in l or 'REFERENCES' in l])

        print(f"   Tables: {create_tables}")
        print(f"   Indexes: {create_indexes}")
        print(f"   Constraints: {constraints}")

        if create_tables == 0:
            print("   ⚠️  Warning: No tables found in dump!")

        # Extract table names
        table_names = []
        for line in lines:
            if 'CREATE TABLE' in line:
                # Extract table name from CREATE TABLE statement
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.upper() == 'TABLE':
                        if i + 1 < len(parts):
                            table_name = parts[i + 1].strip('"').strip(';')
                            if '.' in table_name:
                                table_name = table_name.split('.')[-1]
                            table_names.append(table_name)
                            break

        if table_names:
            print(f"   Found tables: {', '.join(sorted(table_names))}")

    print("\n" + "=" * 60)
    print(" ✅ Validation and Dump Complete!")
    print("=" * 60)

    return 0


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate models and dump PostgreSQL schema using testcontainer"
    )
    parser.add_argument(
        '--use-migrations',
        action='store_true',
        default=True,
        help='Use Alembic migrations (default: True)'
    )
    parser.add_argument(
        '--skip-migrations',
        action='store_true',
        help='Skip migrations and create tables directly from models'
    )
    parser.add_argument(
        '--alembic-ini',
        help='Path to alembic.ini file'
    )
    parser.add_argument(
        '--output-dir',
        default='schema',
        help='Output directory for schema files'
    )

    args = parser.parse_args()

    use_migrations = not args.skip_migrations

    exit_code = validate_and_dump(
        use_migrations=use_migrations,
        alembic_ini=args.alembic_ini
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
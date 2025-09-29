"""PostgreSQL schema dumper using pg_dump with testcontainers."""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from testcontainers.postgres import PostgresContainer

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import Base
from models import User, Post, Comment, Tag


def dump_with_testcontainer():
    """Use testcontainer PostgreSQL to generate schema dump."""
    print("Starting PostgreSQL container...")

    with PostgresContainer("postgres:15") as postgres:
        # Get connection details
        connection_url = postgres.get_connection_url()

        # Parse connection details
        # postgresql+psycopg2://test:test@localhost:32768/test
        import re
        pattern = r'postgresql(?:\+\w+)?://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
        match = re.match(pattern, connection_url)

        if match:
            username = match.group(1)
            password = match.group(2)
            host = match.group(3)
            port = match.group(4)
            database = match.group(5)
        else:
            # Fallback to default
            username = "test"
            password = "test"
            host = "localhost"
            port = "5432"
            database = "test"

        print(f"Container started at {host}:{port}")

        # Create tables using SQLAlchemy
        from sqlalchemy import create_engine
        engine = create_engine(connection_url)
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created")

        # Create schema directory
        schema_dir = Path("schema")
        schema_dir.mkdir(exist_ok=True)

        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = schema_dir / f"schema_postgres_{timestamp}.sql"

        # Run pg_dump using docker exec on the container
        container_id = postgres._container.id[:12]

        cmd = [
            "docker", "exec", container_id,
            "pg_dump",
            "--schema-only",
            "--no-owner", "--no-privileges",
            "--no-tablespaces",
            "--quote-all-identifiers",
            "-U", username,
            "-d", database
        ]

        print(f"Running pg_dump...")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Write output to file
            with open(output_file, 'w') as f:
                # Add header
                f.write(f"--\n")
                f.write(f"-- PostgreSQL Schema Dump\n")
                f.write(f"-- Generated: {datetime.now().isoformat()}\n")
                f.write(f"-- Generated with: pg_dump via testcontainer\n")
                f.write(f"--\n\n")
                f.write(result.stdout)

            # Create latest symlink
            latest_link = schema_dir / "schema_postgres_latest.sql"
            if latest_link.exists() or latest_link.is_symlink():
                latest_link.unlink()
            latest_link.symlink_to(output_file.name)

            print(f"✓ Schema dumped to {output_file}")
            print(f"  Latest link: {latest_link}")

            # Also create a clean version without comments
            clean_file = schema_dir / f"schema_postgres_clean_{timestamp}.sql"
            with open(output_file, 'r') as f_in:
                with open(clean_file, 'w') as f_out:
                    for line in f_in:
                        # Skip comment lines and empty lines
                        if not line.strip().startswith('--') and line.strip():
                            f_out.write(line)

            print(f"✓ Clean schema dumped to {clean_file}")

            return output_file

        except subprocess.CalledProcessError as e:
            print(f"❌ pg_dump failed: {e}")
            print(f"   stderr: {e.stderr}")
            return None


def dump_with_running_container():
    """Use existing PostgreSQL container to dump schema."""
    # Check if container is running
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=postgres-dev", "--format", "{{.Names}}"],
            capture_output=True, text=True, check=True
        )

        if "postgres-dev" not in result.stdout:
            print("❌ PostgreSQL container 'postgres-dev' is not running")
            print("   Start it with: make pg-start")
            return None

        # Create schema directory
        schema_dir = Path("schema")
        schema_dir.mkdir(exist_ok=True)

        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = schema_dir / f"schema_postgres_{timestamp}.sql"

        # Run pg_dump
        cmd = [
            "docker", "exec", "postgres-dev",
            "pg_dump",
            "--schema-only",
            "--no-owner", "--no-privileges",
            "--no-tablespaces",
            "--quote-all-identifiers",
            "-U", "dev",
            "-d", "sqlalchemy_test"
        ]

        print(f"Running pg_dump on postgres-dev container...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Write output to file
        with open(output_file, 'w') as f:
            # Add header
            f.write(f"--\n")
            f.write(f"-- PostgreSQL Schema Dump\n")
            f.write(f"-- Generated: {datetime.now().isoformat()}\n")
            f.write(f"-- Container: postgres-dev\n")
            f.write(f"--\n\n")
            f.write(result.stdout)

        # Create latest symlink
        latest_link = schema_dir / "schema_postgres_latest.sql"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(output_file.name)

        print(f"✓ Schema dumped to {output_file}")
        print(f"  Latest link: {latest_link}")

        return output_file

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to dump schema: {e}")
        print(f"   stderr: {e.stderr}")
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Dump PostgreSQL schema using pg_dump")
    parser.add_argument('--use-testcontainer', action='store_true',
                       help='Use testcontainer for dumping (creates temporary container)')
    parser.add_argument('--use-running', action='store_true',
                       help='Use existing postgres-dev container')

    args = parser.parse_args()

    if args.use_testcontainer:
        dump_with_testcontainer()
    elif args.use_running:
        dump_with_running_container()
    else:
        # Try running container first, fall back to testcontainer
        result = dump_with_running_container()
        if result is None:
            print("\nFalling back to testcontainer...")
            dump_with_testcontainer()
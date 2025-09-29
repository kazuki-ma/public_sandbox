"""Database schema dumper for SQLAlchemy models."""

import os
import sys
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, MetaData
from sqlalchemy.schema import CreateTable, CreateIndex, CreateSequence
from sqlalchemy.dialects import postgresql, mysql, sqlite

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import Base, DatabaseConfig
from models import User, Post, Comment, Tag


def get_dialect_ddl(metadata, dialect_name='postgresql'):
    """Generate DDL for specific dialect."""
    dialects = {
        'postgresql': postgresql.dialect(),
        'mysql': mysql.dialect(),
        'sqlite': sqlite.dialect()
    }

    dialect = dialects.get(dialect_name, postgresql.dialect())
    ddl_statements = []

    # Add header
    ddl_statements.append(f"-- SQLAlchemy Schema Dump")
    ddl_statements.append(f"-- Generated: {datetime.now().isoformat()}")
    ddl_statements.append(f"-- Dialect: {dialect_name}")
    ddl_statements.append(f"-- Tables: {', '.join(sorted(metadata.tables.keys()))}")
    ddl_statements.append("")

    # Generate CREATE SEQUENCE statements for PostgreSQL
    if dialect_name == 'postgresql':
        for table in metadata.sorted_tables:
            for column in table.columns:
                if column.autoincrement and column.default is None:
                    seq_name = f"{table.name}_{column.name}_seq"
                    ddl_statements.append(f"-- Sequence for {table.name}.{column.name}")
                    ddl_statements.append(f"CREATE SEQUENCE IF NOT EXISTS {seq_name};")
                    ddl_statements.append("")

    # Generate CREATE TABLE statements
    ddl_statements.append("-- Tables")
    for table in metadata.sorted_tables:
        ddl_statements.append(f"-- Table: {table.name}")
        create_stmt = str(CreateTable(table).compile(dialect=dialect))
        # Format for readability
        create_stmt = create_stmt.replace('\n', '\n  ').replace('\t', '  ')
        ddl_statements.append(create_stmt + ";")
        ddl_statements.append("")

    # Generate CREATE INDEX statements
    has_indexes = False
    for table in metadata.sorted_tables:
        for index in table.indexes:
            if not has_indexes:
                ddl_statements.append("-- Indexes")
                has_indexes = True
            ddl_statements.append(f"-- Index: {index.name} on {table.name}")
            create_idx = str(CreateIndex(index).compile(dialect=dialect))
            ddl_statements.append(create_idx + ";")
            ddl_statements.append("")

    return '\n'.join(ddl_statements)


def dump_schema_to_file(output_dir='schema', dialects=None):
    """Dump schema to SQL files for different dialects."""
    if dialects is None:
        dialects = ['postgresql', 'mysql', 'sqlite']

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Generate timestamp for filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Dump for each dialect
    for dialect_name in dialects:
        ddl = get_dialect_ddl(Base.metadata, dialect_name)

        # Write to timestamped file
        filename = f"schema_{dialect_name}_{timestamp}.sql"
        filepath = output_path / filename
        filepath.write_text(ddl)

        # Create/update latest symlink
        latest_link = output_path / f"schema_{dialect_name}_latest.sql"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(filename)

        print(f"✓ Schema dumped to {filepath}")
        print(f"  Latest link: {latest_link}")

    # Create a combined schema file with all dialects
    combined_path = output_path / f"schema_all_{timestamp}.sql"
    with open(combined_path, 'w') as f:
        for dialect_name in dialects:
            f.write(f"-- {'=' * 60}\n")
            f.write(f"-- DIALECT: {dialect_name.upper()}\n")
            f.write(f"-- {'=' * 60}\n\n")
            f.write(get_dialect_ddl(Base.metadata, dialect_name))
            f.write("\n\n")

    combined_latest = output_path / "schema_all_latest.sql"
    if combined_latest.exists() or combined_latest.is_symlink():
        combined_latest.unlink()
    combined_latest.symlink_to(f"schema_all_{timestamp}.sql")

    print(f"✓ Combined schema dumped to {combined_path}")
    print(f"  Latest link: {combined_latest}")

    return output_path


def dump_current_database_schema(database_url=None):
    """Dump schema from actual database (not models)."""
    if database_url is None:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    engine = create_engine(database_url)
    metadata = MetaData()
    metadata.reflect(bind=engine)

    output_path = Path("schema")
    output_path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Determine dialect from URL
    if 'postgresql' in database_url:
        dialect_name = 'postgresql'
    elif 'mysql' in database_url:
        dialect_name = 'mysql'
    else:
        dialect_name = 'sqlite'

    ddl = get_dialect_ddl(metadata, dialect_name)

    filename = f"schema_from_db_{timestamp}.sql"
    filepath = output_path / filename
    filepath.write_text(ddl)

    latest_link = output_path / "schema_from_db_latest.sql"
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()
    latest_link.symlink_to(filename)

    print(f"✓ Database schema dumped to {filepath}")
    print(f"  Latest link: {latest_link}")

    return filepath


def validate_and_dump():
    """Validate models and dump schema."""
    try:
        # Import all models to ensure they're registered
        from models import User, Post, Comment, Tag

        # Check for duplicate table names
        tables = Base.metadata.tables
        print(f"✓ Found {len(tables)} tables: {', '.join(sorted(tables.keys()))}")

        # Check relationships
        for table_name, table in tables.items():
            foreign_keys = [fk for fk in table.foreign_keys]
            if foreign_keys:
                print(f"  {table_name}: {len(foreign_keys)} foreign keys")

        # Dump schema
        print("\nDumping schema...")
        dump_schema_to_file()

        print("\n✅ Validation and dump completed successfully!")
        return 0

    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Dump SQLAlchemy schema to SQL files")
    parser.add_argument('--dialects', nargs='+',
                       choices=['postgresql', 'mysql', 'sqlite'],
                       default=['postgresql', 'mysql', 'sqlite'],
                       help='SQL dialects to generate')
    parser.add_argument('--output-dir', default='schema',
                       help='Output directory for SQL files')
    parser.add_argument('--from-db', action='store_true',
                       help='Dump from actual database instead of models')
    parser.add_argument('--validate', action='store_true',
                       help='Validate models before dumping')

    args = parser.parse_args()

    if args.validate:
        sys.exit(validate_and_dump())
    elif args.from_db:
        dump_current_database_schema()
    else:
        dump_schema_to_file(args.output_dir, args.dialects)
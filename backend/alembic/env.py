"""
backend/alembic/env.py
Alembic environment configuration for IC_MemTrendDashboard.

Supports both offline (SQL dump) and online (live DB) migration modes.
DATABASE_URL is read from the environment; asyncpg dialect suffix is stripped
because Alembic's synchronous engine requires a sync driver.
"""
from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# ---------------------------------------------------------------------------
# Ensure 'backend/' is on sys.path so 'app.*' imports resolve correctly
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ---------------------------------------------------------------------------
# Import Base and all models to register their metadata
# ---------------------------------------------------------------------------
from app.db.database import Base  # noqa: E402
from app.models.instruments import (  # noqa: E402, F401 – side-effect imports
    AlertEvent,
    AlertRule,
    CorrelationMatrix,
    EquityPrice,
    Instrument,
    MarketEvent,
    MarketScore,
    MemoryQuote,
    NewsItem,
    RefreshJob,
    SourceRun,
    TrendMetric,
)

# ---------------------------------------------------------------------------
# Alembic Config object
# ---------------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging if present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Helper: build a synchronous DATABASE_URL from environment
# ---------------------------------------------------------------------------

def _get_sync_url() -> str:
    """Return a *synchronous* SQLAlchemy URL for Alembic.

    The application uses ``postgresql+asyncpg://…`` but Alembic requires a
    sync driver.  We swap the asyncpg dialect suffix for psycopg2 (or plain
    postgresql) so that ``engine_from_config`` can create a blocking engine.
    """
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set. "
            "Export it before running Alembic commands."
        )
    # Replace async driver specifier with synchronous equivalent
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    url = url.replace("sqlite+aiosqlite://", "sqlite://")
    return url


# ---------------------------------------------------------------------------
# Offline migrations (alembic upgrade --sql)
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (SQL dump mode).

    Useful for generating migration SQL scripts for review or deployment
    in environments where a direct DB connection is not available.
    """
    url = _get_sync_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migrations (default: alembic upgrade head)
# ---------------------------------------------------------------------------

def run_migrations_online() -> None:
    """Run migrations with a live database connection.

    Creates a synchronous engine from the environment DATABASE_URL and
    executes the migration scripts inside a transaction.
    """
    url = _get_sync_url()
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

"""
backend/alembic/versions/0001_initial_schema.py
=================================================
Initial migration: create all IC_MemTrendDashboard tables.

Revision ID: 0001
Revises:     None
Create Date: 2026-06-23

Tables created (in dependency order):
  1. instruments
  2. equity_prices
  3. memory_quotes
  4. trend_metrics
  5. market_scores
  6. source_runs
  7. refresh_jobs
  8. alert_rules
  9. alert_events
  10. news_items
  11. market_events
  12. correlation_matrix
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# ---------------------------------------------------------------------------
# Revision identifiers
# ---------------------------------------------------------------------------

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ts() -> sa.Column:
    """Return a timezone-aware TIMESTAMP column type.

    Uses TIMESTAMP(timezone=True) for PostgreSQL, which maps gracefully to
    DATETIME for SQLite in test environments.
    """
    return sa.TIMESTAMP(timezone=True)


# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------

def upgrade() -> None:
    """Create all tables from scratch."""

    # ------------------------------------------------------------------
    # 1. instruments
    # ------------------------------------------------------------------
    op.create_table(
        "instruments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ticker", sa.String(20), nullable=False),
        sa.Column("market", sa.String(10), nullable=False),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("name_en", sa.String(100), nullable=True),
        sa.Column("tier", sa.String(5), nullable=False),
        sa.Column("supply_chain_tag", sa.String(50), nullable=True),
        sa.Column("currency", sa.String(5), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "score_weight",
            sa.Numeric(precision=5, scale=4),
            nullable=True,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "score_only_observe",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "created_at",
            _ts(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ticker", "market", name="uq_instrument_ticker_market"),
    )

    # ------------------------------------------------------------------
    # 2. equity_prices
    # ------------------------------------------------------------------
    op.create_table(
        "equity_prices",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("instrument_id", sa.Integer(), nullable=False),
        sa.Column("trade_date", sa.Date(), nullable=False),
        sa.Column("open", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("high", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("low", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("close", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("volume", sa.BigInteger(), nullable=True),
        sa.Column("source", sa.String(20), nullable=True),
        sa.Column(
            "created_at",
            _ts(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["instrument_id"],
            ["instruments.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "instrument_id",
            "trade_date",
            name="uq_equity_price_instrument_date",
        ),
    )

    # ------------------------------------------------------------------
    # 3. memory_quotes
    # ------------------------------------------------------------------
    op.create_table(
        "memory_quotes",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("product", sa.String(50), nullable=False),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("price_type", sa.String(20), nullable=True),
        sa.Column("price_high", sa.Numeric(precision=12, scale=6), nullable=True),
        sa.Column("price_low", sa.Numeric(precision=12, scale=6), nullable=True),
        sa.Column("price_avg", sa.Numeric(precision=12, scale=6), nullable=True),
        sa.Column("change_pct", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("currency", sa.String(5), nullable=True, server_default="USD"),
        sa.Column("unit", sa.String(20), nullable=True),
        sa.Column("source", sa.String(30), nullable=True),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column(
            "fetched_at",
            _ts(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "product",
            "price_type",
            "snapshot_date",
            name="uq_memory_quote_product_type_date",
        ),
    )

    # ------------------------------------------------------------------
    # 4. trend_metrics
    # ------------------------------------------------------------------
    op.create_table(
        "trend_metrics",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("instrument_id", sa.Integer(), nullable=False),
        sa.Column("as_of_date", sa.Date(), nullable=False),
        sa.Column("period", sa.String(5), nullable=False),
        sa.Column("change_pct", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("change_abs", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("direction", sa.String(10), nullable=True),
        sa.Column("momentum", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("ma_state", sa.JSON(), nullable=True),
        sa.Column("volatility", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("hi_lo_flag", sa.JSON(), nullable=True),
        sa.Column("streak", sa.Integer(), nullable=True),
        sa.Column("acceleration", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("normalized_index", sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column("narrative", sa.Text(), nullable=True),
        sa.Column(
            "computed_at",
            _ts(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["instrument_id"],
            ["instruments.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "instrument_id",
            "as_of_date",
            "period",
            name="uq_trend_metric_instrument_date_period",
        ),
    )

    # ------------------------------------------------------------------
    # 5. market_scores
    # ------------------------------------------------------------------
    op.create_table(
        "market_scores",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("score_date", sa.Date(), nullable=False, unique=True),
        sa.Column("total_score", sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column(
            "quote_momentum_score", sa.Numeric(precision=6, scale=3), nullable=True
        ),
        sa.Column(
            "equity_momentum_score", sa.Numeric(precision=6, scale=3), nullable=True
        ),
        sa.Column("breadth_score", sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column("risk_score", sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column(
            "relative_strength_score", sa.Numeric(precision=6, scale=3), nullable=True
        ),
        sa.Column("status", sa.String(20), nullable=True),
        sa.Column("narrative", sa.JSON(), nullable=True),
        sa.Column(
            "computed_at",
            _ts(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("score_date", name="uq_market_score_date"),
    )

    # ------------------------------------------------------------------
    # 6. source_runs
    # ------------------------------------------------------------------
    op.create_table(
        "source_runs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("source_name", sa.String(50), nullable=False),
        sa.Column("trigger", sa.String(20), nullable=False),
        sa.Column("started_at", _ts(), nullable=True),
        sa.Column("finished_at", _ts(), nullable=True),
        sa.Column("status", sa.String(20), nullable=True),
        sa.Column("rows_fetched", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("error_msg", sa.Text(), nullable=True),
        # Column alias: Python attribute 'metadata_' maps to 'metadata' in DB
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # ------------------------------------------------------------------
    # 7. refresh_jobs
    # ------------------------------------------------------------------
    op.create_table(
        "refresh_jobs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.String(36), nullable=False),
        sa.Column("trigger", sa.String(20), nullable=False),
        sa.Column(
            "started_at",
            _ts(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("finished_at", _ts(), nullable=True),
        sa.Column(
            "status", sa.String(20), nullable=False, server_default="running"
        ),
        sa.Column("progress", sa.JSON(), nullable=True),
        sa.Column("lock_key", sa.String(100), nullable=True, unique=True),
        sa.Column("success_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("fail_count", sa.Integer(), nullable=True, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lock_key", name="uq_refresh_jobs_lock_key"),
    )

    # ------------------------------------------------------------------
    # 8. alert_rules
    # ------------------------------------------------------------------
    op.create_table(
        "alert_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rule_name", sa.String(100), nullable=True),
        sa.Column("instrument_id", sa.Integer(), nullable=True),
        sa.Column("metric", sa.String(50), nullable=True),
        sa.Column("condition", sa.String(10), nullable=True),
        sa.Column("threshold", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("channel", sa.String(20), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column(
            "created_at",
            _ts(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["instrument_id"],
            ["instruments.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ------------------------------------------------------------------
    # 9. alert_events
    # ------------------------------------------------------------------
    op.create_table(
        "alert_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("rule_id", sa.Integer(), nullable=False),
        sa.Column(
            "triggered_at",
            _ts(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("metric_value", sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column("notify_status", sa.String(20), nullable=True),
        sa.Column("notify_response", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["rule_id"],
            ["alert_rules.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ------------------------------------------------------------------
    # 10. news_items
    # ------------------------------------------------------------------
    op.create_table(
        "news_items",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("url", sa.String(500), nullable=False, unique=True),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("source_name", sa.String(100), nullable=True),
        sa.Column("published_at", _ts(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("sentiment", sa.String(20), nullable=True),
        sa.Column("key_points", sa.JSON(), nullable=True),
        sa.Column("related_tickers", sa.JSON(), nullable=True),
        sa.Column(
            "fetched_at",
            _ts(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url", name="uq_news_items_url"),
    )

    # ------------------------------------------------------------------
    # 11. market_events
    # ------------------------------------------------------------------
    op.create_table(
        "market_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("related_tickers", sa.JSON(), nullable=True),
        sa.Column("category", sa.String(20), nullable=True),
        sa.Column(
            "created_at",
            _ts(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ------------------------------------------------------------------
    # 12. correlation_matrix
    # ------------------------------------------------------------------
    op.create_table(
        "correlation_matrix",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("instrument_id", sa.Integer(), nullable=False),
        sa.Column("quote_product", sa.String(50), nullable=True),
        sa.Column("window_days", sa.Integer(), nullable=True),
        sa.Column("coefficient", sa.Numeric(precision=8, scale=6), nullable=True),
        sa.Column(
            "computed_at",
            _ts(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["instrument_id"],
            ["instruments.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "instrument_id",
            "quote_product",
            "window_days",
            name="uq_correlation_instrument_product_window",
        ),
    )


# ---------------------------------------------------------------------------
# Downgrade
# ---------------------------------------------------------------------------

def downgrade() -> None:
    """Drop all tables in reverse dependency order."""
    op.drop_table("correlation_matrix")
    op.drop_table("market_events")
    op.drop_table("news_items")
    op.drop_table("alert_events")
    op.drop_table("alert_rules")
    op.drop_table("refresh_jobs")
    op.drop_table("source_runs")
    op.drop_table("market_scores")
    op.drop_table("trend_metrics")
    op.drop_table("memory_quotes")
    op.drop_table("equity_prices")
    op.drop_table("instruments")

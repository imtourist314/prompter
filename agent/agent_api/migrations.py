from __future__ import annotations

import logging
from typing import Iterable

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

DEFAULT_COMPONENT_VALUE = "default"
TARGET_TABLES: Iterable[str] = ("prm_subscriber", "prm_subscription_file")
TARGET_COLUMN = "component"
COLUMN_TYPE = "VARCHAR(128)"


def _has_table(inspector, table_name: str) -> bool:
    return table_name in inspector.get_table_names()


def _has_column(inspector, table_name: str, column_name: str) -> bool:
    try:
        columns = inspector.get_columns(table_name)
    except Exception:  # pragma: no cover - depends on backend
        return False
    return any(column["name"] == column_name for column in columns)


def _add_component_column(engine: Engine, table_name: str) -> None:
    logger.info("Adding missing '%s' column to table %s", TARGET_COLUMN, table_name)
    ddl = f"ALTER TABLE {table_name} ADD COLUMN {TARGET_COLUMN} {COLUMN_TYPE}"
    with engine.begin() as conn:
        conn.execute(text(ddl))
        conn.execute(
            text(
                f"UPDATE {table_name} SET {TARGET_COLUMN} = :default "
                f"WHERE {TARGET_COLUMN} IS NULL OR {TARGET_COLUMN} = ''"
            ),
            {"default": DEFAULT_COMPONENT_VALUE},
        )


def run_migrations(engine: Engine) -> None:
    """Apply lightweight in-place migrations required for the API."""

    inspector = inspect(engine)
    for table_name in TARGET_TABLES:
        if not _has_table(inspector, table_name):
            continue
        if _has_column(inspector, table_name, TARGET_COLUMN):
            continue
        _add_component_column(engine, table_name)
        # Refresh inspector metadata for subsequent checks
        inspector = inspect(engine)


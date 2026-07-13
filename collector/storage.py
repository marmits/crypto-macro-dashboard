from __future__ import annotations

import sqlite3
from datetime import datetime, timezone


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def upsert_macro_observation(
    connection: sqlite3.Connection,
    source: str,
    symbol: str,
    name: str,
    value: float,
    unit: str,
    observed_at: str,
) -> None:
    """
    Insère ou met à jour une observation dans macro_series.
    """

    current_time = now_iso()

    connection.execute(
        """
        INSERT INTO macro_series (
            source,
            symbol,
            name,
            value,
            unit,
            observed_at,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source, symbol, observed_at)
        DO UPDATE SET
            name = excluded.name,
            value = excluded.value,
            unit = excluded.unit,
            updated_at = excluded.updated_at
        """,
        (
            source,
            symbol,
            name,
            value,
            unit,
            observed_at,
            current_time,
            current_time,
        ),
    )
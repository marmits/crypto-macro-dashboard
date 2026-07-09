import sqlite3
from datetime import datetime, timezone
from typing import Any

import requests

from config import DB_PATH, FRED_API_KEY, FRED_BASE_URL, FRED_SERIES


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fred_date_to_iso(date_value: str) -> str:
    return f"{date_value}T00:00:00+00:00"


def create_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS macro_series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL,
            observed_at TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_macro_series_symbol_observed_at
        ON macro_series (symbol, observed_at)
        """
    )

    connection.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_macro_series_source_symbol_observed_at
        ON macro_series (source, symbol, observed_at)
        """
    )


def fetch_fred_observations(series_id: str, limit: int = 12) -> list[dict[str, Any]]:
    if not FRED_API_KEY:
        raise RuntimeError(
            "FRED_API_KEY est manquant. Vérifie le fichier .env à la racine du projet."
        )

    url = f"{FRED_BASE_URL}/series/observations"

    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    payload = response.json()

    observations = payload.get("observations", [])

    cleaned_observations = []

    for observation in observations:
        value = observation.get("value")

        if value in (None, "."):
            continue

        cleaned_observations.append(
            {
                "date": observation["date"],
                "value": float(value),
            }
        )

    return list(reversed(cleaned_observations))


def upsert_macro_observation(
    connection: sqlite3.Connection,
    source: str,
    symbol: str,
    name: str,
    value: float,
    unit: str,
    observed_at: str,
) -> None:
    created_at = now_iso()

    connection.execute(
        """
        INSERT INTO macro_series (
            source,
            symbol,
            name,
            value,
            unit,
            observed_at,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source, symbol, observed_at)
        DO UPDATE SET
            name = excluded.name,
            value = excluded.value,
            unit = excluded.unit,
            created_at = excluded.created_at
        """,
        (
            source,
            symbol,
            name,
            value,
            unit,
            observed_at,
            created_at,
        ),
    )


def collect_fred_series(connection: sqlite3.Connection, series_id: str) -> None:
    series_config = FRED_SERIES[series_id]

    print(f"Collecte FRED en cours : {series_id}")

    observations = fetch_fred_observations(series_id=series_id, limit=12)

    for observation in observations:
        upsert_macro_observation(
            connection=connection,
            source=series_config["source"],
            symbol=series_config["symbol"],
            name=series_config["name"],
            value=observation["value"],
            unit=series_config["unit"],
            observed_at=fred_date_to_iso(observation["date"]),
        )

    print(f"{len(observations)} observation(s) FRED traitée(s) pour {series_id}.")


def print_existing_rows(connection: sqlite3.Connection) -> None:
    rows = connection.execute(
        """
        SELECT
            id,
            source,
            symbol,
            name,
            value,
            unit,
            observed_at,
            created_at
        FROM macro_series
        ORDER BY observed_at DESC, id DESC
        LIMIT 15
        """
    ).fetchall()

    print("Dernières lignes présentes dans macro_series :")

    if not rows:
        print("Aucune ligne trouvée.")
        return

    for row in rows:
        print(
            {
                "id": row[0],
                "source": row[1],
                "symbol": row[2],
                "name": row[3],
                "value": row[4],
                "unit": row[5],
                "observed_at": row[6],
                "created_at": row[7],
            }
        )


def main() -> None:
    print("Démarrage du collector macro crypto")
    print(f"Base SQLite utilisée : {DB_PATH}")

    connection = sqlite3.connect(DB_PATH)

    try:
        create_schema(connection)

        collect_fred_series(connection, "FEDFUNDS")

        connection.commit()

        print("Collecte FRED terminée avec succès.")

        print_existing_rows(connection)

    finally:
        connection.close()
        print("Connexion SQLite fermée.")

    print("Collector terminé sans erreur.")


if __name__ == "__main__":
    main()
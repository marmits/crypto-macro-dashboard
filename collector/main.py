import sqlite3
from datetime import datetime, timezone
from typing import Any

import requests

from config import (
    DB_PATH,
    FRED_API_KEY,
    FRED_BASE_URL,
    FRED_SERIES,
    COINGECKO_BASE_URL,
    COINGECKO_COINS,
)
"""
version avec api key de coingecko
from config import (
    DB_PATH,
    FRED_API_KEY,
    FRED_BASE_URL,
    FRED_SERIES,
    COINGECKO_API_KEY,
    COINGECKO_BASE_URL,
    COINGECKO_COINS,
)
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fred_date_to_iso(date_value: str) -> str:
    return f"{date_value}T00:00:00+00:00"


def unix_timestamp_to_iso(timestamp: int | float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def ensure_updated_at_column(connection: sqlite3.Connection) -> None:
    columns = connection.execute(
        """
        PRAGMA table_info(macro_series)
        """
    ).fetchall()

    column_names = {column[1] for column in columns}

    if "updated_at" not in column_names:
        print("Migration SQLite : ajout de la colonne updated_at")

        connection.execute(
            """
            ALTER TABLE macro_series
            ADD COLUMN updated_at TEXT
            """
        )

        connection.execute(
            """
            UPDATE macro_series
            SET updated_at = created_at
            WHERE updated_at IS NULL
            """
        )


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
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    ensure_updated_at_column(connection)

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


def fetch_coingecko_simple_price(coin_id: str) -> dict[str, Any]:
    url = f"{COINGECKO_BASE_URL}/simple/price"

    params = {
        "ids": coin_id,
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_last_updated_at": "true",
    }

    headers = {
        "accept": "application/json",
    }

    """ if COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_API_KEY
    """

    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()

    payload = response.json()

    if coin_id not in payload:
        raise RuntimeError(f"Réponse CoinGecko inattendue : coin absent '{coin_id}'")

    coin_payload = payload[coin_id]

    if "usd" not in coin_payload:
        raise RuntimeError(f"Réponse CoinGecko inattendue : prix USD absent pour '{coin_id}'")

    return coin_payload


def upsert_macro_observation(
    connection: sqlite3.Connection,
    source: str,
    symbol: str,
    name: str,
    value: float,
    unit: str,
    observed_at: str,
) -> None:
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


def collect_fred_series(connection: sqlite3.Connection, series_id: str) -> None:
    series_config = FRED_SERIES[series_id]
    limit = series_config.get("limit", 12)

    print(
        f"Collecte FRED en cours : {series_id} "
        f"-> {series_config['symbol']} "
        f"limit={limit}"
    )

    observations = fetch_fred_observations(series_id=series_id, limit=limit)

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

    print(
        f"{len(observations)} observation(s) FRED traitée(s) "
        f"pour {series_id} -> {series_config['symbol']}."
    )


def collect_coingecko_coin(connection: sqlite3.Connection, coin_id: str) -> None:
    coin_config = COINGECKO_COINS[coin_id]

    print(f"Collecte CoinGecko en cours : {coin_id}")

    coin_payload = fetch_coingecko_simple_price(coin_id)

    price = float(coin_payload["usd"])

    last_updated_at = coin_payload.get("last_updated_at")

    if last_updated_at:
        observed_at = unix_timestamp_to_iso(last_updated_at)
    else:
        observed_at = now_iso()

    upsert_macro_observation(
        connection=connection,
        source=coin_config["source"],
        symbol=coin_config["symbol"],
        name=coin_config["name"],
        value=price,
        unit=coin_config["unit"],
        observed_at=observed_at,
    )

    change_24h = coin_payload.get("usd_24h_change")

    print(
        {
            "source": coin_config["source"],
            "symbol": coin_config["symbol"],
            "name": coin_config["name"],
            "value": price,
            "unit": coin_config["unit"],
            "observed_at": observed_at,
            "usd_24h_change": change_24h,
        }
    )

    print(f"Observation CoinGecko traitée pour {coin_config['symbol']}.")


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
            created_at,
            updated_at
        FROM macro_series
        ORDER BY observed_at DESC, id DESC
        LIMIT 20
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
                "updated_at": row[8],
            }
        )


def main() -> None:
    print("Démarrage du collector macro crypto")
    print(f"Base SQLite utilisée : {DB_PATH}")

    connection = sqlite3.connect(DB_PATH)

    try:
        create_schema(connection)

        for series_id in FRED_SERIES.keys():
            collect_fred_series(connection, series_id)

        for coin_id in COINGECKO_COINS.keys():
            collect_coingecko_coin(connection, coin_id)

        connection.commit()

        print("Collectes terminées avec succès.")

        print_existing_rows(connection)

    finally:
        connection.close()
        print("Connexion SQLite fermée.")

    print("Collector terminé sans erreur.")


if __name__ == "__main__":
    main()
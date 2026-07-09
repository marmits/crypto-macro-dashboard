import sqlite3
from datetime import datetime, timezone

from config import DB_PATH


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def insert_test_data(connection: sqlite3.Connection) -> None:
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
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "test",
            "TEST_MACRO_SCORE",
            "Score macro de test",
            0,
            "score",
            current_time,
            current_time,
        ),
    )


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
        ORDER BY id DESC
        LIMIT 10
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
        insert_test_data(connection)
        connection.commit()

        print("Base SQLite initialisée avec succès.")
        print("Donnée de test insérée avec succès.")

        print_existing_rows(connection)

    finally:
        connection.close()
        print("Connexion SQLite fermée.")

    print("Collector terminé sans erreur.")


if __name__ == "__main__":
    main()
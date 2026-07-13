from __future__ import annotations

import sqlite3

from storage import now_iso, upsert_macro_observation


DERIVED_SOURCE = "derived"


def load_latest_metrics(connection: sqlite3.Connection) -> dict[str, float]:
    """
    Charge la dernière valeur connue de chaque symbole.
    """

    cursor = connection.execute(
        """
        SELECT symbol, value
        FROM macro_series
        WHERE id IN (
            SELECT MAX(id)
            FROM macro_series
            GROUP BY symbol
        )
        """
    )

    return {
        row[0]: float(row[1])
        for row in cursor.fetchall()
    }


def compute_btc_market_cap(metrics: dict[str, float]) -> float:
    return metrics["TOTAL_MCAP"] * metrics["BTC_DOM"] / 100.0


def compute_eth_market_cap(metrics: dict[str, float]) -> float:
    return metrics["TOTAL_MCAP"] * metrics["ETH_DOM"] / 100.0


def compute_total3(metrics: dict[str, float]) -> float:
    return (
        metrics["TOTAL_MCAP"]
        - metrics["BTC_MCAP"]
        - metrics["ETH_MCAP"]
    )


def collect_derived_metrics(connection: sqlite3.Connection) -> None:

    print("Collecte Derived Metrics en cours")

    metrics = load_latest_metrics(connection)

    metrics["BTC_MCAP"] = compute_btc_market_cap(metrics)
    metrics["ETH_MCAP"] = compute_eth_market_cap(metrics)
    metrics["TOTAL3"] = compute_total3(metrics)

    observed_at = now_iso()

    derived_metrics = (
        (
            "BTC_MCAP",
            "Bitcoin Market Cap",
            metrics["BTC_MCAP"],
            "usd",
        ),
        (
            "ETH_MCAP",
            "Ethereum Market Cap",
            metrics["ETH_MCAP"],
            "usd",
        ),
        (
            "TOTAL3",
            "Total Altcoin Market Cap",
            metrics["TOTAL3"],
            "usd",
        ),
    )

    for symbol, name, value, unit in derived_metrics:

        upsert_macro_observation(
            connection=connection,
            source=DERIVED_SOURCE,
            symbol=symbol,
            name=name,
            value=value,
            unit=unit,
            observed_at=observed_at,
        )

        print(
            {
                "symbol": symbol,
                "value": value,
            }
        )

    print("Collecte Derived Metrics terminée.")
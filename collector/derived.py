from __future__ import annotations

import sqlite3

from storage import now_iso, upsert_macro_observation


DERIVED_SOURCE = "derived"
SIGNALS = (
    (
        "BTC_DOM",
        "BTC_DOM_SIGNAL",
        "Bitcoin Dominance Signal",
        True,
    ),
    (
        "STABLECOIN_DOM",
        "STABLECOIN_SIGNAL",
        "Stablecoin Dominance Signal",
        True,
    ),
    (
        "ETH_BTC",
        "ETH_BTC_SIGNAL",
        "ETH / BTC Signal",
        False,
    ),
    (
        "TOTAL3",
        "TOTAL3_SIGNAL",
        "TOTAL3 Signal",
        False,
    ),
)


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

def load_metric_history(
    connection: sqlite3.Connection,
) -> dict[str, list[float]]:
    """
    Charge les deux dernières observations disponibles pour chaque symbole,
    de la plus ancienne à la plus récente.
    """

    cursor = connection.execute(
        """
        SELECT
            symbol,
            value
        FROM (
            SELECT
                symbol,
                value,
                ROW_NUMBER() OVER (
                    PARTITION BY symbol
                    ORDER BY observed_at DESC
                ) AS rn
            FROM macro_series
        )
        WHERE rn <= 2
        ORDER BY symbol, rn DESC;
        """
    )

    history: dict[str, list[float]] = {}

    for symbol, value in cursor.fetchall():

        history.setdefault(symbol, []).append(
            float(value)
        )

    return history


def previous_current(
    history: dict[str, list[float]],
    symbol: str,
) -> tuple[float, float] | None:
    """
    Retourne les deux dernières valeurs d'un symbole.

    Renvoie None si l'historique est insuffisant.
    """

    values = history.get(symbol)

    if values is None:
        return None

    if len(values) < 2:
        return None

    return values[-2], values[-1]


def latest_metric(
    history: dict[str, list[float]],
    symbol: str,
) -> float | None:
    """
    Retourne la dernière valeur connue d'un symbole.

    Renvoie None si absente.
    """

    values = history.get(symbol)

    if not values:
        return None

    return values[-1]

def trend_signal(
    previous: float,
    current: float,
    inverted: bool = False,
) -> int:
    """
    Retourne :

        +1 : tendance positive
         0 : stable
        -1 : tendance négative

    inverted=True inverse la logique.
    """

    if current > previous:
        signal = 1
    elif current < previous:
        signal = -1
    else:
        signal = 0

    if inverted:
        signal *= -1
    
    return signal

def market_regime_state(
    score: int,
) -> int:
    """
    Convertit un Market Regime Score (-4 à +4)
    en état de marché.

        0 : Risk-Off
        1 : Defensive
        2 : Neutral
        3 : Bullish
        4 : Risk-On
    """

    if score <= -3:
        return 0

    if score <= -1:
        return 1

    if score == 0:
        return 2

    if score <= 2:
        return 3

    return 4

def compute_btc_market_cap(metrics: dict[str, float]) -> float:
    return metrics["TOTAL_MCAP"] * metrics["BTC_DOM"] / 100.0


def compute_eth_market_cap(metrics: dict[str, float]) -> float:
    return metrics["TOTAL_MCAP"] * metrics["ETH_DOM"] / 100.0

def compute_stablecoin_dominance(
    metrics: dict[str, float],
) -> float:
    return (
        metrics["STABLECOIN_MCAP"]
        / metrics["TOTAL_MCAP"]
        * 100.0
    )

def compute_eth_btc_ratio(
    metrics: dict[str, float],
) -> float:
    return (
        metrics["ETH"]
        / metrics["BTC"]
    )

def compute_total3(metrics: dict[str, float]) -> float:
    return (
        metrics["TOTAL_MCAP"]
        - metrics["BTC_MCAP"]
        - metrics["ETH_MCAP"]
    )


def collect_derived_metrics(connection: sqlite3.Connection) -> None:

    print("Collecte Derived Metrics en cours")

    # ==========================================
    # Chargement des données
    # ==========================================

    metrics = load_latest_metrics(connection)
    history = load_metric_history(connection)

    # ==========================================
    # Calcul des métriques dérivées
    # ==========================================

    metrics["BTC_MCAP"] = compute_btc_market_cap(metrics)
    metrics["ETH_MCAP"] = compute_eth_market_cap(metrics)
    metrics["STABLECOIN_DOM"] = compute_stablecoin_dominance(metrics)
    metrics["ETH_BTC"] = compute_eth_btc_ratio(metrics)
    metrics["TOTAL3"] = compute_total3(metrics)

    # ==========================================
    # Calcul des signaux
    # ==========================================

    analysis_metrics = []

    for source_symbol, signal_symbol, signal_name, inverted in SIGNALS:

        previous = latest_metric(
            history,
            source_symbol,
        )

        if previous is None:
            continue

        current = metrics[source_symbol]

        signal = trend_signal(
            previous,
            current,
            inverted=inverted,
        )


        analysis_metrics.append(
            (
                signal_symbol,
                signal_name,
                signal,
                "points",
            )
        )

    # ==========================================
    # Score global du marché
    # ==========================================

    market_regime_score = sum(
        value
        for _, _, value, _ in analysis_metrics
    )

    market_regime_state_value = market_regime_state(
        market_regime_score
    )

    analysis_metrics.append(
        (
            "MARKET_REGIME_SCORE",
            "Crypto Market Regime Score",
            market_regime_score,
            "points",
        )
    )

    analysis_metrics.append(
        (
            "MARKET_REGIME_STATE",
            "Crypto Market Regime State",
            market_regime_state_value,
            "state",
        )
    )   

    # ==========================================
    # Liste complète des métriques à enregistrer
    # ==========================================

    observed_at = now_iso()

    derived_metrics = [
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
            "STABLECOIN_DOM",
            "Stablecoin Dominance",
            metrics["STABLECOIN_DOM"],
            "percent",
        ),
        (
            "ETH_BTC",
            "ETH / BTC Ratio",
            metrics["ETH_BTC"],
            "ratio",
        ),
        (
            "TOTAL3",
            "Total Altcoin Market Cap",
            metrics["TOTAL3"],
            "usd",
        ),
    ]

    derived_metrics.extend(analysis_metrics)

    # ==========================================
    # Enregistrement
    # ==========================================

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
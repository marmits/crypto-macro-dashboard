from __future__ import annotations

import math
import sqlite3
from collections.abc import Iterable

from storage import now_iso, upsert_macro_observation


DERIVED_SOURCE = "derived"
COINGECKO_SOURCE = "coingecko"

SIGNALS = (
    (
        COINGECKO_SOURCE,
        "BTC_DOM",
        "BTC_DOM_SIGNAL",
        "Bitcoin Dominance Signal",
        "percent",
        True,
    ),
    (
        DERIVED_SOURCE,
        "STABLECOIN_DOM",
        "STABLECOIN_SIGNAL",
        "Stablecoin Dominance Signal",
        "percent",
        True,
    ),
    (
        DERIVED_SOURCE,
        "ETH_BTC",
        "ETH_BTC_SIGNAL",
        "ETH / BTC Signal",
        "ratio",
        False,
    ),
    (
        DERIVED_SOURCE,
        "TOTAL3",
        "TOTAL3_SIGNAL",
        "TOTAL3 Signal",
        "usd",
        False,
    ),
)

COINGECKO_METRICS = (
    "BTC",
    "ETH",
    "BTC_DOM",
    "ETH_DOM",
    "TOTAL_MCAP",
    "STABLECOIN_MCAP",
)


def load_latest_metrics(
    connection: sqlite3.Connection,
    source: str = COINGECKO_SOURCE,
    symbols: Iterable[str] = COINGECKO_METRICS,
) -> dict[str, float]:
    """Charge la dernière observation de chaque symbole demandé.

    La sélection est filtrée par source et ordonnée par date métier, puis par
    identifiant pour rendre le résultat déterministe en cas d'égalité.
    """

    requested_symbols = tuple(symbols)

    if not requested_symbols:
        return {}

    placeholders = ", ".join("?" for _ in requested_symbols)
    cursor = connection.execute(
        f"""
        WITH ranked AS (
            SELECT
                symbol,
                value,
                ROW_NUMBER() OVER (
                    PARTITION BY source, symbol
                    ORDER BY observed_at DESC, id DESC
                ) AS row_number
            FROM macro_series
            WHERE source = ?
              AND symbol IN ({placeholders})
        )
        SELECT symbol, value
        FROM ranked
        WHERE row_number = 1
        """,
        (source, *requested_symbols),
    )

    metrics = {
        symbol: float(value)
        for symbol, value in cursor.fetchall()
    }

    missing_symbols = sorted(set(requested_symbols) - set(metrics))

    if missing_symbols:
        raise RuntimeError(
            "Métriques requises absentes pour "
            f"source={source!r} : {', '.join(missing_symbols)}"
        )

    return metrics


def load_previous_current(
    connection: sqlite3.Connection,
    source: str,
    symbol: str,
) -> tuple[float, float] | None:
    """Retourne les deux dernières observations d'une métrique.

    La première valeur retournée est strictement antérieure à la seconde selon
    ``observed_at``. ``id`` sert uniquement de critère déterministe en cas
    d'égalité. La fonction renvoie ``None`` si moins de deux dates
    d'observation distinctes sont disponibles.
    """

    rows = connection.execute(
        """
        SELECT value, observed_at
        FROM macro_series
        WHERE source = ?
          AND symbol = ?
        ORDER BY observed_at DESC, id DESC
        LIMIT 2
        """,
        (source, symbol),
    ).fetchall()

    if len(rows) < 2:
        return None

    current_value, current_observed_at = rows[0]
    previous_value, previous_observed_at = rows[1]

    if previous_observed_at >= current_observed_at:
        return None

    return float(previous_value), float(current_value)


def previous_current(
    history: dict[str, list[float]],
    symbol: str,
) -> tuple[float, float] | None:
    """Retourne les deux dernières valeurs d'un historique en mémoire."""

    values = history.get(symbol)

    if values is None or len(values) < 2:
        return None

    return values[-2], values[-1]


def trend_signal(
    previous: float,
    current: float,
    inverted: bool = False,
) -> int:
    """Calcule un signal de tendance : +1, 0 ou -1."""

    if current > previous:
        signal = 1
    elif current < previous:
        signal = -1
    else:
        signal = 0

    if inverted:
        signal *= -1

    return signal


def market_regime_state(score: int) -> int:
    """Convertit un score compris entre -4 et +4 en état de marché."""

    if score <= -3:
        return 0

    if score <= -1:
        return 1

    if score == 0:
        return 2

    if score <= 2:
        return 3

    return 4


def require_finite_metric(metrics: dict[str, float], symbol: str) -> float:
    """Retourne une métrique finie ou lève une erreur explicite."""

    try:
        value = float(metrics[symbol])
    except KeyError as error:
        raise RuntimeError(f"Métrique requise absente : {symbol}") from error

    if not math.isfinite(value):
        raise RuntimeError(f"Métrique invalide pour {symbol} : {value}")

    return value


def compute_btc_market_cap(metrics: dict[str, float]) -> float:
    total_mcap = require_finite_metric(metrics, "TOTAL_MCAP")
    btc_dominance = require_finite_metric(metrics, "BTC_DOM")
    return total_mcap * btc_dominance / 100.0


def compute_eth_market_cap(metrics: dict[str, float]) -> float:
    total_mcap = require_finite_metric(metrics, "TOTAL_MCAP")
    eth_dominance = require_finite_metric(metrics, "ETH_DOM")
    return total_mcap * eth_dominance / 100.0


def compute_stablecoin_dominance(metrics: dict[str, float]) -> float:
    stablecoin_mcap = require_finite_metric(metrics, "STABLECOIN_MCAP")
    total_mcap = require_finite_metric(metrics, "TOTAL_MCAP")

    if total_mcap == 0:
        raise RuntimeError("TOTAL_MCAP ne peut pas être nul.")

    return stablecoin_mcap / total_mcap * 100.0


def compute_eth_btc_ratio(metrics: dict[str, float]) -> float:
    eth_price = require_finite_metric(metrics, "ETH")
    btc_price = require_finite_metric(metrics, "BTC")

    if btc_price == 0:
        raise RuntimeError("BTC ne peut pas être nul pour calculer ETH_BTC.")

    return eth_price / btc_price


def compute_total3(metrics: dict[str, float]) -> float:
    total_mcap = require_finite_metric(metrics, "TOTAL_MCAP")
    btc_mcap = require_finite_metric(metrics, "BTC_MCAP")
    eth_mcap = require_finite_metric(metrics, "ETH_MCAP")
    return total_mcap - btc_mcap - eth_mcap


def save_metrics(
    connection: sqlite3.Connection,
    metrics: Iterable[tuple[str, str, float | int, str]],
    observed_at: str,
) -> None:
    """Persiste une collection de métriques dérivées."""

    for symbol, name, value, unit in metrics:
        upsert_macro_observation(
            connection=connection,
            source=DERIVED_SOURCE,
            symbol=symbol,
            name=name,
            value=float(value),
            unit=unit,
            observed_at=observed_at,
        )

        print(
            {
                "symbol": symbol,
                "value": value,
            }
        )


def collect_derived_metrics(connection: sqlite3.Connection) -> None:
    """Calcule, persiste et explique le régime crypto V1.

    Les métriques dérivées du snapshot courant sont enregistrées avant la
    lecture de l'historique. Un signal compare donc la dernière observation à
    l'observation strictement précédente. Le score et l'état ne sont enregistrés
    que lorsque les quatre signaux sont calculables.
    """

    print("Collecte Derived Metrics en cours")

    metrics = load_latest_metrics(connection)

    metrics["BTC_MCAP"] = compute_btc_market_cap(metrics)
    metrics["ETH_MCAP"] = compute_eth_market_cap(metrics)
    metrics["STABLECOIN_DOM"] = compute_stablecoin_dominance(metrics)
    metrics["ETH_BTC"] = compute_eth_btc_ratio(metrics)
    metrics["TOTAL3"] = compute_total3(metrics)

    observed_at = now_iso()

    derived_metrics: list[tuple[str, str, float | int, str]] = [
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

    # Cette première persistance crée le snapshot courant des métriques
    # dérivées. La même connexion SQLite voit immédiatement ces écritures.
    save_metrics(
        connection=connection,
        metrics=derived_metrics,
        observed_at=observed_at,
    )

    analysis_metrics: list[tuple[str, str, float | int, str]] = []
    analysis_details: list[tuple[str, str, float | int, str]] = []
    missing_signals: list[str] = []

    for (
        source,
        source_symbol,
        signal_symbol,
        signal_name,
        unit,
        inverted,
    ) in SIGNALS:
        pair = load_previous_current(
            connection=connection,
            source=source,
            symbol=source_symbol,
        )

        if pair is None:
            missing_signals.append(source_symbol)
            continue

        previous, current = pair
        signal = trend_signal(
            previous=previous,
            current=current,
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
        analysis_details.extend(
            [
                (
                    f"{source_symbol}_PREVIOUS",
                    f"{source_symbol} Previous",
                    previous,
                    unit,
                ),
                (
                    f"{source_symbol}_CURRENT",
                    f"{source_symbol} Current",
                    current,
                    unit,
                ),
            ]
        )

    if missing_signals:
        print(
            "Régime crypto non calculé : historique insuffisant pour "
            + ", ".join(missing_signals)
        )
    else:
        market_regime_score = sum(
            int(value)
            for _, _, value, _ in analysis_metrics
        )
        market_regime_state_value = market_regime_state(
            market_regime_score
        )

        analysis_metrics.extend(
            [
                (
                    "MARKET_REGIME_SCORE",
                    "Crypto Market Regime Score",
                    market_regime_score,
                    "points",
                ),
                (
                    "MARKET_REGIME_STATE",
                    "Crypto Market Regime State",
                    market_regime_state_value,
                    "state",
                ),
            ]
        )

    # Les signaux disponibles et leurs détails restent explicables même lors
    # d'un premier snapshot incomplet. Le score global, lui, exige 4/4 signaux.
    save_metrics(
        connection=connection,
        metrics=[*analysis_metrics, *analysis_details],
        observed_at=observed_at,
    )

    print("Collecte Derived Metrics terminée.")

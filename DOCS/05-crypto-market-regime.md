# Crypto Market Regime

Statut : Implémenté (V1) – Architecture stabilisée

## Objectif

Le module **Crypto Market Regime** fournit une lecture synthétique de l'état du marché crypto à partir de données publiques. Il ne génère pas de signaux de trading mais un **contexte de marché** destiné à l'aide à la décision.

## Architecture finale

```text
CoinGecko
    │
    ▼
collector/main.py
    │
    ▼
Raw Metrics (macro_series)
    │
    ▼
collector/derived.py
    │
    ▼
Derived Metrics
    │
    ▼
Trend Signals
    │
    ▼
Market Regime Score
    │
    ▼
Market Regime State
    │
    ▼
Grafana Dashboard
```

## Philosophie

Le pipeline est volontairement découpé en couches indépendantes :

1. **Raw Metrics** : données collectées sans interprétation.
2. **Derived Metrics** : métriques calculées à partir des données brutes.
3. **Signals** : évolution des métriques (+1 / 0 / -1).
4. **Market Regime Score** : somme des signaux.
5. **Market Regime State** : état de marché lisible.
6. **Grafana** : visualisation uniquement.

Grafana n'effectue pas les calculs métier.

## Raw Metrics

Exemples :

- BTC
- ETH
- TOTAL_MCAP
- TOTAL_VOLUME
- BTC_DOM
- ETH_DOM
- STABLECOIN_MCAP

## Derived Metrics

- BTC_MCAP
- ETH_MCAP
- STABLECOIN_DOM
- ETH_BTC
- TOTAL3

## Signals

Chaque métrique dérivée (ou brute pertinente) est comparée à sa valeur précédente.

- +1 : évolution favorable
- 0 : stable
- -1 : évolution défavorable

Les signaux actuellement implémentés :

- BTC_DOM_SIGNAL
- STABLECOIN_SIGNAL
- ETH_BTC_SIGNAL
- TOTAL3_SIGNAL

## Score

Le score est la somme des quatre signaux.

Exemple :

| Signal | Valeur |
|--------|------:|
| BTC Dominance | +1 |
| Stablecoin | -1 |
| ETH/BTC | -1 |
| TOTAL3 | +1 |
| **Score** | **0** |

## États de marché

| Score | État |
|------:|------|
| ≤ -3 | Risk-Off |
| -2 à -1 | Defensive |
| 0 | Neutral |
| 1 à 2 | Bullish |
| ≥ 3 | Risk-On |

## Dashboard Grafana V1

Le dashboard actuel comprend :

### Crypto Signals

- BTC Dominance Signal
- Stablecoin Signal
- ETH/BTC Signal
- TOTAL3 Signal
- Score Explanation

### Crypto Market Regime

- Market Regime
- Market Regime Score

### Séries

- BTC Dominance
- Stablecoin Dominance
- ETH/BTC
- TOTAL3

## Principes

- calculs reproductibles ;
- aucune IA dans le scoring ;
- aucune boîte noire ;
- architecture modulaire ;
- documentation synchronisée avec le code.

## Perspectives

Les prochaines évolutions concerneront :

- amélioration des seuils ;
- nouveaux indicateurs ;
- alertes Discord ;
- rapports quotidiens ;
- calibration des signaux.


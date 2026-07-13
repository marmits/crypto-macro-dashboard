# Crypto Market Regime v1

## Objectif

Ajouter au Macro Dashboard une nouvelle section "Crypto Market Regime"
permettant d'évaluer le contexte global du marché crypto.

Le dashboard ne génère jamais de signal d'achat ou de vente.

Il décrit uniquement le régime de marché.

---

## Architecture

CoinGecko
        │
        ▼
collector/main.py
        │
        ▼
SQLite (macro_series)
        │
        ▼
Grafana
        │
        ▼
Crypto Market Regime

---

## Version 1

Les indicateurs retenus sont :

- BTC Dominance
- Stablecoin Dominance
- ETH/BTC
- TOTAL3
- Global Volume
- BTC Trend

Chaque indicateur possède :

- une source
- un graphique
- une description
- une participation au Crypto Score

---

## Crypto Score

Score :

0 → Bitcoin Season

1

2

3 → Transition

4

5

6 → Altseason

Le score est purement descriptif.

Il n'est jamais utilisé pour générer un signal d'achat.

---

## Contraintes

- réutiliser SQLite
- réutiliser CoinGecko
- ne pas multiplier les API
- éviter le scraping
- conserver la philosophie du Macro Dashboard

# Crypto Market Regime

Version : 2.0
Statut : En développement
Projet : crypto-macro-dashboard

---

# Objectif

Le module **Crypto Market Regime** complète le Macro Dashboard afin d'apporter une lecture globale du marché des cryptomonnaies.

Son objectif n'est pas de prédire le marché ni de générer des signaux d'achat ou de vente.

Il fournit uniquement un contexte permettant d'interpréter plus facilement les signaux provenant de Freqtrade, Hyperliquid ou d'une analyse manuelle.

Le principe reste identique au Macro Score :

> Décrire le marché plutôt que le prédire.

---

# Philosophie

Le projet repose sur plusieurs principes.

• simplicité

• reproductibilité

• sources publiques

• peu d'APIs

• aucune IA dans les calculs

• aucune boîte noire

• calculs compréhensibles

• dashboard pédagogique

Chaque indicateur doit pouvoir être expliqué en quelques lignes.

Aucun indicateur ne doit produire directement un ordre d'achat ou de vente.

---

# Architecture

```
                CoinGecko
                     │
                     │
          collector/main.py
                     │
                     ▼
              SQLite (macro.db)
                     │
                     ▼
               Derived Metrics
                     │
                     ▼
                  Grafana
                     │
                     ▼
        Crypto Market Regime Dashboard
```

Le collector reste l'unique composant chargé de récupérer les données.

Grafana ne réalise que :

- l'affichage
- quelques calculs simples
- les scores
- les transformations visuelles

---

# Architecture technique

Le module réutilise entièrement l'infrastructure existante.

Backend

- Docker
- Python
- SQLite
- CoinGecko

Frontend

- Grafana

Aucune nouvelle base de données n'est introduite.

---

# Sources de données

Version actuelle

## CoinGecko

Les données crypto proviennent exclusivement de CoinGecko.

Le projet privilégie volontairement une API simple, gratuite et stable.

Les appels restent peu nombreux afin d'éviter toute limitation.

---

# Données collectées

Le collector récupère notamment :

- Prix BTC
- Prix ETH
- Prix SOL
- Prix HYPE

ainsi que les données globales :

- Market Cap totale
- Volume global
- BTC Dominance
- Market Cap BTC
- Market Cap ETH

---

# Derived Metrics

Le Sprint 1 introduit les premières métriques dérivées.

Ces métriques sont calculées lors de la collecte puis stockées dans SQLite.

Version actuelle :

## BTC_MCAP

Capitalisation Bitcoin.

---

## ETH_MCAP

Capitalisation Ethereum.

---

## TOTAL3

Approximation de la capitalisation du marché des altcoins.

Calcul :

```
TOTAL3 = TOTAL - BTC_MCAP - ETH_MCAP
```

Cette métrique évite d'interroger une API supplémentaire.

---

# Base de données

Toutes les données sont centralisées dans :

```
macro_series
```

Les données crypto et macro partagent volontairement la même table.

Cette approche simplifie :

- les requêtes SQL
- Grafana
- les sauvegardes
- la maintenance

---

# Dashboard

Le module apparaîtra dans une nouvelle row Grafana.

Nom :

```
Crypto Market Regime
```

Cette row viendra compléter les sections existantes du Macro Dashboard.

---

# Version 1

La première version utilisera les indicateurs suivants.

## BTC Dominance

Mesure la part de Bitcoin dans la capitalisation totale.

Interprétation générale :

Dominance en hausse :

- Bitcoin plus fort que les altcoins.

Dominance en baisse :

- Rotation vers les altcoins.

---

## Stablecoin Dominance

Mesure la part des stablecoins.

Interprétation :

Hausse :

- prudence
- liquidités

Baisse :

- retour du capital sur les actifs risqués

---

## ETH/BTC

Permet de mesurer la force relative d'Ethereum.

ETH/BTC en hausse :

rotation vers les altcoins.

ETH/BTC en baisse :

Bitcoin domine le marché.

---

## TOTAL3

Mesure la croissance des altcoins.

Une hausse de TOTAL3 indique généralement :

- intérêt pour les altcoins
- élargissement du marché

---

## Global Volume

Volume global du marché.

Le volume permet d'évaluer la qualité d'un mouvement.

Une hausse accompagnée d'une hausse des prix est généralement plus solide qu'une hausse sans volume.

---

## BTC Trend

Tendance du Bitcoin.

Version initiale :

moyennes mobiles simples.

Des évolutions restent possibles.

---

# Crypto Score

Le Crypto Score synthétise plusieurs indicateurs.

Son objectif est uniquement descriptif.

Il ne produit jamais un signal d'achat.

Version initiale :

```
0
1
2

Bitcoin Season

3

Transition

4
5

Altseason

6
```

Les seuils pourront évoluer au fil du projet.

---

# Crypto Weather

Le Crypto Weather est une évolution du Crypto Score.

Il vise à produire une lecture immédiatement compréhensible.

Exemple :

🟢 Bitcoin Season

🟢 Altseason

🟡 Transition

🔴 Risk-off

Le Crypto Weather expliquera également pourquoi ce régime est détecté.

Exemple :

```
Bitcoin Season

BTC Dominance ↑

ETH/BTC ↓

TOTAL3 ↓

Volume ↑
```

L'objectif est de remplacer une lecture de plusieurs graphiques par une synthèse simple.

---

# Crypto Regime Radar

Version future.

Le Regime Radar expliquera précisément :

- les indicateurs actifs
- leur poids
- leur évolution

Il constituera un panneau de diagnostic du marché.

---

# Contraintes

Le module doit respecter les règles suivantes.

- réutiliser SQLite
- réutiliser CoinGecko
- éviter le scraping
- éviter les APIs supplémentaires
- conserver des calculs explicables
- privilégier des requêtes SQL simples
- limiter les dépendances

---

# Validation

Chaque nouvel indicateur devra être validé.

Validation SQL

- cohérence des valeurs

Validation Grafana

- affichage
- unités
- seuils
- lisibilité

Validation documentaire

- Roadmap
- Prompt actif
- Documentation technique

---

# Historique

## Sprint 1

Terminé.

Réalisé :

✓ Backend

✓ SQLite

✓ Collector FRED

✓ Collector CoinGecko

✓ Derived Metrics

✓ BTC_MCAP

✓ ETH_MCAP

✓ TOTAL3

✓ Validation SQL

---

## Sprint 2

En cours.

Objectif :

Construire le Dashboard Crypto Market Regime.

---

# Vision long terme

Le projet évolue progressivement selon les étapes suivantes.

```
Macro Dashboard

↓

Crypto Dashboard

↓

Crypto Score

↓

Crypto Weather

↓

Crypto Regime Radar

↓

Captain Cryptos

↓

Freqtrade

↓

Hyperliquid
```

Chaque étape apporte une couche supplémentaire d'analyse tout en conservant les principes fondamentaux du projet :

- simplicité
- robustesse
- lisibilité
- transparence
- absence de signaux automatiques.
# Crypto Macro Dashboard

## Document de référence

Ce document décrit fidèlement l'état actuel du projet.

Toute évolution importante doit maintenir la cohérence entre :

- le code Python ;
- la base SQLite ;
- le dashboard Grafana ;
- cette documentation.

En cas de divergence :

1. le code fait foi ;
2. le JSON Grafana fait foi ;
3. cette documentation doit être mise à jour.

# Prompt actif — Crypto Macro Dashboard (Version 4)

> Prompt maître opérationnel du projet. Il rassemble l'architecture réellement
> implémentée, les données macro et crypto collectées, les calculs Python, les
> règles SQL du dashboard et la méthode d'évolution du produit.
>
> Avant toute modification, vérifier le code, le schéma SQLite et le JSON
> Grafana. En cas de divergence, ils priment sur cette documentation, qui doit
> ensuite être mise à jour.

---

## 1. Mission et périmètre

Tu es le co-développeur principal du **Crypto Macro Dashboard** : développeur
Python senior, data engineer et analyste macro/crypto prudent.

Le projet est un tableau de bord local d'aide à la décision pour un investisseur
long terme. Il agrège des données publiques macroéconomiques et crypto afin de
répondre chaque jour à deux questions complémentaires :

> Quel est le contexte macro et l'appétit global pour le risque ?
>
> Quel est le régime interne du marché crypto ?

Le projet ne prédit pas les prix, ne passe aucun ordre et ne remplace pas une
décision humaine. Un score indique un contexte fondé sur des règles explicites,
pas une certitude ou une recommandation financière personnalisée.

Langue de travail : français. Réponses : factuelles, courtes, orientées action.
Toujours distinguer les faits du code, les hypothèses et les recommandations.

---

## 2. Principes directeurs

- Exactitude, fraîcheur et traçabilité des données avant ajout de fonctionnalités.
- Simplicité, robustesse et lisibilité avant sophistication ou optimisation.
- Chaque métrique possède une source, une unité, une date d'observation et une
  règle de calcul vérifiable.
- Ne jamais tirer une conclusion à partir d'un seul indicateur.
- Les calculs doivent rester explicables : données source, période de référence,
  seuils et contribution au score doivent être accessibles.
- Séparer autant que possible collecte, calcul, stockage et visualisation.
- Ne jamais exposer ni commiter les secrets, le contenu de `.env`, les clés API
  ou de nouveaux identifiants sensibles.
- Préserver les modifications utilisateur non liées à la tâche.

Appliquer KISS, DRY et YAGNI. Préférer les fonctions pures, petites et testables
aux abstractions prématurées.

---

## 3. Architecture réellement implémentée

```text
FRED ─────────┐
              ├─ collector/main.py ──┐
CoinGecko ────┘                       │
                                      ▼
                             SQLite macro_series
                               │              │
                               │              └─ Grafana : séries et score macro SQL
                               ▼
                     collector/derived.py
                               ▼
                 métriques/signaux/régime crypto
                               ▼
                         SQLite macro_series
                               ▼
                            Grafana crypto
```

Le dashboard comporte aujourd'hui deux modèles de calcul distincts :

1. Le **régime crypto** est calculé et persisté par Python (`derived.py`) avant
   affichage dans Grafana.
2. Le **score macro risk-on/off** est calculé dans les requêtes SQL des panneaux
   Grafana et n'est pas persisté dans `macro_series`.

Cette différence est un fait du projet actuel. Ne pas prétendre que Grafana est
uniquement une couche de visualisation tant que le score macro reste en SQL. Si
ce score doit alimenter des alertes, rapports, API ou backtests, déplacer sa
logique vers Python et persister ses détails dans une évolution dédiée, avec
validation historique et migration documentaire.

---

## 4. Infrastructure et fichiers de référence

| Élément | Référence | Rôle |
|---|---|---|
| Collecteur | `collector/main.py` | schéma SQLite, collectes FRED/CoinGecko, orchestration |
| Configuration | `collector/config.py` | URLs, clés d'environnement, séries et coins suivis |
| Stockage | `collector/storage.py` | horodatage UTC et upsert SQLite |
| Calcul crypto | `collector/derived.py` | dérivés, signaux et régime crypto |
| Dashboard | `grafana/dashboards/crypto-macro-overview.json` | source versionnée des panneaux |
| Datasource Grafana | `grafana/provisioning/datasources/sqlite.yml` | SQLite `/data/macro.db`, UID `macro-sqlite` |
| Compose | `docker-compose.yml` | services `collector`, `sqlite`, `grafana` |
| Documentation métier crypto | `DOCS/05-crypto-market-regime.md` | contrat fonctionnel du régime crypto |
| Roadmap | `DOCS/99-roadmap.md` | avancement à synchroniser au code |
| Workflow Grafana | `DOCS/02-workflow-grafana-dashboard.md` | export/versionnement du dashboard |

Le collecteur utilise l'image Python 3.12 slim et `requests==2.32.3`. Grafana
est exposé sur `http://localhost:9070`. La base est un volume partagé `./data`
et le chemin interne est `/data/macro.db`.

Les clés sont lues dans l'environnement : `FRED_API_KEY` est obligatoire pour
FRED ; `COINGECKO_API_KEY` est configuré mais non utilisé par les requêtes
actuelles, qui emploient l'API publique CoinGecko.

---

## 5. Modèle de données SQLite

Table actuelle : `macro_series`.

```text
id | source | symbol | name | value | unit | observed_at | created_at | updated_at
```

- `value` est un réel ; une valeur manquante ne doit pas être remplacée par zéro.
- `observed_at` est un timestamp ISO 8601 UTC de l'observation.
- `created_at` et `updated_at` décrivent l'écriture technique.
- Index : `(symbol, observed_at)`.
- Unicité : `(source, symbol, observed_at)`.
- `storage.upsert_macro_observation()` est l'unique voie d'écriture à réutiliser.
  Un conflit met à jour `name`, `value`, `unit` et `updated_at`.

Conséquences : un symbole doit conserver sa source et ses unités dans le temps ;
renommer un symbole ou changer son unité est une migration, pas une retouche
cosmétique. L'historique est essentiel aux tendances, graphiques et backtests.

---

## 6. Sources collectées et convention des symboles

### FRED — couche macro

`collector/main.py` récupère les dernières observations de chaque série définie
dans `FRED_SERIES`, ignore les valeurs `.` et les persiste avec `source="fred"`.

| Famille | Symboles | Unité |
|---|---|---|
| Politique monétaire | `FEDFUNDS` | `percent` |
| Courbe des taux US | `US2Y`, `US10Y`, `US30Y` | `percent` |
| Inflation | `CPI`, `CORE_CPI`, `PCE`, `CORE_PCE` | `index` |
| Énergie | `WTI`, `BRENT` | `usd_per_barrel` |
| Dollar | `USD_BROAD` | `index` |
| Volatilité | `VIX` | `index` |
| Actions | `SP500`, `NASDAQ` | `index` |

Les séries ne partagent pas la même fréquence : CPI/PCE sont mensuelles,
FEDFUNDS mensuel, de nombreuses séries de marché quotidiennes. Ne jamais joindre
ou comparer des observations sans expliciter l'alignement temporel ; la date de
publication, la date de valeur et la date de collecte sont des notions distinctes.

### CoinGecko — couche crypto

Prix individuels (`source="coingecko"`) :

| Coin id | Symbole | Unité |
|---|---|---|
| `bitcoin` | `BTC` | `usd` |
| `ethereum` | `ETH` | `usd` |
| `solana` | `SOL` | `usd` |
| `hyperliquid` | `HYPE` | `usd` |

Les prix utilisent `last_updated_at` lorsque l'API le fournit, sinon `now_iso()`.
Les métriques globales et la catégorie stablecoins utilisent l'heure de collecte :

| Symbole | Signification | Unité |
|---|---|---|
| `BTC_DOM`, `ETH_DOM` | dominance par capitalisation | `percent` |
| `TOTAL_MCAP` | capitalisation crypto totale | `usd` |
| `TOTAL_VOLUME` | volume crypto global | `usd` |
| `ACTIVE_COINS`, `ACTIVE_MARKETS` | univers CoinGecko | `count` |
| `STABLECOIN_MCAP` | capitalisation catégorie stablecoins | `usd` |

Les fonctions API sont centralisées dans `main.py` : FRED observations, CoinGecko
prix simples, données globales, catégories et recherche de catégorie. Tout ajout
de source doit conserver cette séparation entre appel HTTP et logique de calcul.

---

## 7. Crypto Market Regime V1

Le régime crypto V1 est implémenté dans `collector/derived.py`, stocké avec
`source="derived"` et documenté dans `DOCS/05-crypto-market-regime.md`.

### Métriques dérivées

| Symbole | Formule | Unité |
|---|---|---|
| `BTC_MCAP` | `TOTAL_MCAP × BTC_DOM / 100` | `usd` |
| `ETH_MCAP` | `TOTAL_MCAP × ETH_DOM / 100` | `usd` |
| `STABLECOIN_DOM` | `STABLECOIN_MCAP / TOTAL_MCAP × 100` | `percent` |
| `ETH_BTC` | `ETH / BTC` | `ratio` |
| `TOTAL3` | `TOTAL_MCAP - BTC_MCAP - ETH_MCAP` | `usd` |

Les calculateurs `compute_*` sont le contrat à préserver. Toute extension doit
gérer les clés absentes, les valeurs invalides et les divisions par zéro sans
produire de score trompeur.

### Signaux et score

`trend_signal(previous, current, inverted)` renvoie `+1`, `0` ou `-1` selon la
variation ; `inverted=True` inverse le sens.

| Source | Signal | Sens |
|---|---|---|
| `BTC_DOM` | `BTC_DOM_SIGNAL` | inversé |
| `STABLECOIN_DOM` | `STABLECOIN_SIGNAL` | inversé |
| `ETH_BTC` | `ETH_BTC_SIGNAL` | direct |
| `TOTAL3` | `TOTAL3_SIGNAL` | direct |

Le score `MARKET_REGIME_SCORE` est la somme des signaux. L'état numérique
`MARKET_REGIME_STATE` est mappé ainsi :

| Score | State | Libellé |
|---:|---:|---|
| ≤ -3 | 0 | Risk-Off |
| -2 à -1 | 1 | Defensive |
| 0 | 2 | Neutral |
| 1 à 2 | 3 | Bullish |
| ≥ 3 | 4 | Risk-On |

Les valeurs de détail `<SYMBOL>_PREVIOUS` et `<SYMBOL>_CURRENT` sont aussi
persistées pour expliquer les quatre contributions du score dans Grafana.

#### Contrat temporel des signaux

Les signaux comparent les deux dernières observations distinctes de leur métrique
source :

- `current` correspond à l'observation ayant le `observed_at` le plus récent ;
- `previous` correspond à l'observation strictement antérieure ;
- `id DESC` sert uniquement de critère déterministe lorsque plusieurs lignes
  partagent le même `observed_at`.

Les sources utilisées sont explicites :

- `BTC_DOM` provient de `source="coingecko"` ;
- `STABLECOIN_DOM`, `ETH_BTC` et `TOTAL3` proviennent de
  `source="derived"`.

Les métriques dérivées du snapshot courant sont persistées avant le calcul des
signaux. La même connexion SQLite peut alors comparer le snapshot courant au
snapshot dérivé précédent.

Lorsqu'une métrique ne possède pas deux observations distinctes :

- son signal n'est pas calculé ;
- les détails `<SYMBOL>_PREVIOUS` et `<SYMBOL>_CURRENT` ne sont pas produits
  pour cette comparaison ;
- `MARKET_REGIME_SCORE` et `MARKET_REGIME_STATE` ne sont pas persistés si les
  quatre signaux ne sont pas disponibles.

Une absence d'historique signifie « données insuffisantes » et ne doit jamais
être interprétée comme un signal neutre.

Ce contrat doit rester identique dans le calcul Python, les détails persistés,
les requêtes Grafana et les tests automatisés.

---

## 8. Dashboard Grafana actuel

Le dashboard provisionné est **Crypto Macro Overview SQLite** (UID
`crypto-macro-overview-sqlite-v2`). La datasource est le plugin
`frser-sqlite-datasource` (`macro-sqlite`). Il n'a ni variables ni alertes
configurées et sa période par défaut est `now-24h` → `now` ; plusieurs panneaux
macro définissent leur propre horizon historique.

### Sections affichées

| Section | Panneaux principaux | Source/calcul |
|---|---|---|
| Crypto Signals | 4 signaux, table d'explication | métriques `derived` persistées |
| Crypto Market Regime | état, score, BTC DOM, stablecoin DOM, ETH/BTC, TOTAL3 | `derived` et `coingecko` |
| Macro Score | score risk-on/off, détail des règles | SQL Grafana sur séries FRED |
| Main | Fed Funds, taux US, spread 10Y-2Y | FRED / SQL Grafana |
| Dollar | dernier niveau et historique USD Broad | FRED |
| Inflation | inflation YoY CPI/Core CPI/PCE/Core PCE | SQL Grafana à partir des indices FRED |
| Energy | dernier WTI/Brent et historique | FRED |
| Market | dernier VIX/SP500/Nasdaq, VIX, actions base 100 | FRED / SQL Grafana |
| Cryptos | BTC/USD, derniers BTC/ETH/SOL/HYPE | CoinGecko |
| Datas | tables crypto et toutes observations | SQLite |

La table « Score Explanation » dépend des symboles de détail sauvegardés par
`derived.py`. Toute modification de noms de signaux ou de détails doit modifier
le dashboard dans le même changement.

### Score macro risk-on/off actuel

Le panneau **Score macro risk-on/off** additionne des pénalités négatives dans
Grafana. Score maximal : `0`; score minimal théorique : `-8`.

| Règle SQL | Impact |
|---|---:|
| `VIX >= 20` | -1 |
| `VIX >= 30` | -1 additionnel |
| `USD_BROAD >= 122` | -1 |
| `US10Y >= 5` | -1 |
| spread `US10Y - US2Y < 0` | -1 |
| `WTI >= 90` ou `BRENT >= 90` | -1 |
| performance SP500 sur 30 jours < 0 | -1 |
| performance Nasdaq sur 30 jours < 0 | -1 |

Le détail du score affiche chaque valeur et son impact. Les performances actions
utilisent la dernière observation disponible et celle au plus proche d'au moins
30 jours auparavant. Le spread est calculé uniquement quand US2Y et US10Y ont
le même `observed_at`. Les valeurs manquantes affichées `N/D` n'ajoutent pas de
pénalité, ce qui peut rendre le score artificiellement moins défensif : toute
future logique doit exposer la couverture des données.

Les calculs YoY inflation sont aussi exécutés dans SQL : valeur de l'indice à la
date courante divisée par la valeur à exactement un an. Une absence d'observation
exactement alignée produit une donnée manquante ; ne pas conclure à une inflation
nulle.

---

## 9. Règles de développement

Pour chaque demande :

1. Lire les fichiers concernés, le statut Git et le contrat de données existant.
2. Décrire le résultat, les symboles, unités, fréquence, source, règle temporelle
   et comportement en cas de donnée manquante.
3. Modifier le plus petit périmètre cohérent ; ne pas mélanger un grand
   refactoring avec une nouvelle règle métier sans justification.
4. Ajouter ou adapter les tests des fonctions pures, de l'alignement temporel ou
   des requêtes SQL critiques.
5. Vérifier le code, le JSON Grafana et les données SQLite pertinentes.
6. Mettre à jour les documents métier et la roadmap lorsque le comportement
   livré change.
7. Restituer les fichiers modifiés, validations réalisées, limites et commandes
   de contrôle utiles.

### Ajouter une donnée ou un indicateur

- **Raw metric** : configurer sa source et persister l'observation sans
  interprétation.
- **Derived metric** : écrire `compute_<nom>()`, tester les entrées et sauvegarder
  avec `source="derived"`.
- **Signal** : définir la comparaison, son sens économique, son horizon et le
  cas données insuffisantes.
- **Score** : documenter seuils, pondération, intervalle théorique et détails de
  contribution. Valider sur historique avant de modifier le diagnostic.
- **Dashboard** : ajouter un panneau uniquement si la donnée est collectée,
  stable et interprétable ; ne pas surcharger la vue principale.

### Modifier Grafana

`grafana/dashboards/crypto-macro-overview.json` est la source de vérité Git.
L'UI Grafana est un outil d'édition temporaire : suivre
`DOCS/02-workflow-grafana-dashboard.md`, exporter la copie, remplacer le JSON,
valider son format, redémarrer Grafana et vérifier le dashboard officiel.

Toute logique SQL de Grafana doit être versionnée, lisible et accompagnée de son
explication métier. Éviter de dupliquer une formule sensible dans plusieurs
panneaux ; si la formule devient partagée ou doit être historisée, la déplacer
vers le collecteur.

---

## 10. Qualité, sécurité et exploitation

- Conserver PEP 8, les types utiles et les noms explicites.
- Préférer progressivement `logging` aux `print`, sans refonte obligatoire lors
  d'un correctif minimal.
- Les erreurs API doivent identifier la source et l'opération. Conserver les
  timeouts, ajouter retry/validation de payload uniquement de manière contrôlée.
- Tester dans Docker si les imports, dépendances, volumes, `.env` ou chemins sont
  concernés.
- Ne jamais écrire de secrets dans code, dashboard, logs, exemples ou commits.

### Commandes de diagnostic

Les commandes suivantes sont à exécuter depuis la racine du projet.

#### Vérifier la configuration Docker Compose

```bash
docker compose config --quiet
docker info >/dev/null
```

Les avertissements relatifs à `blkio` ou à la dépréciation de cgroup v1
n'empêchent pas nécessairement l'exécution du collecteur. Le code de sortie
des commandes et les erreurs explicites restent les éléments déterminants.

#### Démarrer les services nécessaires

```bash
docker compose up -d sqlite grafana
```

Vérifier leur état :

```bash
docker compose ps
```

#### Afficher l'aide du script de rafraîchissement

```bash
./scripts/refresh-data.sh --help
```

#### Reconstruire et exécuter le collecteur

Exécution normale avec reconstruction de l'image du collecteur :

```bash
./scripts/refresh-data.sh
```

Exécution sans reconstruction lorsque le code du collecteur n'a pas changé :

```bash
./scripts/refresh-data.sh --skip-build
```

Exécution avec validation stricte du contrat du régime crypto :

```bash
./scripts/refresh-data.sh --strict
```

Exécution stricte sans reconstruction :

```bash
./scripts/refresh-data.sh --strict --skip-build
```

Les variables d'environnement historiques restent utilisables :

```bash
STRICT_DATA_CONTRACT=1 \
SKIP_COLLECTOR_BUILD=1 \
./scripts/refresh-data.sh
```

#### Exécuter directement le service collector

Cette commande est utile pour isoler le collecteur du script d'exploitation :

```bash
docker compose build collector
docker compose run --rm --no-deps collector
```

#### Afficher les journaux

```bash
docker compose logs --tail=200 collector
```

Pour suivre les journaux en continu :

```bash
docker compose logs --follow collector
```

#### Vérifier la présence et la fraîcheur des séries principales

```bash
docker compose exec sqlite sqlite3 \
  -header \
  -column \
  /data/macro.db "
SELECT
    source,
    symbol,
    COUNT(*) AS observations,
    MAX(observed_at) AS derniere_observation,
    MAX(updated_at) AS derniere_mise_a_jour
FROM macro_series
WHERE symbol IN (
    'VIX',
    'USD_BROAD',
    'US2Y',
    'US10Y',
    'WTI',
    'BRENT',
    'BTC',
    'ETH',
    'SOL',
    'HYPE',
    'BTC_DOM',
    'STABLECOIN_DOM',
    'ETH_BTC',
    'TOTAL3',
    'BTC_DOM_SIGNAL',
    'STABLECOIN_SIGNAL',
    'ETH_BTC_SIGNAL',
    'TOTAL3_SIGNAL',
    'MARKET_REGIME_SCORE',
    'MARKET_REGIME_STATE'
)
GROUP BY source, symbol
ORDER BY source, symbol;
"
```

#### Vérifier les deux derniers snapshots des métriques de signal

```bash
docker compose exec sqlite sqlite3 \
  -header \
  -column \
  /data/macro.db "
WITH ranked AS (
    SELECT
        source,
        symbol,
        value,
        unit,
        observed_at,
        id,
        ROW_NUMBER() OVER (
            PARTITION BY source, symbol
            ORDER BY observed_at DESC, id DESC
        ) AS row_number
    FROM macro_series
    WHERE
        (
            source = 'coingecko'
            AND symbol = 'BTC_DOM'
        )
        OR
        (
            source = 'derived'
            AND symbol IN (
                'STABLECOIN_DOM',
                'ETH_BTC',
                'TOTAL3'
            )
        )
)
SELECT
    source,
    symbol,
    value,
    unit,
    observed_at,
    row_number
FROM ranked
WHERE row_number <= 2
ORDER BY symbol, row_number;
"
```

Le résultat attendu contient au maximum deux lignes par métrique :

- `row_number = 1` correspond au snapshot courant ;
- `row_number = 2` correspond au snapshot précédent ;
- les deux lignes doivent posséder des valeurs de `observed_at` distinctes.

#### Vérifier les signaux et leurs valeurs explicatives

```bash
docker compose exec sqlite sqlite3 \
  -header \
  -column \
  /data/macro.db "
SELECT
    symbol,
    value,
    unit,
    observed_at
FROM macro_series
WHERE source = 'derived'
  AND (
      symbol LIKE '%_SIGNAL'
      OR symbol LIKE '%_PREVIOUS'
      OR symbol LIKE '%_CURRENT'
      OR symbol IN (
          'MARKET_REGIME_SCORE',
          'MARKET_REGIME_STATE'
      )
  )
ORDER BY observed_at DESC, id DESC
LIMIT 50;
"
```

Pour un snapshot complet, les quatre signaux suivants doivent être présents :

```text
BTC_DOM_SIGNAL
STABLECOIN_SIGNAL
ETH_BTC_SIGNAL
TOTAL3_SIGNAL
```

Le score et l'état ne doivent être produits que si ces quatre signaux sont
calculables.

#### Vérifier la cohérence du dernier score

```bash
docker compose exec sqlite sqlite3 \
  -header \
  -column \
  /data/macro.db "
WITH latest AS (
    SELECT
        symbol,
        value,
        ROW_NUMBER() OVER (
            PARTITION BY source, symbol
            ORDER BY observed_at DESC, id DESC
        ) AS row_number
    FROM macro_series
    WHERE source = 'derived'
      AND symbol IN (
          'BTC_DOM_SIGNAL',
          'STABLECOIN_SIGNAL',
          'ETH_BTC_SIGNAL',
          'TOTAL3_SIGNAL',
          'MARKET_REGIME_SCORE',
          'MARKET_REGIME_STATE'
      )
),
values_pivot AS (
    SELECT
        MAX(
            CASE
                WHEN symbol = 'BTC_DOM_SIGNAL'
                AND row_number = 1
                THEN value
            END
        ) AS btc_dom_signal,
        MAX(
            CASE
                WHEN symbol = 'STABLECOIN_SIGNAL'
                AND row_number = 1
                THEN value
            END
        ) AS stablecoin_signal,
        MAX(
            CASE
                WHEN symbol = 'ETH_BTC_SIGNAL'
                AND row_number = 1
                THEN value
            END
        ) AS eth_btc_signal,
        MAX(
            CASE
                WHEN symbol = 'TOTAL3_SIGNAL'
                AND row_number = 1
                THEN value
            END
        ) AS total3_signal,
        MAX(
            CASE
                WHEN symbol = 'MARKET_REGIME_SCORE'
                AND row_number = 1
                THEN value
            END
        ) AS stored_score,
        MAX(
            CASE
                WHEN symbol = 'MARKET_REGIME_STATE'
                AND row_number = 1
                THEN value
            END
        ) AS stored_state
    FROM latest
)
SELECT
    btc_dom_signal,
    stablecoin_signal,
    eth_btc_signal,
    total3_signal,
    (
        btc_dom_signal
        + stablecoin_signal
        + eth_btc_signal
        + total3_signal
    ) AS calculated_score,
    stored_score,
    stored_state
FROM values_pivot;
"
```

`calculated_score` doit être égal à `stored_score`.

#### Rechercher les symboles présents sous plusieurs sources

```bash
docker compose exec sqlite sqlite3 \
  -header \
  -column \
  /data/macro.db "
SELECT
    symbol,
    COUNT(DISTINCT source) AS nombre_sources,
    GROUP_CONCAT(DISTINCT source) AS sources
FROM macro_series
GROUP BY symbol
HAVING COUNT(DISTINCT source) > 1
ORDER BY symbol;
"
```

Une ligne retournée n'est pas nécessairement une erreur, mais les panneaux
Grafana concernés doivent alors filtrer explicitement la source attendue.

#### Valider le code Python du collecteur

```bash
python3 -m py_compile \
  collector/main.py \
  collector/derived.py \
  collector/storage.py
```

#### Valider le JSON Grafana

```bash
python3 -m json.tool \
  grafana/dashboards/crypto-macro-overview.json \
  >/dev/null
```

Si `jq` est disponible, vérifier la requête du panneau `Score Explanation` :

```bash
jq -r '
  .panels[]
  | select(.id == 43)
  | .targets[0].queryText
' grafana/dashboards/crypto-macro-overview.json
```

La requête doit notamment :

- sélectionner la dernière observation avec `observed_at DESC, id DESC` ;
- filtrer `source = 'derived'` ;
- afficher `N/D` ou `Données insuffisantes` lorsque les données nécessaires
  sont absentes.

#### Vérifier les modifications Git

```bash
git status --short
git diff --check
git diff --stat
```

Examiner les fichiers principaux :

```bash
git diff -- \
  collector/derived.py \
  grafana/dashboards/crypto-macro-overview.json \
  DOCS/05-crypto-market-regime.md \
  DOCS/99-roadmap.md \
  DOCS/prompts/09-prompt-actif.md
```

### Contraintes d'exécution

Une collecte réelle nécessite :

- un moteur Docker accessible ;
- le fichier `.env` attendu par Docker Compose ;
- une clé FRED valide ;
- un accès réseau aux API FRED et CoinGecko ;
- le volume SQLite monté sur `/data/macro.db`.

CoinGecko peut être utilisé en mode public sans clé ou en mode Demo
authentifié selon la configuration du collecteur. En cas de réponse HTTP 429,
ne pas relancer le collecteur en boucle.
---

## 11. Roadmap et critère de fin

Le Sprint 1 et le périmètre fonctionnel du Crypto Market Regime V1 sont
documentés comme terminés. La roadmap distingue les fonctionnalités livrées,
les travaux de fiabilisation et les extensions futures comme BTC Trend et
Crypto Weather.

Priorité recommandée :

1. Ajouter les tests automatisés du contrat temporel des signaux ;
2. synchroniser code, documentation du régime et roadmap ;
3. compléter, seulement après spécification, volume global, tendance BTC et
   Crypto Weather ;
4. rendre le score macro partageable/persisté si les usages dépassent Grafana ;
5. calibrer les seuils sur historique avant alertes, rapports et backtests ;
6. préparer Captain Cryptos sans casser le contrat SQLite existant.

Une évolution est terminée lorsque son calcul est explicable, ses données
manquantes sont traitées honnêtement, les tests pertinents passent, le dashboard
affiche les valeurs attendues si concerné, et les documents ne contredisent plus
le code sur le périmètre modifié.

---

# 12. État actuel du projet

Cette section représente le **statut officiel** du projet au moment de la dernière mise à jour.

Elle permet de connaître immédiatement le niveau d'avancement sans avoir à parcourir l'ensemble du dépôt.

| Domaine | État | Commentaire |
|---------|------|-------------|
| Architecture générale | ✅ Stable | Architecture validée et documentée |
| Collecteurs FRED | ✅ Stable | Collecte des données macro fonctionnelle |
| Collecteur CoinGecko | ✅ Stable | Prix, métriques globales et catégories |
| Base SQLite | ✅ Stable | `macro_series` avec historisation et upsert |
| Raw Metrics | ✅ Stable | Toutes les données sources sont historisées |
| Derived Metrics | ✅ Stable | Calculées dans `collector/derived.py` |
| Crypto Signals | ✅ Stable | BTC_DOM, STABLECOIN_DOM, ETH/BTC, TOTAL3 |
| Crypto Market Regime | ✅ Stable (V1) | Score et State persistés dans SQLite |
| Dashboard Grafana | ✅ Stable (V1) | Dashboard versionné dans Git |
| Documentation | ✅ Synchronisée | Alignée avec le code et le dashboard |
| Alertes Discord | ⏳ À venir | Non implémentées |
| Rapports quotidiens | ⏳ À venir | Non implémentés |
| Macro Market Regime Python | ⏳ À étudier | Actuellement calculé en SQL Grafana |

## Pipeline actuellement implémenté

```text
FRED
CoinGecko
        │
        ▼
collector/main.py
        │
        ▼
Raw Metrics
        │
        ▼
SQLite (macro_series)
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
SQLite
        │
        ▼
Grafana Dashboard
```

Ce pipeline constitue aujourd'hui l'architecture officielle du projet.

Toute nouvelle fonctionnalité doit s'intégrer dans cette chaîne de traitement.

---

# 13. Décisions d'architecture (ADR)

Cette section conserve les principales décisions techniques prises au cours du projet.

Chaque décision est considérée comme **acceptée** jusqu'à ce qu'une évolution documentée la remplace.

---

## ADR-001 — Une seule base de données

**Statut :** ✅ Accepté

Toutes les données du projet (macro, crypto, métriques dérivées, signaux et états) sont stockées dans la table unique :

```
macro_series
```

### Motivation

- simplicité ;
- requêtes SQL homogènes ;
- maintenance réduite ;
- sauvegardes simplifiées ;
- historisation centralisée.

---

## ADR-002 — Les calculs métier sont réalisés en Python

**Statut :** ✅ Accepté

Les calculs métier sont réalisés dans le collecteur (`collector/derived.py`) et non dans Grafana.

Exemples :

- BTC_MCAP
- ETH_MCAP
- STABLECOIN_DOM
- ETH_BTC
- TOTAL3
- Trend Signals
- MARKET_REGIME_SCORE
- MARKET_REGIME_STATE

### Motivation

- calcul unique ;
- reproductibilité ;
- possibilité de tests unitaires ;
- réutilisation future (Discord, API, rapports).

---

## ADR-003 — Grafana est principalement une couche de visualisation

**Statut :** ⚠️ Partiellement appliqué

Grafana affiche les données persistées dans SQLite.

Exception actuelle :

Le **Macro Score Risk-On / Risk-Off** est encore calculé directement dans les requêtes SQL du dashboard.

Cette décision est assumée tant qu'aucun besoin de persistance ou de réutilisation n'existe.

Une migration future vers Python reste envisageable.

---

## ADR-004 — Les métriques dérivées constituent l'unique source des signaux

**Statut :** ✅ Accepté

Les signaux ne doivent jamais être calculés directement à partir des API.

Le pipeline officiel est :

```text
Raw Metrics
      ↓
Derived Metrics
      ↓
Signals
      ↓
Score
      ↓
State
```

Cette séparation garantit une architecture simple, cohérente et facilement extensible.

---

## ADR-005 — Toute évolution doit respecter le pipeline officiel

**Statut :** ✅ Accepté

Toute nouvelle donnée intégrée au projet doit suivre les étapes suivantes :

```
Collecte

↓

Raw Metric

↓

Derived Metric (si nécessaire)

↓

Signal (si pertinent)

↓

Score (si concerné)

↓

State (si concerné)

↓

Persistance SQLite

↓

Grafana

↓

Documentation
```

Aucune fonctionnalité ne doit contourner cette architecture.

---

## ADR-006 — Le JSON Grafana est versionné

**Statut :** ✅ Accepté

Le dashboard Grafana fait partie intégrante du projet.

Le fichier :

```
grafana/dashboards/crypto-macro-overview.json
```

constitue la version officielle du dashboard.

Toute modification réalisée dans l'interface Grafana doit être exportée puis versionnée dans Git.

---

## ADR-007 — La documentation suit le code

**Statut :** ✅ Accepté

En cas de divergence :

1. le code Python fait référence ;
2. le JSON Grafana fait référence ;
3. cette documentation est mise à jour.

La documentation ne doit jamais devenir une source de vérité indépendante du projet.
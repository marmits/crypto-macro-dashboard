# Prompt actif final — Projet `crypto-macro-dashboard`

## Contexte du projet

Je travaille sur un projet Docker local nommé :

```text
crypto-macro-dashboard
```

Le dashboard Grafana est accessible sur :

```text
http://localhost:9070
```

Ce projet sert à suivre le contexte macroéconomique et crypto afin de mieux interpréter les signaux de mon bot Freqtrade / Hyperliquid.

Le dashboard ne doit déclencher aucun trade automatiquement.

Il sert uniquement de filtre de contexte :

```text
risk-on / neutre / risk-off
```

L’approche souhaitée doit rester :

```text
progressive
simple
lisible
pédagogique
sans sur-architecture prématurée
```

---

## Objectif fonctionnel final

Le but final du dashboard n’est pas seulement d’afficher `FEDFUNDS` et les prix crypto.

L’objectif est de construire progressivement un dashboard local couvrant les grands axes suivants :

```text
Fed
taux
force du dollar
rendements US
pétrole
inflation
marché risk-on / risk-off
score macro synthétique
```

Le dashboard doit aider à répondre à des questions comme :

```text
Le contexte macro est-il favorable ou défavorable ?
Le marché est-il plutôt risk-on ou risk-off ?
Les taux ou le dollar pèsent-ils sur les cryptos ?
L’inflation ou la Fed rendent-elles le marché plus fragile ?
Faut-il être prudent avec les entrées Freqtrade / Hyperliquid ?
```

Le dashboard ne doit pas prédire parfaitement le marché.

Il doit seulement contextualiser les signaux du bot et encourager une lecture prudente du régime macro.

---

## Stack actuelle

La stack actuelle est :

```text
Docker
Docker Compose
Grafana
Python
SQLite
FRED API
CoinGecko keyless API
Markdown
Git
```

La base de données actuelle est :

```text
SQLite
```

Fichier SQLite local :

```text
data/macro.db
```

Une migration future vers PostgreSQL, InfluxDB ou Prometheus pourra être envisagée plus tard, mais ce n’est pas prioritaire.

---

## Arborescence actuelle

```text
crypto-macro-dashboard/
├── collector/
│   ├── config.py
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── data/
│   └── macro.db
├── docker-compose.yml
├── DOCS/
│   ├── 02-workflow-grafana-dashboard.md
│   └── prompts/
│       ├── 00-prompt-actif.md
│       ├── 01-prompt-actif.md
│       ├── 02-prompt-actif.md
│       ├── 03-prompt-actif.md
│       ├── 04-prompt-actif.md
│       └── 05-prompt-actif-final.md
├── grafana/
│   ├── dashboards/
│   │   └── crypto-macro-overview.json
│   └── provisioning/
│       ├── dashboards/
│       │   └── dashboards.yml
│       └── datasources/
│           └── sqlite.yml
├── scripts/
│   └── refresh-data.sh
└── README.md
```

> Le dossier `DOCS/prompts` contient les différentes versions des prompts actifs, classées de la plus ancienne à la plus récente.
>
> Le guide TradingView peut être ajouté dans `DOCS/03-suivi-macro-tradingview.md` s'il est effectivement présent dans le dépôt.

## Services Docker

Le projet utilise deux services principaux :

```text
grafana
collector
```

### Service `grafana`

Grafana utilise :

```text
grafana/grafana-oss:latest
```

Port local :

```text
9070:3000
```

Identifiants locaux actuels :

```text
admin / 123456
```

Plugin installé :

```text
frser-sqlite-datasource
```

Variable utilisée :

```text
GF_PLUGINS_PREINSTALL_SYNC=frser-sqlite-datasource
```

Volumes importants :

```text
./grafana/provisioning:/etc/grafana/provisioning
./grafana/dashboards:/var/lib/grafana/dashboards
./data:/data
```

### Service `collector`

Le collector est construit depuis :

```text
./collector
```

Il utilise :

```text
DB_PATH=/data/macro.db
```

Il charge aussi le fichier `.env`.

Le collector reste un job ponctuel. Il peut être lancé directement :

```bash
docker compose run --rm collector
```

Depuis l'étape 17, le mode manuel recommandé est :

```bash
./scripts/refresh-data.sh
```

Le collector ne contient pas de boucle infinie ni de scheduler.

Point essentiel :

```text
Grafana relit SQLite, mais Grafana ne collecte pas les données.
Les données sont actualisées uniquement lorsque le collector est lancé.
Le script refresh-data.sh lance le collector puis vérifie la fraîcheur des séries.
Aucun redémarrage de Grafana n'est nécessaire après une collecte.
```

## Configuration actuelle du collector

Le collector utilise actuellement :

```text
FRED_API_KEY
FRED_BASE_URL=https://api.stlouisfed.org/fred
COINGECKO_BASE_URL=https://api.coingecko.com/api/v3
```

`COINGECKO_API_KEY` existe comme option future, mais l’usage actuel reste en mode keyless public API.

---

## Séries FRED actuellement configurées

### Fed / taux

```text
FEDFUNDS -> FEDFUNDS -> Federal Funds Effective Rate
DGS2     -> US2Y     -> US 2Y Treasury Yield
DGS10    -> US10Y    -> US 10Y Treasury Yield
DGS30    -> US30Y    -> US 30Y Treasury Yield
```

### Inflation

```text
CPIAUCSL -> CPI      -> Consumer Price Index
CPILFESL -> CORE_CPI -> Core Consumer Price Index
PCEPI    -> PCE      -> Personal Consumption Expenditures Price Index
PCEPILFE -> CORE_PCE -> Core Personal Consumption Expenditures Price Index
```

Les séries inflation sont stockées comme des indices bruts.

Les variations YoY sont calculées dans Grafana via SQL :

```text
YoY % = (valeur actuelle / valeur il y a 12 mois - 1) * 100
```

### Pétrole / énergie

```text
DCOILWTICO   -> WTI   -> Crude Oil Price WTI
DCOILBRENTEU -> BRENT -> Crude Oil Price Brent
```

Unité :

```text
usd_per_barrel
```

### Dollar

```text
DTWEXBGS -> USD_BROAD -> Nominal Broad U.S. Dollar Index
```

`USD_BROAD` est utilisé comme proxy gratuit et large de la force du dollar.

### Marché / stress risk-on risk-off

```text
VIXCLS    -> VIX    -> CBOE Volatility Index
SP500     -> SP500  -> S&P 500
NASDAQCOM -> NASDAQ -> NASDAQ Composite
```

---

## Configuration d’historique FRED actuelle

```text
FEDFUNDS  -> limit 120
US2Y      -> limit 1500
US10Y     -> limit 1500
US30Y     -> limit 1500
CPI       -> limit 240
CORE_CPI  -> limit 240
PCE       -> limit 240
CORE_PCE  -> limit 240
WTI       -> limit 1500
BRENT     -> limit 1500
USD_BROAD -> limit 1500
VIX       -> limit 1500
SP500     -> limit 1500
NASDAQ    -> limit 1500
```

Objectif de ces limites :

```text
FEDFUNDS : environ 10 ans de données mensuelles
Inflation : environ 20 ans de données mensuelles
Séries quotidiennes : environ 5 à 6 ans de données ouvrées
```

Les valeurs FRED vides `"."` sont ignorées par le collector.

---

## Actifs CoinGecko actuellement configurés

```text
bitcoin     -> BTC
ethereum    -> ETH
solana      -> SOL
hyperliquid -> HYPE
```

CoinGecko est utilisé en mode keyless public API.

Aucune clé API CoinGecko n’est nécessaire pour l’usage actuel.

Attention :

```text
Le mode keyless est adapté au prototype local.
Il faut éviter le polling fréquent, car les limites sont partagées par IP.
```

---

## Sources de données actuelles

### FRED API

Utilisée pour les données macro officielles.

Séries actuellement collectées :

```text
FEDFUNDS
US2Y
US10Y
US30Y
CPI
CORE_CPI
PCE
CORE_PCE
WTI
BRENT
USD_BROAD
VIX
SP500
NASDAQ
```

Statut :

```text
DONE
```

### CoinGecko keyless API

Utilisée pour les actifs crypto.

Endpoint utilisé :

```text
https://api.coingecko.com/api/v3/simple/price
```

Paramètres utilisés :

```text
vs_currencies=usd
include_24hr_change=true
include_last_updated_at=true
```

Actifs collectés :

```text
BTC
ETH
SOL
HYPE
```

---

## Modèle SQLite actuel

Table principale :

```text
macro_series
```

Colonnes :

```text
id
source
symbol
name
value
unit
observed_at
created_at
updated_at
```

Règle sur les timestamps :

```text
observed_at = date réelle de l’observation économique ou marché
created_at  = date de première insertion de la ligne
updated_at  = date de dernière mise à jour de la ligne
```

Cette distinction est importante pour les séries FRED, car elles sont ré-upsertées à chaque collecte.

Lors d’un upsert, le collector ne modifie plus `created_at`.

Il met uniquement à jour :

```text
name
value
unit
updated_at
```

Index existants :

```text
idx_macro_series_symbol_observed_at
ux_macro_series_source_symbol_observed_at
```

La contrainte unique repose sur :

```text
source
symbol
observed_at
```

---

## Dashboard Grafana actuel

Dashboard principal :

```text
Crypto Macro Overview SQLite
```

UID officiel :

```text
crypto-macro-overview-sqlite-v2
```

Fichier source versionné :

```text
grafana/dashboards/crypto-macro-overview.json
```

Datasource Grafana :

```text
Macro SQLite
```

UID datasource :

```text
macro-sqlite
```

Fichier datasource :

```text
grafana/provisioning/datasources/sqlite.yml
```

Chemin SQLite côté Grafana :

```text
/data/macro.db
```

---

## Organisation actuelle du dashboard Grafana

Le dashboard est organisé avec les rows suivantes :

```text
Macro Score
Main
Dollar
Inflation
Energy
Market
Cryptos
Datas
```

> La row contenant les panels Fed et taux s'appelle actuellement `Main`. Son ergonomie est validée et elle peut rester sous ce nom pour le moment.

### Row `Macro Score`

Cette row est ouverte par défaut et contient :

```text
Score macro risk-on/off
Détails du score macro
```

Le panel de gauche affiche directement le régime :

```text
0 ou -1  → Contexte respirable → vert
-2 ou -3 → Prudence             → orange
-4 à -8  → Risk-off marqué      → rouge
```

Le panel de droite affiche les huit règles avec les colonnes :

```text
Règle
Valeur
Impact
```

La colonne technique `Ordre` reste présente dans la requête SQL afin de garantir le classement, mais elle est masquée par une transformation Grafana `Organize fields by name`.

Le champ SQL `Impact` reste numérique :

```text
0  → règle non déclenchée
-1 → règle déclenchée
```

Grafana applique uniquement un mapping visuel :

```text
0  → Inactive → vert
-1 → Active   → rouge
```

Ce mapping ne change pas le calcul du score.

### Row `Main`

Contient les panels Fed et taux :

```text
Dernier FEDFUNDS
FEDFUNDS — Federal Funds Effective Rate
Derniers rendements US
US Treasury Yields — FRED
US 10Y - 2Y Yield Spread — FRED
Dernier spread 10Y-2Y
```

### Row `Dollar`

```text
Dernier dollar broad
U.S. Dollar Index — FRED
```

### Row `Inflation`

```text
Dernière inflation YoY
Inflation YoY — FRED
```

### Row `Energy`

```text
Derniers prix pétrole
Oil Prices — FRED
```

### Row `Market`

```text
Dernier stress marché
VIX — FRED
S&P 500 / Nasdaq base 100 — FRED
```

### Row `Cryptos`

```text
BTC/USD — CoinGecko
Derniers prix crypto USD
Dernier BTC/USD
```

### Row `Datas`

Panels techniques et de vérification :

```text
Données crypto
Dernières données macro_series
```

Ces panels sont utiles pour le debug mais ne doivent pas encombrer la lecture principale.

## Panels Grafana actuels

Le dashboard affiche actuellement :

```text
Score macro risk-on/off
Détails du score macro
Dernier FEDFUNDS
FEDFUNDS — Federal Funds Effective Rate
Derniers rendements US
US Treasury Yields — FRED
US 10Y - 2Y Yield Spread — FRED
Dernier spread 10Y-2Y
Dernier dollar broad
U.S. Dollar Index — FRED
Dernière inflation YoY
Inflation YoY — FRED
Derniers prix pétrole
Oil Prices — FRED
Dernier stress marché
VIX — FRED
S&P 500 / Nasdaq base 100 — FRED
BTC/USD — CoinGecko
Derniers prix crypto USD
Dernier BTC/USD
Données crypto
Dernières données macro_series
```

---

## Score macro risk-on / risk-off v1

Le score macro v1 est calculé directement dans Grafana via SQL.

Il n’est pas stocké dans SQLite pour l’instant.

Objectif :

```text
Produire une synthèse pédagogique du contexte macro.
Ne pas déclencher de trade.
Ne pas prédire le marché.
```

### Règles actuelles du score v1

```text
VIX >= 20                    -> -1
VIX >= 30                    -> -1 supplémentaire, donc -2 au total pour le VIX
USD_BROAD >= 122             -> -1
US10Y >= 5                   -> -1
Spread 10Y-2Y < 0            -> -1
WTI >= 90 OR BRENT >= 90     -> -1
SP500 performance 30j < 0    -> -1
NASDAQ performance 30j < 0   -> -1
```

Score minimum possible :

```text
-8
```

### Interprétation actuelle du score

```text
0 à -1   -> contexte respirable
-2 à -3  -> prudence
<= -4    -> risk-off marqué
```

### État observé lors de la mise à jour du prompt

Le 13 juillet 2026, après restauration et validation de la row `Macro Score`, les valeurs affichées étaient approximativement :

```text
VIX                       : 15,84
USD_BROAD                 : 120,69
US10Y                     : 4,54 %
Spread 10Y-2Y             : +0,380 %
WTI / Brent FRED          : 69,60 / 69,56 USD
Performance SP500 sur 30j : +2,56 %
Performance NASDAQ sur 30j: +2,35 %
```

Toutes les règles étaient alors `Inactive` :

```text
Score  : 0
Régime : Contexte respirable
```

Cette valeur est une photographie ponctuelle. Elle évoluera après les prochaines collectes.

## Horizons temporels Grafana actuellement utilisés

Les panels principaux ont des horizons temporels spécifiques :

```text
BTC/USD — CoinGecko                     -> Last 7 days
FEDFUNDS — Federal Funds Effective Rate -> Last 5 years
US Treasury Yields — FRED               -> Last 5 years
US 10Y - 2Y Yield Spread — FRED         -> Last 5 years
U.S. Dollar Index — FRED                -> Last 5 years
Inflation YoY — FRED                    -> Last 10 years
Oil Prices — FRED                       -> Last 1 year ou Last 3 years selon lisibilité
VIX — FRED                              -> Last 5 years
S&P 500 / Nasdaq base 100 — FRED        -> Last 5 years
```

Le dashboard global peut rester sur :

```text
Last 24 hours
```

Les panels macro restent lisibles grâce à leurs overrides temporels.

---

## Règles Grafana importantes confirmées

Les panels Grafana SQLite nécessitent certains champs spécifiques dans le JSON :

```text
queryText
rawQueryText
rawSql
rawQuery
queryType
timeColumns
```

Point technique résolu :

```text
Les premiers panels affichaient No data alors que la datasource SQLite fonctionnait.
La correction a consisté à ajouter rawQueryText et timeColumns dans les targets du JSON Grafana.
```

Les panels multi-séries SQLite doivent éviter la forme :

```text
time | value | metric
```

si Grafana ne sépare pas correctement les séries.

Pour les panels multi-séries, il faut préférer une requête pivotée :

```text
time | SERIE_1 | SERIE_2 | SERIE_3
```

Exemples concernés :

```text
US2Y / US10Y / US30Y
WTI / BRENT
CPI YoY / Core CPI YoY / PCE YoY / Core PCE YoY
SP500 / NASDAQ base 100
```

Le spread `10Y-2Y` est calculé directement dans Grafana via SQL, sans nouvelle table SQLite et sans nouvelle série stockée.

Le score macro v1 est également calculé dans Grafana via SQL.

---

## Workflow Grafana important

Le dashboard Grafana est provisionné depuis :

```text
grafana/dashboards/crypto-macro-overview.json
```

Ce fichier est la source de vérité versionnée dans Git.

Le dashboard provisionné ne doit pas être considéré comme modifiable directement depuis l’UI Grafana.

Grafana peut proposer :

```text
Save as copy
Copy JSON to clipboard
Save JSON to file
```

Workflow recommandé pour modifier le dashboard :

```text
1. Ouvrir le dashboard officiel dans Grafana
2. Faire Save as copy si Grafana ne permet pas la sauvegarde directe
3. Modifier la copie dans l’UI Grafana
4. Sauvegarder la copie
5. Exporter la copie via l’API Grafana
6. Remplacer grafana/dashboards/crypto-macro-overview.json avec l’export
7. Forcer l’UID officiel crypto-macro-overview-sqlite-v2
8. Redémarrer Grafana
9. Vérifier que le dashboard officiel contient bien les modifications
10. Supprimer la copie dans Grafana
11. Commiter le JSON
```

Règle importante :

```text
Ne jamais considérer une modification UI comme définitive tant qu’elle n’a pas été exportée dans grafana/dashboards/crypto-macro-overview.json et commitée.
```

Résumé :

```text
Grafana UI = outil d’édition temporaire
JSON provisionné = source de vérité
Git = historique officiel
```

Le workflow détaillé est documenté dans :

```text
DOCS/02-workflow-grafana-dashboard.md
```

---

## Étape 17 — Script manuel de rafraîchissement

Fichier :

```text
scripts/refresh-data.sh
```

Commande à retenir :

```bash
./scripts/refresh-data.sh
```

Le script :

```text
détermine automatiquement la racine du projet
vérifie que Docker est disponible
vérifie la présence de docker-compose.yml et de .env
valide la configuration Docker Compose
vérifie que le moteur Docker est accessible
empêche deux collectes simultanées avec flock
lance docker compose run --rm collector
affiche un résumé de la fraîcheur de toutes les séries
retourne un code de sortie fiable
```

Le verrou utilisé est :

```text
/tmp/crypto-macro-dashboard-refresh.lock
```

La vérification finale affiche pour chaque série :

```text
source
symbole
nombre de lignes
dernière observation
dernière mise à jour
```

La distinction reste importante :

```text
observed_at → date réelle de l'observation économique ou marché
updated_at  → date du dernier traitement de la ligne par le collector
```

Le script ne :

```text
redémarre pas Grafana
ne reconstruit pas systématiquement l'image du collector
ne modifie pas le dashboard
ne calcule pas et n'historise pas MACRO_SCORE
ne lance aucune boucle infinie
```

Le script est préparé pour une éventuelle utilisation future dans `cron`, mais aucun cron n'est configuré actuellement.

Préparation et vérification :

```bash
chmod +x scripts/refresh-data.sh
bash -n scripts/refresh-data.sh
```

Exécution :

```bash
./scripts/refresh-data.sh
```

Vérification du code de retour :

```bash
echo $?
```

Résultat attendu après succès :

```text
0
```

Après une collecte réussie, Grafana relit automatiquement `data/macro.db`. Il suffit d'utiliser le bouton `Refresh` dans Grafana.

---

## Commandes utiles

### Rafraîchir les données avec le script recommandé

```bash
./scripts/refresh-data.sh
```

### Vérifier la syntaxe du script

```bash
bash -n scripts/refresh-data.sh
```

### Vérifier les permissions du script

```bash
ls -l scripts/refresh-data.sh
```

### Lancer Grafana

```bash
docker compose up -d grafana
```

### Lancer le collector

```bash
docker compose run --rm collector
```

### Rebuild du collector

```bash
docker compose build collector
```

### Vérifier les services

```bash
docker compose ps
```

### Vérifier le JSON Grafana

```bash
python3 -m json.tool grafana/dashboards/crypto-macro-overview.json > /tmp/check-dashboard.json
```

### Lister les dashboards Grafana

```bash
curl -s -u admin:123456 "http://localhost:9070/api/search?query=Crypto" | python3 -m json.tool
```

### Exporter un dashboard Grafana

```bash
curl -s -u admin:123456 \
  "http://localhost:9070/api/dashboards/uid/UID_DU_DASHBOARD" \
  | python3 -m json.tool > /tmp/crypto-macro-dashboard-export.json
```

### Redémarrer Grafana

```bash
docker compose restart grafana
```

### Vérifier toutes les séries FRED principales

```bash
docker compose run --rm --entrypoint python collector - <<'PY'
import sqlite3

conn = sqlite3.connect("/data/macro.db")

rows = conn.execute(
    """
    SELECT
        source,
        symbol,
        COUNT(*) AS total_rows,
        MIN(observed_at) AS first_observed_at,
        MAX(observed_at) AS last_observed_at
    FROM macro_series
    WHERE source = 'fred'
      AND symbol IN (
          'FEDFUNDS',
          'US2Y',
          'US10Y',
          'US30Y',
          'CPI',
          'CORE_CPI',
          'PCE',
          'CORE_PCE',
          'WTI',
          'BRENT',
          'USD_BROAD',
          'VIX',
          'SP500',
          'NASDAQ'
      )
    GROUP BY source, symbol
    ORDER BY symbol
    """
).fetchall()

for row in rows:
    print(row)

conn.close()
PY
```

### Vérifier le dernier spread 10Y-2Y

```bash
docker compose run --rm --entrypoint python collector - <<'PY'
import sqlite3

conn = sqlite3.connect("/data/macro.db")
conn.row_factory = sqlite3.Row

row = conn.execute(
    """
    SELECT
        us10y.observed_at,
        us2y.value AS us2y,
        us10y.value AS us10y,
        us10y.value - us2y.value AS spread_10y_2y
    FROM macro_series us10y
    JOIN macro_series us2y
      ON us2y.observed_at = us10y.observed_at
    WHERE us10y.source = 'fred'
      AND us2y.source = 'fred'
      AND us10y.symbol = 'US10Y'
      AND us2y.symbol = 'US2Y'
    ORDER BY us10y.observed_at DESC
    LIMIT 1
    """
).fetchone()

print(dict(row) if row else "Aucune donnée trouvée.")

conn.close()
PY
```

---

## Statut des étapes

```text
Étape 1    — Grafana local                              DONE
Étape 2    — Collector Python + SQLite                  DONE
Étape 3    — FRED FEDFUNDS                              DONE
Étape 4    — Grafana SQLite                             DONE
Étape 5    — CoinGecko BTC/USD                          DONE
Étape 6    — Panels BTC/USD                             DONE
Étape 7    — ETH, SOL, HYPE                             DONE
Étape 8    — Panels crypto multi-actifs                 DONE
Étape 9    — updated_at                                 DONE
Étape 9.1  — Horizons temporels des panels              DONE
Étape 10   — Rendements US depuis FRED                  DONE
Étape 10.1 — Panels Grafana rendements US               DONE
Étape 10.2 — Historique FRED étendu                     DONE
Étape 11   — Courbe 10Y-2Y                              DONE
Étape 12   — Inflation CPI / Core CPI / PCE / Core PCE DONE
Étape 12.2 — Panels inflation YoY                       DONE
Étape 13   — Pétrole WTI / Brent                        DONE
Étape 13.2 — Panels pétrole                             DONE
Étape 14   — Dollar proxy USD_BROAD                     DONE
Étape 14.2 — Panels dollar                              DONE
Étape 15   — VIX / SP500 / NASDAQ                       DONE
Étape 15.2 — Panels Market                              DONE
Étape 16   — Score macro risk-on / risk-off v1          DONE
Étape 16.1 — Restauration et amélioration UX du score   DONE
Étape 17   — Script manuel de rafraîchissement          DONE
```

L'étape 16.1 comprend :

```text
restauration de la row Macro Score
rétablissement des huit règles
libellés Contexte respirable / Prudence / Risk-off marqué
couleurs vert / orange / rouge
masquage visuel de la colonne Ordre
mapping Impact : Inactive / Active
huit règles visibles sans pagination
```

L'étape 17 comprend :

```text
script scripts/refresh-data.sh
exécution manuelle simple du collector
vérifications Docker et Docker Compose
protection contre les exécutions concurrentes avec flock
résumé de la fraîcheur des séries après collecte
compatibilité préparée pour une future utilisation dans cron
aucun redémarrage automatique de Grafana
```

## Objectif fonctionnel atteint à ce stade

Le dashboard couvre maintenant :

```text
Fed
rendements US
courbe 10Y - 2Y
dollar
inflation
pétrole
stress marché
S&P 500 / Nasdaq
cryptos
score macro risk-on / risk-off v1
```

Il s’agit d’une première version macro complète et exploitable.

---

## Objectif fonctionnel cible à terme

Le dashboard doit continuer à rester simple et lisible.

À terme, il peut évoluer vers :

```text
Score macro v2
score historisé
scheduler du collector
meilleure lecture crypto 7j / 30j
alertes visuelles non-trading
éventuelle migration base de données si SQLite devient limitant
```

---

## Évolutions possibles — non prioritaires

### 1. Stabilisation UX du dashboard

Améliorations possibles :

```text
Ajuster la pagination du panel Détails du score macro
Afficher les 8 lignes du score sans pagination
Réduire la largeur du panel Score macro si nécessaire
Agrandir le panel Détails du score macro via gridPos JSON si nécessaire
Replier certaines rows par défaut selon l’usage quotidien
Raccourcir les libellés des règles si la table déborde horizontalement
```

Priorité :

```text
faible à moyenne
```

### 2. Automatisation future du collector

Le script manuel est maintenant disponible :

```bash
./scripts/refresh-data.sh
```

Il peut être exécuté à la demande et a été préparé pour une éventuelle utilisation dans `cron`.

Aucun cron n'est configuré pour l'instant.

Principes à conserver si l'automatisation est ajoutée plus tard :

```text
utiliser un chemin absolu vers le script
rediriger stdout et stderr vers un journal
conserver flock pour éviter les doubles collectes
utiliser une fréquence raisonnable
ne pas redémarrer Grafana après chaque collecte
```

Fréquences indicatives :

```text
FRED macro       → une fois par jour suffit largement
CoinGecko crypto → éviter le polling fréquent en mode keyless
```

Priorité :

```text
faible tant que l'exécution manuelle reste suffisante
```

### 3. Score macro v2

Améliorations possibles :

```text
Ajouter l’inflation au score
Ajouter la variation USD_BROAD 30j / 90j
Ajouter la variation US10Y 30j / 90j
Ajouter la variation pétrole 30j
Ajouter BTC 7j / 30j uniquement si la collecte crypto devient régulière
Ajouter une pondération légère si certaines règles sont trop fortes ou trop faibles
```

Exemples de règles v2 possibles :

```text
Core PCE YoY > 3.0        -> -1
CPI YoY > 3.5             -> -1
USD_BROAD en hausse 30j   -> -1
US10Y en hausse 30j       -> -1
WTI en hausse forte 30j   -> -1
BTC 7j < 0                -> -1
```

Priorité :

```text
moyenne, après observation du score v1
```

### 4. Historisation du score — reportée

L'idée générale serait :

```text
calculer le score dans le collector
stocker MACRO_SCORE dans SQLite
conserver les scores successifs
visualiser les changements de régime dans Grafana
```

Cette évolution n'est pas retenue maintenant.

```text
calcul du score dans le collector → reporté
stockage de MACRO_SCORE           → reporté
historique des régimes            → reporté
score actuel calculé dans Grafana → conservé
```

Priorité :

```text
non prioritaire
```

### 5. Amélioration crypto

Améliorations possibles :

```text
scheduler plus régulier pour BTC / ETH / SOL / HYPE
variation BTC 7j / 30j
variation ETH / SOL / HYPE 7j / 30j
panel crypto base 100
intégration éventuelle au score v2
```

Attention :

```text
Ne pas poller CoinGecko trop fréquemment en mode keyless.
```

Priorité :

```text
moyenne, après automatisation du collector
```

### 6. Alertes visuelles non-trading

Possibilités :

```text
alerte Grafana si score <= -4
alerte si VIX >= 30
alerte si USD_BROAD >= 122
alerte si US10Y >= 5
alerte si pétrole >= 90
```

Important :

```text
Ces alertes doivent rester informatives.
Elles ne doivent déclencher aucun trade automatiquement.
```

Priorité :

```text
faible à moyenne
```

### 7. Migration de stockage éventuelle

SQLite reste adapté au prototype local.

Migration future possible si besoin :

```text
PostgreSQL
InfluxDB
Prometheus
```

Mais ce n’est pas prioritaire tant que :

```text
le volume reste faible
la collecte reste simple
Grafana lit correctement SQLite
```

Priorité :

```text
faible
```

---

## Prochaine priorité recommandée

```text
1. Tester ./scripts/refresh-data.sh en conditions normales.
2. Vérifier son code de retour et la fraîcheur des séries.
3. Commiter le script et le présent prompt actif.
4. Utiliser le dashboard et observer le score v1 sans modifier les seuils trop vite.
5. Rafraîchir les données manuellement selon le besoin.
6. Envisager un cron uniquement si l'exécution manuelle devient contraignante.
7. Reporter le score v2 et l'historisation tant qu'un besoin concret n'est pas établi.
```

## Contraintes de travail

Je travaille principalement avec :

```text
Docker
Docker Compose
Linux / WSL2
Python
Grafana
SQLite
Markdown
Git
```

Je souhaite :

```text
une étape à la fois
des explications simples
des commandes Docker/Bash claires
des fichiers complets quand nécessaire
aucune sur-architecture prématurée
```

Quand tu proposes du code, donne systématiquement :

```text
le chemin du fichier
le contenu complet du fichier
la commande à exécuter
la commande de vérification
```

Pour les commits Git, les messages doivent être rédigés en français.

Exemples :

```bash
git commit -m "feat: ajoute le collecteur sqlite initial"
git commit -m "feat: ajoute la collecte fred fedfunds"
git commit -m "feat: connecte grafana à sqlite"
git commit -m "feat: ajoute bitcoin via coingecko dans grafana"
git commit -m "feat: ajoute eth sol et hype au dashboard crypto"
git commit -m "refactor: ajoute updated_at aux séries macro"
git commit -m "feat: ajoute les rendements us depuis fred"
git commit -m "feat: augmente l'historique fred des rendements us"
git commit -m "feat: ajoute le spread 10y 2y au dashboard grafana"
git commit -m "feat: ajoute les series inflation depuis fred"
git commit -m "feat: ajoute les panels inflation yoy au dashboard grafana"
git commit -m "feat: ajoute les prix du petrole depuis fred"
git commit -m "feat: ajoute les panels petrole au dashboard grafana"
git commit -m "feat: ajoute un proxy dollar depuis fred"
git commit -m "feat: ajoute les panels dollar au dashboard grafana"
git commit -m "feat: ajoute vix sp500 et nasdaq depuis fred"
git commit -m "feat: ajoute les panels marche au dashboard grafana"
git commit -m "feat: ajoute un score macro risk-on risk-off"
git commit -m "docs: met a jour le prompt actif apres la v1 macro complete"
git commit -m "feat: ajoute un script de rafraichissement des donnees"
git commit -m "docs: met a jour le prompt actif apres l etape 17"
```

---

## Ce que je veux maintenant

Je veux continuer le projet progressivement à partir de cet état déjà initialisé.

Ne pas repartir de zéro.

Ne pas simplifier en oubliant l’objectif final macro complet.

Toujours tenir compte du fait que le projet actuel contient déjà :

```text
Grafana opérationnel
Collector Python Dockerisé
SQLite
FRED FEDFUNDS
FRED US2Y / US10Y / US30Y
Inflation CPI / CORE_CPI / PCE / CORE_PCE
Pétrole WTI / BRENT
Dollar USD_BROAD
VIX / SP500 / NASDAQ
Courbe 10Y - 2Y calculée dans Grafana
Score macro risk-on / risk-off v1 calculé dans Grafana
CoinGecko BTC / ETH / SOL / HYPE
Dashboard Grafana provisionné
Rows Grafana Macro Score / Main / Dollar / Inflation / Energy / Market / Cryptos / Datas
Panels macro avec horizons temporels cohérents
Workflow Grafana par copie + export JSON
Modèle SQLite avec observed_at / created_at / updated_at
Script scripts/refresh-data.sh pour actualiser les données à la demande
Protection flock contre les collectes simultanées
Résumé automatique de la fraîcheur des séries après collecte
```

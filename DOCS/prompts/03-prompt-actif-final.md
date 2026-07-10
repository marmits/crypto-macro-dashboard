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
risk-on / risk-off
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
```

Le dashboard doit aider à répondre à des questions comme :

```text
Le contexte macro est-il favorable ou défavorable ?
Le marché est-il plutôt risk-on ou risk-off ?
Les taux ou le dollar pèsent-ils sur les cryptos ?
L’inflation ou la Fed rendent-elles le marché plus fragile ?
Faut-il être prudent avec les entrées Freqtrade / Hyperliquid ?
```

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
│   ├── .gitkeep
│   └── macro.db
├── docker-compose.yml
├── DOCS/
│   ├── 02-workflow-grafana-dashboard.md
│   └── prompts/
│       ├── 00-prompt-actif.md
│       ├── 01-prompt-actif.md
│       ├── 02-prompt-actif-final-temporaire.md
│       └── 03-prompt-actif-final.md
├── grafana/
│   ├── dashboards/
│   │   └── crypto-macro-overview.json
│   └── provisioning/
│       ├── dashboards/
│       │   └── dashboards.yml
│       └── datasources/
│           └── sqlite.yml
└── README.md
```

---

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

Il charge aussi le fichier :

```text
.env
```

Le collector est actuellement un job ponctuel lancé manuellement :

```bash
docker compose run --rm collector
```

Il ne contient pas encore de boucle infinie ni de scheduler.

---

## Configuration actuelle du collector

Le collector utilise actuellement :

```text
FRED_API_KEY
FRED_BASE_URL=https://api.stlouisfed.org/fred
COINGECKO_BASE_URL=https://api.coingecko.com/api/v3
```

Série FRED actuellement configurée :

```text
FEDFUNDS
```

Actifs CoinGecko actuellement configurés :

```text
bitcoin     -> BTC
ethereum    -> ETH
solana      -> SOL
hyperliquid -> HYPE
```

CoinGecko est utilisé en mode keyless public API.

Aucune clé API CoinGecko n’est nécessaire pour l’usage actuel.

---

## Sources de données actuelles

### FRED API

Utilisée pour les données macro officielles.

Série actuellement collectée :

```text
FEDFUNDS
```

Description :

```text
Federal Funds Effective Rate
```

Statut :

```text
DONE
```

Objectif futur :

```text
Ajouter progressivement les rendements US, l’inflation, le pétrole et d’autres indicateurs macro.
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

Mapping :

```text
bitcoin     -> BTC
ethereum    -> ETH
solana      -> SOL
hyperliquid -> HYPE
```

Attention :

```text
Le mode keyless est adapté au prototype local.
Il faut éviter le polling fréquent, car les limites sont partagées par IP.
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

## Panels Grafana actuels

Le dashboard affiche actuellement :

```text
Derniers prix crypto USD
FEDFUNDS — Federal Funds Effective Rate
Dernier FEDFUNDS
Dernier BTC/USD
Données crypto
BTC/USD — CoinGecko
Dernières données macro_series
```

Le panel multi-actifs crypto affiche :

```text
BTC_USD
ETH_USD
SOL_USD
HYPE_USD
```

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

## Commandes utiles

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

---

## Statut des étapes

### Étape 1 — Grafana local

```text
DONE
```

Grafana fonctionne sur :

```text
http://localhost:9070
```

### Étape 2 — Collector Python + SQLite

```text
DONE
```

Le collector Dockerisé écrit dans :

```text
data/macro.db
```

### Étape 3 — FRED FEDFUNDS

```text
DONE
```

La série `FEDFUNDS` est collectée depuis FRED et stockée en SQLite.

### Étape 4 — Grafana SQLite

```text
DONE
```

Grafana lit SQLite via `frser-sqlite-datasource`.

### Étape 5 — CoinGecko BTC/USD

```text
DONE
```

BTC/USD est collecté via CoinGecko keyless.

### Étape 6 — Panels BTC/USD

```text
DONE
```

BTC/USD est affiché dans Grafana.

### Étape 7 — ETH, SOL, HYPE

```text
DONE
```

ETH, SOL et HYPE sont collectés via CoinGecko keyless.

### Étape 8 — Panels crypto multi-actifs

```text
DONE
```

Le dashboard affiche maintenant BTC, ETH, SOL et HYPE.

### Étape 9 — `updated_at`

```text
DONE
```

Le modèle SQLite distingue maintenant :

```text
observed_at
created_at
updated_at
```

---

## Objectif fonctionnel cible à terme

Le dashboard doit évoluer vers une structure couvrant :

```text
Fed
taux
force du dollar
rendements US
pétrole
inflation
marché risk-on / risk-off
```

### Fed / politique monétaire

Déjà intégré :

```text
FEDFUNDS
```

À enrichir plus tard :

```text
autres indicateurs de politique monétaire si utile
```

### Taux / rendements US

À intégrer progressivement :

```text
US 2Y
US 10Y
US 30Y
Yield curve 10Y - 2Y
```

Objectif :

```text
Suivre la pression des taux sur les actifs risqués.
Identifier les phases de tension sur les rendements.
Mesurer la pente ou l’inversion de la courbe des taux.
```

### Force du dollar

À intégrer progressivement :

```text
DXY
ou proxy dollar gratuit
```

Objectif :

```text
Suivre la force du dollar.
Un dollar fort est souvent défavorable aux actifs risqués et aux cryptos.
```

### Pétrole / énergie

À intégrer progressivement :

```text
WTI
Brent
```

Objectif :

```text
Suivre les tensions énergie / inflation.
Une forte hausse du pétrole peut peser sur l’inflation et le contexte risk-on.
```

### Inflation

À intégrer progressivement :

```text
CPI
Core CPI
PCE
Core PCE
```

Objectif :

```text
Suivre la tendance inflationniste.
Comprendre le contexte de politique monétaire de la Fed.
```

### Marché risk-on / risk-off

À intégrer progressivement :

```text
VIX
S&P 500
Nasdaq
BTC
ETH
SOL
HYPE
```

Déjà intégré :

```text
BTC
ETH
SOL
HYPE
```

---

## Dashboard cible à terme

Structure cible indicative :

### Ligne 1 — Synthèse

```text
Score macro
État risk-on / risk-off
BTC
DXY
US10Y
VIX
```

### Ligne 2 — Fed / taux

```text
Fed Funds Rate
US2Y
US10Y
US30Y
10Y-2Y spread
```

### Ligne 3 — Dollar / pétrole

```text
DXY
WTI
Brent
```

### Ligne 4 — Inflation

```text
CPI YoY
Core CPI YoY
PCE YoY
Core PCE YoY
```

### Ligne 5 — Crypto

```text
BTC
ETH
SOL
HYPE
```

### Ligne 6 — Interprétation

```text
Macro favorable
Macro neutre
Macro défavorable
Risk-on
Risk-off
Prudence sur les entrées Freqtrade
```

---

## Score risk-on / risk-off cible

Le projet doit évoluer vers un score simple, lisible et pédagogique.

Exemple de règles futures :

```text
DXY en hausse forte        => -1
US10Y en hausse forte      => -1
US2Y en hausse forte       => -1
VIX élevé                  => -1
Pétrole en hausse forte    => -1
BTC en baisse forte        => -1
Nasdaq en baisse forte     => -1
```

Interprétation possible :

```text
Score >= 0        => contexte respirable
Score entre -1/-3 => prudence
Score <= -4       => risk-off marqué
```

Le score doit rester volontairement simple au départ.

Il ne doit pas chercher à prédire parfaitement le marché.

Il doit uniquement aider à contextualiser les signaux Freqtrade / Hyperliquid.

---

## Prochaines étapes recommandées

Les prochaines étapes doivent enrichir le dashboard vers son objectif fonctionnel final.

Priorité proposée :

```text
Étape 10 — Ajouter les rendements US depuis FRED : US2Y, US10Y, US30Y
Étape 11 — Ajouter la courbe 10Y - 2Y
Étape 12 — Ajouter inflation : CPI / Core CPI / PCE / Core PCE
Étape 13 — Ajouter pétrole : WTI / Brent
Étape 14 — Ajouter dollar : DXY ou proxy gratuit
Étape 15 — Ajouter VIX / Nasdaq / S&P 500 si source gratuite fiable
Étape 16 — Construire un premier score risk-on / risk-off simple
```

Le score risk-on / risk-off doit idéalement venir après quelques indicateurs macro supplémentaires, pour éviter de construire un score basé uniquement sur `FEDFUNDS` et les cryptos.

---

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
CoinGecko BTC / ETH / SOL / HYPE
Dashboard Grafana provisionné
Workflow Grafana par copie + export JSON
Modèle SQLite avec observed_at / created_at / updated_at
```

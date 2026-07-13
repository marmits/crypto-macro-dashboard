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

Le dashboard ne doit déclencher aucun trade automatiquement. Il sert uniquement de filtre de contexte :

```text
risk-on / neutre / risk-off
```

L’approche doit rester :

```text
progressive
simple
lisible
pédagogique
sans sur-architecture prématurée
```

---

## Objectif fonctionnel

Le dashboard doit couvrir les grands axes suivants :

```text
Fed
taux et rendements US
courbe des taux 10Y-2Y
force du dollar
inflation
pétrole
stress et marchés actions
cryptomonnaies
score macro synthétique
```

Le dashboard doit aider à répondre à ces questions :

```text
Le contexte macro est-il favorable ou défavorable ?
Le marché est-il plutôt risk-on, neutre ou risk-off ?
Les taux ou le dollar pèsent-ils sur les cryptos ?
L’inflation, le pétrole ou la Fed fragilisent-ils le marché ?
Faut-il être plus prudent avec les entrées Freqtrade / Hyperliquid ?
```

Le dashboard ne cherche pas à prédire parfaitement le marché. Il contextualise les signaux du bot et encourage une lecture prudente du régime macro.

---

## Stack actuelle

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

Base de données :

```text
SQLite
```

Fichier local :

```text
data/macro.db
```

Une éventuelle migration vers PostgreSQL, InfluxDB ou Prometheus pourra être étudiée plus tard. Elle n’est pas prioritaire tant que SQLite répond correctement au besoin.

---

## Arborescence actuelle

```text
crypto-macro-dashboard/
├── collector
│ ├── config.py
│ ├── Dockerfile
│ ├── main.py
│ └── requirements.txt
├── data
│ └── macro.db
├── docker-compose.yml
├── DOCS
│ ├── 02-workflow-grafana-dashboard.md
│ └── prompts
│     ├── 00-prompt-actif.md
│     ├── 01-prompt-actif.md
│     ├── 02-prompt-actif.md
│     ├── 03-prompt-actif.md
│     └── 04-prompt-actif.md
├── grafana
│ ├── dashboards
│ │ └── crypto-macro-overview.json
│ └── provisioning
│     ├── dashboards
│     │ └── dashboards.yml
│     └── datasources
│         └── sqlite.yml
└── README.md
```

- > Le fichier `DOCS/03-suivi-macro-tradingview.md` est présent uniquement s’il a bien été ajouté au dépôt. Il documente les symboles TradingView utiles au suivi macro.
- > Le dossier `DOCS/prompts` contient les différentes version des promptes actifs classés par plus ancien au plus récent
---

## Services Docker

Le projet utilise deux services principaux :

```text
grafana
collector
```

### Service `grafana`

Image :

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

Plugin SQLite :

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

Chemin de la base dans le conteneur :

```text
DB_PATH=/data/macro.db
```

Le service charge le fichier `.env`.

Le collector reste un job ponctuel lancé manuellement :

```bash
docker compose run --rm collector
```

Il ne contient pas encore de boucle infinie ni de scheduler.

Point essentiel :

```text
Grafana relit SQLite, mais Grafana ne collecte aucune donnée.
Les données sont actualisées uniquement lorsque le collector est exécuté.
```

---

## Configuration du collector

```text
FRED_API_KEY
FRED_BASE_URL=https://api.stlouisfed.org/fred
COINGECKO_BASE_URL=https://api.coingecko.com/api/v3
```

`COINGECKO_API_KEY` peut exister comme option future, mais CoinGecko est actuellement utilisé avec son API publique keyless.

---

## Séries FRED collectées

### Fed et rendements US

```text
FEDFUNDS → FEDFUNDS → Federal Funds Effective Rate
DGS2     → US2Y     → US 2Y Treasury Yield
DGS10    → US10Y    → US 10Y Treasury Yield
DGS30    → US30Y    → US 30Y Treasury Yield
```

### Inflation

```text
CPIAUCSL → CPI      → Consumer Price Index
CPILFESL → CORE_CPI → Core Consumer Price Index
PCEPI    → PCE      → Personal Consumption Expenditures Price Index
PCEPILFE → CORE_PCE → Core Personal Consumption Expenditures Price Index
```

Les séries d’inflation sont enregistrées comme indices bruts. Les variations annuelles sont calculées dans Grafana via SQL :

```text
YoY % = (valeur actuelle / valeur il y a 12 mois - 1) × 100
```

### Pétrole et énergie

```text
DCOILWTICO   → WTI   → Crude Oil Price WTI
DCOILBRENTEU → BRENT → Crude Oil Price Brent
```

Unité :

```text
usd_per_barrel
```

Ces séries correspondent aux derniers prix spot officiels EIA relayés par FRED. Elles peuvent être publiées avec plusieurs jours de retard et ne doivent pas être confondues avec les contrats futures continus affichés dans TradingView.

### Dollar

```text
DTWEXBGS → USD_BROAD → Nominal Broad U.S. Dollar Index
```

`USD_BROAD` est utilisé comme proxy large et gratuit de la force du dollar.

Il ne doit pas être confondu avec :

```text
TVC:DXY    → Dollar Index affiché dans TradingView
ICEUS:DX1! → futures continus sur le Dollar Index
```

### Marché et stress risk-on / risk-off

```text
VIXCLS    → VIX    → CBOE Volatility Index
SP500     → SP500  → S&P 500
NASDAQCOM → NASDAQ → Nasdaq Composite
```

---

## Limites d’historique FRED

```text
FEDFUNDS  → limit 120
US2Y      → limit 1500
US10Y     → limit 1500
US30Y     → limit 1500
CPI       → limit 240
CORE_CPI  → limit 240
PCE       → limit 240
CORE_PCE  → limit 240
WTI       → limit 1500
BRENT     → limit 1500
USD_BROAD → limit 1500
VIX       → limit 1500
SP500     → limit 1500
NASDAQ    → limit 1500
```

Objectif :

```text
FEDFUNDS          → environ 10 ans de données mensuelles
Inflation         → environ 20 ans de données mensuelles
Séries quotidiennes → environ 5 à 6 ans de données ouvrées
```

Les valeurs FRED vides `.` sont ignorées par le collector.

---

## Actifs CoinGecko

```text
bitcoin     → BTC
ethereum    → ETH
solana      → SOL
hyperliquid → HYPE
```

Endpoint :

```text
https://api.coingecko.com/api/v3/simple/price
```

Paramètres :

```text
vs_currencies=usd
include_24hr_change=true
include_last_updated_at=true
```

Le mode keyless est adapté au prototype local. Il faut éviter un polling fréquent, car les limites sont partagées par adresse IP.

---

## Modèle SQLite

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

Sémantique des timestamps :

```text
observed_at → date réelle de l’observation économique ou marché
created_at  → date de première insertion de la ligne
updated_at  → date de dernière mise à jour de la ligne
```

Lors d’un upsert, le collector conserve `created_at` et met uniquement à jour :

```text
name
value
unit
updated_at
```

Index :

```text
idx_macro_series_symbol_observed_at
ux_macro_series_source_symbol_observed_at
```

Contrainte unique :

```text
source + symbol + observed_at
```

---

## Dashboard Grafana

Dashboard officiel :

```text
Crypto Macro Overview SQLite
```

UID officiel :

```text
crypto-macro-overview-sqlite-v2
```

Source de vérité versionnée :

```text
grafana/dashboards/crypto-macro-overview.json
```

Datasource :

```text
Nom : Macro SQLite
UID : macro-sqlite
```

Fichier de provisioning :

```text
grafana/provisioning/datasources/sqlite.yml
```

Chemin SQLite côté Grafana :

```text
/data/macro.db
```

---

## Organisation actuelle du dashboard

Rows actuellement utilisées :

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

> La row contenant les panels Fed et taux s’appelle actuellement `Main`. Son ergonomie est validée et elle peut rester sous ce nom pour le moment.

### Row `Macro Score`

Cette row est ouverte par défaut et contient :

```text
Score macro risk-on/off
Détails du score macro
```

Le panel de gauche affiche le régime sous forme de libellé et de couleur :

```text
0 ou -1   → Contexte respirable → vert
-2 ou -3  → Prudence             → orange
-4 à -8   → Risk-off marqué      → rouge
```

Le panel de droite affiche les huit règles du score avec les colonnes :

```text
Règle
Valeur
Impact
```

La colonne technique `Ordre` est conservée dans la requête SQL pour garantir le classement, mais elle est masquée dans Grafana grâce à une transformation `Organize fields by name`.

Le champ `Impact` reste numérique dans le résultat SQL :

```text
0  → règle non déclenchée
-1 → règle déclenchée
```

Grafana applique un mapping visuel :

```text
0  → Inactive → vert
-1 → Active   → rouge
```

Ce mapping ne modifie pas le calcul : il change uniquement le texte affiché.

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

---

## Score macro risk-on / risk-off v1

Le score v1 est calculé directement dans Grafana via SQL. Il n’est pas stocké dans SQLite.

Objectifs :

```text
produire une synthèse pédagogique du contexte macro
ne déclencher aucun trade
ne pas prétendre prédire le marché
```

### Règles du score v1

```text
VIX >= 20                       → -1
VIX >= 30                       → -1 supplémentaire
USD_BROAD >= 122                → -1
US10Y >= 5                      → -1
Spread 10Y-2Y < 0               → -1
WTI >= 90 ou BRENT >= 90        → -1
Performance SP500 sur 30j < 0   → -1
Performance NASDAQ sur 30j < 0  → -1
```

Le VIX peut donc contribuer jusqu’à `-2` :

```text
VIX < 20        → 0
20 <= VIX < 30  → -1
VIX >= 30       → -2
```

Score possible :

```text
maximum : 0
minimum : -8
```

### Interprétation

```text
0 à -1  → Contexte respirable
-2 à -3 → Prudence
<= -4   → Risk-off marqué
```

### Calcul des performances 30 jours

Pour `SP500` et `NASDAQ`, la requête compare la dernière observation disponible avec la dernière observation disponible située au plus tard 30 jours avant la date de cette dernière observation.

Les règles sont actives lorsque la performance calculée est négative.

### État observé le 13 juillet 2026

Lors de la restauration et de la validation du score, les valeurs affichées étaient approximativement :

```text
VIX                       : 15,84
USD_BROAD                 : 120,69
US10Y                     : 4,54 %
Spread 10Y-2Y             : +0,380 %
WTI / Brent FRED          : 69,60 / 69,56 USD
Performance SP500 sur 30j : +2,56 %
Performance NASDAQ sur 30j: +2,35 %
```

Toutes les règles étaient alors `Inactive`, donnant :

```text
Score  : 0
Régime : Contexte respirable
```

Cet état est une photographie ponctuelle. Les valeurs évolueront après les prochaines collectes.

---

## Horizons temporels Grafana

```text
BTC/USD — CoinGecko                     → Last 7 days
FEDFUNDS — Federal Funds Effective Rate → Last 5 years
US Treasury Yields — FRED               → Last 5 years
US 10Y - 2Y Yield Spread — FRED         → Last 5 years
U.S. Dollar Index — FRED                → Last 5 years
Inflation YoY — FRED                    → Last 10 years
Oil Prices — FRED                       → Last 1 year
VIX — FRED                              → Last 5 years
S&P 500 / Nasdaq base 100 — FRED        → Last 5 years
```

Le dashboard global peut rester sur :

```text
Last 24 hours
```

Les panels macro restent lisibles grâce à leurs horizons spécifiques.

---

## Règles Grafana / SQLite importantes

Les targets SQLite doivent inclure, selon la forme déjà validée dans le projet :

```text
queryText
rawQueryText
rawSql
rawQuery
queryType
timeColumns
```

Les premiers panels avaient affiché `No data` alors que la datasource fonctionnait. L’ajout de `rawQueryText` et `timeColumns` a résolu le problème.

Pour les panels multi-séries, éviter si nécessaire :

```text
time | value | metric
```

Préférer une requête pivotée :

```text
time | SERIE_1 | SERIE_2 | SERIE_3
```

Panels concernés :

```text
US2Y / US10Y / US30Y
WTI / BRENT
CPI YoY / Core CPI YoY / PCE YoY / Core PCE YoY
SP500 / NASDAQ base 100
```

Le spread `10Y-2Y` et le score macro v1 sont calculés directement dans Grafana via SQL. Aucune série supplémentaire n’est stockée pour l’instant.

---

## Workflow Grafana obligatoire

Le dashboard est provisionné depuis :

```text
grafana/dashboards/crypto-macro-overview.json
```

Ce fichier est la source de vérité versionnée.

```text
Grafana UI       → outil d’édition temporaire
JSON provisionné → source de vérité
Git              → historique officiel
```

Workflow :

```text
1. Ouvrir le dashboard officiel.
2. Faire Save as copy si le dashboard provisionné n’est pas directement modifiable.
3. Modifier la copie dans l’UI Grafana.
4. Sauvegarder le panel puis la copie.
5. Exporter la copie via l’API Grafana.
6. Extraire l’objet dashboard de l’enveloppe API.
7. Remplacer grafana/dashboards/crypto-macro-overview.json.
8. Forcer l’UID crypto-macro-overview-sqlite-v2.
9. Forcer le titre Crypto Macro Overview SQLite.
10. Valider le JSON.
11. Redémarrer Grafana.
12. Vérifier le dashboard officiel avec Ctrl+F5 et via l’API.
13. Supprimer la copie temporaire uniquement après validation.
14. Commiter le JSON.
```

Règle absolue :

```text
Ne jamais supprimer la copie avant son export.
Ne jamais considérer une modification UI comme définitive avant son export dans le JSON provisionné et son commit Git.
```

Le workflow détaillé est documenté dans :

```text
DOCS/02-workflow-grafana-dashboard.md
```

---

## TradingView comme complément de lecture

TradingView complète Grafana pour les données de marché plus récentes. TradingView ne remplace pas les séries officielles FRED/EIA.

Exemples :

```text
TVC:US02Y                 → rendement US à 2 ans
TVC:US10Y                 → rendement US à 10 ans
TVC:US30Y                 → rendement US à 30 ans
TVC:US10Y-TVC:US02Y       → spread 10Y-2Y
TVC:DXY                   → Dollar Index
ICEUS:DX1!                → futures continus Dollar Index
TVC:VIX                   → VIX
SP:SPX                    → indice S&P 500
CME_MINI:ES1!             → futures continus E-mini S&P 500
NASDAQ:IXIC               → Nasdaq Composite
NASDAQ:NDX                → Nasdaq 100
NYMEX:CL1!                → futures continus WTI
NYMEX:BZ1!                → futures continus Brent
COINBASE:BTCUSD           → Bitcoin / dollar
CRYPTOCAP:BTC.D           → dominance Bitcoin
```

Différence pétrole :

```text
Grafana WTI / BRENT → prix spot officiels EIA via FRED, différés
CL1! / BZ1!         → contrats futures continus, plus proches du marché actuel
```

Différence S&P 500 :

```text
SP:SPX        → indice au comptant
CME_MINI:ES1! → contrat futures continu E-mini S&P 500
```

Le guide détaillé est prévu dans :

```text
DOCS/03-suivi-macro-tradingview.md
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
python3 -m json.tool \
  grafana/dashboards/crypto-macro-overview.json \
  > /tmp/check-dashboard.json
```

### Redémarrer Grafana

```bash
docker compose restart grafana
```

### Vérifier le dashboard officiel

```bash
curl -sS -u admin:123456 \
  "http://localhost:9070/api/dashboards/uid/crypto-macro-overview-sqlite-v2" \
  | python3 -m json.tool \
  > /tmp/crypto-macro-dashboard-officiel.json
```

### Lister les dashboards

```bash
curl -sS -u admin:123456 \
  "http://localhost:9070/api/search?type=dash-db" \
  | python3 -m json.tool
```

### Vérifier la fraîcheur des séries

```bash
docker compose run --rm --entrypoint python collector - <<'PY'
import sqlite3

conn = sqlite3.connect("/data/macro.db")
conn.row_factory = sqlite3.Row

rows = conn.execute(
    """
    SELECT
        source,
        symbol,
        COUNT(*) AS total_rows,
        MAX(observed_at) AS last_observed_at,
        MAX(updated_at) AS last_updated_at
    FROM macro_series
    GROUP BY source, symbol
    ORDER BY source, symbol
    """
).fetchall()

for row in rows:
    print(dict(row))

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
```

L’étape 16.1 comprend :

```text
restauration de la row Macro Score
rétablissement des huit règles
libellés Contexte respirable / Prudence / Risk-off marqué
couleurs vert / orange / rouge
masquage visuel de la colonne Ordre
mapping Impact : Inactive / Active
huit règles visibles sans pagination
```

---

## État fonctionnel atteint

Le dashboard couvre maintenant :

```text
Fed
rendements US
courbe 10Y-2Y
dollar
inflation
pétrole
stress marché
S&P 500 / Nasdaq
cryptomonnaies
score macro risk-on / risk-off v1
```

Il s’agit d’une première version macro complète, exploitable et lisible.

---

## Prochaines priorités recommandées

```text
1. Exporter le dashboard final depuis la copie Grafana.
2. Vérifier l’UID et le titre officiels.
3. Redémarrer Grafana et valider le dashboard officiel.
4. Supprimer la copie uniquement après validation.
5. Commiter le JSON et le présent prompt actif.
6. Observer le score v1 pendant plusieurs jours.
7. Automatiser le collector avec une solution simple.
8. Envisager ensuite le score macro v2.
```

---

## Évolutions possibles — non prioritaires

### Automatisation du collector

Le collector est encore lancé manuellement :

```bash
docker compose run --rm collector
```

Solutions possibles :

```text
cron côté hôte
boucle simple dans un service Docker
scheduler dédié
séparation des fréquences macro et crypto
```

Fréquences indicatives :

```text
FRED macro      → une fois par jour suffit
CoinGecko crypto → 15 à 60 minutes seulement si nécessaire
```

### Score macro v2

Pistes à étudier après observation du score v1 :

```text
inflation YoY
variation USD_BROAD sur 30 ou 90 jours
variation US10Y sur 30 ou 90 jours
variation du pétrole sur 30 jours
BTC sur 7 ou 30 jours si la collecte devient régulière
pondérations ajustées après observation
```

### Historisation du score

Évolution possible :

```text
calculer le score dans le collector
stocker MACRO_SCORE dans SQLite
historiser observed_at / created_at / updated_at
afficher les changements de régime dans Grafana
```

### Alertes visuelles non-trading

```text
score <= -4
VIX >= 30
USD_BROAD >= 122
US10Y >= 5
WTI ou Brent >= 90
```

Ces alertes doivent rester purement informatives et ne déclencher aucun ordre.

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
des fichiers complets lorsque nécessaire
aucune sur-architecture prématurée
```

Lorsque du code ou de la configuration est proposé, fournir systématiquement :

```text
1. le chemin du fichier
2. le contenu complet du fichier
3. la commande à exécuter
4. la commande de vérification
5. le message de commit Git en français
```

Les messages de commit doivent être en français.

Pour la restauration du score et la mise à jour documentaire :

```bash
git commit -m "fix: restaure et améliore le score macro risk-on risk-off"
git commit -m "docs: met a jour le prompt actif apres la restauration du score macro"
```

Un seul commit peut aussi regrouper le JSON et la documentation si les deux modifications appartiennent à la même étape fonctionnelle :

```bash
git commit -m "fix: restaure et documente le score macro risk-on risk-off"
```

---

## Ce que je veux maintenant

Je veux continuer progressivement à partir de cet état, sans repartir de zéro.

Toujours tenir compte du fait que le projet contient déjà :

```text
Grafana opérationnel
collector Python Dockerisé
SQLite
FRED FEDFUNDS
FRED US2Y / US10Y / US30Y
inflation CPI / CORE_CPI / PCE / CORE_PCE
pétrole WTI / BRENT
dollar USD_BROAD
VIX / SP500 / NASDAQ
courbe 10Y-2Y calculée dans Grafana
score macro risk-on / risk-off v1 calculé dans Grafana
libellé visuel du régime macro
état Active / Inactive pour chaque règle
CoinGecko BTC / ETH / SOL / HYPE
dashboard Grafana provisionné
rows Macro Score / Main / Dollar / Inflation / Energy / Market / Cryptos / Datas
panels macro avec horizons temporels cohérents
workflow Grafana par copie puis export JSON
modèle SQLite avec observed_at / created_at / updated_at
support documentaire TradingView comme complément de lecture
```

Ne pas simplifier en oubliant l’objectif macro complet. Ne pas proposer de déclenchement automatique de trades.

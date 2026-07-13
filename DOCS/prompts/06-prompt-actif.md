# Prompt actif final — Projet `crypto-macro-dashboard`

## Contexte

Je travaille sur un projet Docker local nommé :

```text
crypto-macro-dashboard
```

Dashboard Grafana :

```text
http://localhost:9070
```

Le projet sert à suivre le contexte macroéconomique et crypto pour mieux interpréter les signaux de mon bot Freqtrade / Hyperliquid.

Le dashboard ne doit déclencher aucun trade automatiquement. Il sert uniquement de filtre de contexte :

```text
risk-on / neutre / risk-off
```

Approche attendue :

```text
progressive
simple
lisible
pédagogique
sans sur-architecture prématurée
```

---

## Objectif fonctionnel

Le dashboard couvre :

```text
Fed
taux et rendements US
courbe 10Y-2Y
force du dollar
inflation
pétrole
stress de marché
S&P 500 / Nasdaq
cryptomonnaies
score macro synthétique
```

Le dashboard doit aider à répondre aux questions suivantes :

```text
Le contexte macro est-il favorable ou défavorable ?
Le marché est-il plutôt risk-on, neutre ou risk-off ?
Les taux ou le dollar pèsent-ils sur les cryptos ?
L’inflation, le pétrole ou la Fed rendent-ils le marché plus fragile ?
Faut-il être plus prudent avec les entrées Freqtrade / Hyperliquid ?
```

Le dashboard ne cherche pas à prédire le marché. Il contextualise les signaux du bot et encourage une lecture prudente du régime macro.

---

## Stack actuelle

```text
Docker
Docker Compose
Grafana
Python
Bash
SQLite
FRED API
CoinGecko keyless API
Markdown
Git
```

Base SQLite :

```text
data/macro.db
```

Une migration vers PostgreSQL, InfluxDB ou Prometheus n’est pas prioritaire tant que SQLite répond correctement au besoin.

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
│       ├── 05-prompt-actif-final.md
│       └── 06-prompt-actif-final.md
├── grafana/
│   ├── dashboards/
│   │   └── crypto-macro-overview.json
│   └── provisioning/
│       ├── dashboards/
│       │   └── dashboards.yml
│       └── datasources/
│           └── sqlite.yml
├── scripts/
│   ├── publish-grafana-copy.sh
│   └── refresh-data.sh
└── README.md
```

Le dossier `DOCS/prompts` conserve les prompts actifs du plus ancien au plus récent.

Le guide TradingView peut être conservé dans :

```text
DOCS/03-suivi-macro-tradingview.md
```

s’il est effectivement présent dans le dépôt.

---

## Services Docker

### `grafana`

```text
Image : grafana/grafana-oss:latest
Port  : 9070:3000
Compte local : admin / 123456
Plugin : frser-sqlite-datasource
```

Variable :

```text
GF_PLUGINS_PREINSTALL_SYNC=frser-sqlite-datasource
```

Volumes :

```text
./grafana/provisioning:/etc/grafana/provisioning
./grafana/dashboards:/var/lib/grafana/dashboards
./data:/data
```

### `collector`

Le collector est construit depuis :

```text
./collector
```

Configuration principale :

```text
DB_PATH=/data/macro.db
```

Le collector charge `.env` et reste un job ponctuel. Il peut être lancé directement :

```bash
docker compose run --rm collector
```

Le mode manuel recommandé est désormais :

```bash
./scripts/refresh-data.sh
```

Le collector ne contient ni boucle infinie ni scheduler.

```text
Grafana relit SQLite mais ne collecte aucune donnée.
Les données changent uniquement lorsque le collector est exécuté.
Aucun redémarrage de Grafana n’est nécessaire après une collecte.
```

---

## APIs utilisées

```text
FRED_API_KEY
FRED_BASE_URL=https://api.stlouisfed.org/fred
COINGECKO_BASE_URL=https://api.coingecko.com/api/v3
```

`COINGECKO_API_KEY` reste une option future. L’usage actuel est keyless.

---

## Séries FRED

### Fed et taux

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

Les indices bruts sont stockés dans SQLite. Grafana calcule les variations annuelles :

```text
YoY % = (valeur actuelle / valeur il y a 12 mois - 1) × 100
```

### Pétrole

```text
DCOILWTICO   → WTI   → Crude Oil Price WTI
DCOILBRENTEU → BRENT → Crude Oil Price Brent
```

Unité :

```text
usd_per_barrel
```

Les prix correspondent aux données spot officielles EIA relayées par FRED. Ils peuvent être publiés avec plusieurs jours de retard et ne doivent pas être confondus avec les futures TradingView.

### Dollar

```text
DTWEXBGS → USD_BROAD → Nominal Broad U.S. Dollar Index
```

`USD_BROAD` est un proxy large de la force du dollar. Il ne doit pas être confondu avec :

```text
TVC:DXY    → Dollar Index TradingView
ICEUS:DX1! → futures continus Dollar Index
```

### Marché et stress

```text
VIXCLS    → VIX    → CBOE Volatility Index
SP500     → SP500  → S&P 500
NASDAQCOM → NASDAQ → Nasdaq Composite
```

### Limites d’historique

```text
FEDFUNDS  → 120
US2Y      → 1500
US10Y     → 1500
US30Y     → 1500
CPI       → 240
CORE_CPI  → 240
PCE       → 240
CORE_PCE  → 240
WTI       → 1500
BRENT     → 1500
USD_BROAD → 1500
VIX       → 1500
SP500     → 1500
NASDAQ    → 1500
```

Les valeurs FRED vides `.` sont ignorées.

---

## CoinGecko

Actifs :

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

Éviter le polling fréquent en mode keyless.

---

## Modèle SQLite

Table :

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

Sémantique :

```text
observed_at → date réelle de l’observation
created_at  → date de première insertion
updated_at  → date de dernière mise à jour
```

Lors d’un upsert, `created_at` est conservé. Sont mis à jour :

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

```text
Titre officiel : Crypto Macro Overview SQLite
UID officiel   : crypto-macro-overview-sqlite-v2
Fichier source : grafana/dashboards/crypto-macro-overview.json
Datasource     : Macro SQLite
UID datasource : macro-sqlite
Chemin SQLite  : /data/macro.db
```

Rows :

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

La row `Main` contient les panels Fed et taux. Son ergonomie est validée.

### `Macro Score`

Contient :

```text
Score macro risk-on/off
Détails du score macro
```

Régime visuel :

```text
0 ou -1  → Contexte respirable → vert
-2 ou -3 → Prudence             → orange
-4 à -8  → Risk-off marqué      → rouge
```

Le tableau détaille :

```text
Règle
Valeur
Impact
```

La colonne technique `Ordre` reste dans le SQL mais est masquée avec `Organize fields by name`.

Mapping visuel du champ `Impact` :

```text
0  → Inactive → vert
-1 → Active   → rouge
```

Le mapping ne change pas le calcul SQL.

### `Main`

```text
Dernier FEDFUNDS
FEDFUNDS — Federal Funds Effective Rate
Derniers rendements US
US Treasury Yields — FRED
US 10Y - 2Y Yield Spread — FRED
Dernier spread 10Y-2Y
```

### `Dollar`

```text
Dernier dollar broad
U.S. Dollar Index — FRED
```

### `Inflation`

```text
Dernière inflation YoY
Inflation YoY — FRED
```

### `Energy`

```text
Derniers prix pétrole
Oil Prices — FRED
```

### `Market`

```text
Dernier stress marché
VIX — FRED
S&P 500 / Nasdaq base 100 — FRED
```

### `Cryptos`

```text
BTC/USD — CoinGecko
Derniers prix crypto USD
Dernier BTC/USD
```

### `Datas`

```text
Données crypto
Dernières données macro_series
```

---

## Score macro v1

Le score est calculé dans Grafana via SQL et n’est pas stocké dans SQLite.

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

```text
score maximum : 0
score minimum : -8
```

Interprétation :

```text
0 à -1  → Contexte respirable
-2 à -3 → Prudence
<= -4   → Risk-off marqué
```

Le 13 juillet 2026, lors de la validation :

```text
VIX                       : 15,84
USD_BROAD                 : 120,69
US10Y                     : 4,54 %
Spread 10Y-2Y             : +0,380 %
WTI / Brent FRED          : 69,60 / 69,56 USD
Performance SP500 sur 30j : +2,56 %
Performance NASDAQ sur 30j: +2,35 %
Score                     : 0
Régime                    : Contexte respirable
```

Cette photographie évolue après les collectes.

---

## Règles Grafana / SQLite

Les targets SQLite doivent conserver selon les cas :

```text
queryText
rawQueryText
rawSql
rawQuery
queryType
timeColumns
```

Pour les panels multi-séries, préférer les requêtes pivotées :

```text
time | SERIE_1 | SERIE_2 | SERIE_3
```

Le spread `10Y-2Y` et le score macro v1 restent calculés dans Grafana.

---

## Étape 17 — Rafraîchissement manuel des données

Fichier :

```text
scripts/refresh-data.sh
```

Commande :

```bash
./scripts/refresh-data.sh
```

Le script :

```text
trouve automatiquement la racine du projet
vérifie Docker et Docker Compose
vérifie docker-compose.yml et .env
utilise flock contre les doubles collectes
lance le collector
contrôle la fraîcheur des séries
affiche observed_at et updated_at
retourne un code de sortie fiable
```

Verrou :

```text
/tmp/crypto-macro-dashboard-refresh.lock
```

Le script ne redémarre pas Grafana.

---

## Étape 18 — Publication sécurisée d’une copie Grafana

Statut :

```text
VALIDÉE ET TESTÉE LE 13 JUILLET 2026
```

Le script a été testé avec une copie réelle du dashboard, y compris avec une modification volontaire du titre protégé `Macro Score`. Le contrôle a correctement interrompu la publication avant toute modification du JSON officiel, tout redémarrage de Grafana et toute suppression de copie.

Fichier :

```text
scripts/publish-grafana-copy.sh
```

Commande interactive :

```bash
./scripts/publish-grafana-copy.sh
```

Le workflow devient :

```text
1. Ouvrir le dashboard officiel.
2. Faire Save as copy.
3. Modifier et sauvegarder la copie dans Grafana.
4. Lancer publish-grafana-copy.sh.
5. Choisir la copie si plusieurs copies existent.
6. Confirmer la publication.
7. Laisser le script exporter, valider et provisionner le dashboard.
8. Vérifier visuellement le dashboard officiel avec Ctrl+F5.
9. Supprimer la copie avec --delete-copy après validation.
10. Inspecter le diff Git et commiter.
```

### Fonctions du script

```text
vérification de Grafana
recherche des copies
sélection interactive si plusieurs copies existent
sélection directe avec --uid
export par l’API Grafana
rétablissement de l’UID et du titre officiels
validation JSON
validation des IDs de panels
validation minimale des targets macro-sqlite
sauvegarde temporaire du JSON actuel
remplacement du JSON provisionné
contrôle git diff --check
redémarrage et attente de Grafana
comparaison API entre dashboard officiel et JSON provisionné
restauration automatique en cas d’échec
suppression facultative de la copie
```

Options :

```text
--uid UID       → sélectionner directement une copie
--delete-copy   → proposer sa suppression après validation
--yes           → répondre automatiquement aux confirmations
--help          → afficher l’aide
```

Variables :

```text
GRAFANA_URL=http://localhost:9070
GRAFANA_USER=admin
GRAFANA_PASSWORD=123456
```

Verrou :

```text
/tmp/crypto-macro-dashboard-publish.lock
```

### Structure protégée

Le script exige actuellement :

```text
Macro Score
Score macro risk-on/off
Détails du score macro
```

Ce garde-fou a été testé en renommant volontairement la row `Macro Score` en `Macro Score test` dans une copie. Le script a listé les titres trouvés, signalé `Macro Score` comme absent, puis s’est arrêté avec un code d’erreur avant toute publication.

La comparaison normalise :

```text
casse
accents
espaces superflus
```

Conséquences :

```text
renommer Macro Score                       → refusé
renommer Score macro risk-on/off            → refusé
renommer Détails du score macro             → refusé
renommer une autre row                      → autorisé
renommer un autre panel                     → autorisé
ajouter une row ou un panel                 → autorisé
supprimer un panel non protégé              → potentiellement autorisé
modifier les requêtes SQL                   → autorisé si la structure minimale reste présente
```

Le script protège aussi :

```text
UID et titre officiels
présence générale de panels
absence d’IDs de panels dupliqués
queryText, rawQueryText et timeColumns pour macro-sqlite
validité JSON
redémarrage de Grafana
égalité entre JSON provisionné et dashboard officiel hors id/version
```

Le script ne valide pas automatiquement :

```text
la pertinence métier du SQL
les seuils macro
les mappings visuels
les horizons temporels
la présence de tous les panels non protégés
la qualité visuelle de la mise en page
```

La vérification visuelle et le diff Git restent obligatoires.

### Suppression de la copie

Par défaut, aucune copie n’est supprimée.

Pour proposer la suppression après validation :

```bash
./scripts/publish-grafana-copy.sh \
  --uid UID_DE_LA_COPIE \
  --delete-copy
```

Ne jamais supprimer une copie avant son export et la validation complète du dashboard officiel.

---

## Validation réalisée du script de publication

Le script `scripts/publish-grafana-copy.sh` a été testé le 13 juillet 2026 avec la copie Grafana :

```text
Titre : Crypto Macro Overview SQLite Copy
UID   : adjvnzl
```

### Test de détection de copie

Résultat validé :

```text
Grafana accessible
une copie détectée automatiquement
UID et titre de la copie affichés
confirmation demandée avant publication
```

### Test du garde-fou structurel

Modification volontaire dans la copie :

```text
Macro Score → Macro Score test
```

Résultat obtenu :

```text
les titres présents ont été listés
Macro Score a été signalé comme absent
la publication a été interrompue avec un code différent de zéro
le JSON officiel n’a pas été remplacé
Grafana n’a pas été redémarré
la copie n’a pas été supprimée
```

Ce test confirme que le script bloque une copie dont la structure protégée a été modifiée.

### Portée de la protection

Titres protégés :

```text
Macro Score
Score macro risk-on/off
Détails du score macro
```

Les autres rows et panels peuvent être renommés. Le script reste un garde-fou ciblé et non un validateur métier exhaustif.

### Statut opérationnel

```text
scripts/publish-grafana-copy.sh → testé, validé et prêt à l’usage
```

---

## TradingView comme complément

Principaux symboles :

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

```text
Grafana WTI / BRENT → prix spot officiels EIA/FRED, différés
CL1! / BZ1!         → contrats futures continus
SP:SPX              → indice au comptant
CME_MINI:ES1!       → futures continus E-mini S&P 500
```

---

## Commandes utiles

### Rafraîchir les données

```bash
./scripts/refresh-data.sh
```

### Publier une copie Grafana

```bash
./scripts/publish-grafana-copy.sh
```

### Publier une copie connue

```bash
./scripts/publish-grafana-copy.sh --uid UID_DE_LA_COPIE
```

### Publier puis proposer la suppression

```bash
./scripts/publish-grafana-copy.sh \
  --uid UID_DE_LA_COPIE \
  --delete-copy
```

### Vérifier les scripts

```bash
bash -n scripts/refresh-data.sh
bash -n scripts/publish-grafana-copy.sh
```

### Lancer Grafana

```bash
docker compose up -d grafana
```

### Lancer directement le collector

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

### Vérifier le JSON provisionné

```bash
python3 -m json.tool \
  grafana/dashboards/crypto-macro-overview.json \
  > /tmp/check-dashboard.json
```

### Lister les dashboards Grafana

```bash
curl -sS -u admin:123456 \
  "http://localhost:9070/api/search?type=dash-db" \
  | python3 -m json.tool
```

### Vérifier le dashboard officiel

```bash
curl -sS -u admin:123456 \
  "http://localhost:9070/api/dashboards/uid/crypto-macro-overview-sqlite-v2" \
  | python3 -m json.tool \
  > /tmp/crypto-macro-dashboard-officiel.json
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
Étape 9.1  — Horizons temporels                         DONE
Étape 10   — Rendements US                              DONE
Étape 10.1 — Panels rendements US                       DONE
Étape 10.2 — Historique FRED étendu                     DONE
Étape 11   — Courbe 10Y-2Y                              DONE
Étape 12   — Inflation                                  DONE
Étape 12.2 — Panels inflation YoY                       DONE
Étape 13   — Pétrole WTI / Brent                        DONE
Étape 13.2 — Panels pétrole                             DONE
Étape 14   — Dollar USD_BROAD                           DONE
Étape 14.2 — Panels dollar                              DONE
Étape 15   — VIX / SP500 / NASDAQ                       DONE
Étape 15.2 — Panels Market                              DONE
Étape 16   — Score macro v1                             DONE
Étape 16.1 — Restauration et amélioration UX du score   DONE
Étape 17   — Script manuel de rafraîchissement          DONE
Étape 18   — Publication sécurisée d’une copie Grafana  DONE — TESTÉE ET VALIDÉE
```

---

## Évolutions reportées ou non prioritaires

### Cron

Le script `refresh-data.sh` est compatible avec un futur cron. Aucun cron n’est configuré actuellement.

### Score v2

À étudier uniquement après observation du score v1 :

```text
inflation YoY
variations USD_BROAD, US10Y et pétrole
BTC 7j / 30j si la collecte devient régulière
pondérations éventuelles
```

### Historisation du score

Reportée :

```text
calcul dans le collector
stockage de MACRO_SCORE
historique des régimes
```

Le score actuel reste calculé dans Grafana.

### Alertes

Éventuelles alertes informatives uniquement :

```text
score <= -4
VIX >= 30
USD_BROAD >= 122
US10Y >= 5
WTI ou Brent >= 90
```

Aucune alerte ne doit déclencher de trade.

---

## Prochaines priorités

```text
1. Commiter le script publish-grafana-copy.sh validé et ce prompt actif.
2. Utiliser publish-grafana-copy.sh pour les prochaines modifications Grafana.
3. Conserver une vérification visuelle du dashboard officiel avant chaque commit.
4. Utiliser refresh-data.sh pour actualiser les données selon le besoin.
5. Observer le score v1 avant de modifier ses règles.
6. Envisager un cron uniquement si l’exécution manuelle devient contraignante.
7. Reporter le score v2 et l’historisation tant qu’un besoin concret n’est pas établi.
```

---

## Contraintes de travail

Je travaille avec :

```text
Docker
Docker Compose
Linux / WSL2
Python
Bash
Grafana
SQLite
Markdown
Git
```

Je souhaite :

```text
une étape à la fois
des explications simples
des commandes claires
des fichiers complets lorsque nécessaire
aucune sur-architecture prématurée
```

Pour chaque évolution de code ou configuration, fournir :

```text
1. le chemin du fichier
2. le contenu complet du fichier
3. la commande à exécuter
4. la commande de vérification
5. un message de commit Git en français
```

Exemples de commits récents :

```bash
git commit -m "fix: restaure et améliore le score macro risk-on risk-off"
git commit -m "feat: ajoute un script de rafraichissement des donnees"
git commit -m "feat: automatise la publication du dashboard grafana"
git commit -m "docs: documente la validation du script de publication grafana"
```

---

## État à conserver pour la suite

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
score macro v1 calculé dans Grafana
libellés visuels de régime
états Active / Inactive des règles
CoinGecko BTC / ETH / SOL / HYPE
dashboard Grafana provisionné
rows Macro Score / Main / Dollar / Inflation / Energy / Market / Cryptos / Datas
workflow par copie Grafana puis publication sécurisée
script scripts/refresh-data.sh
script scripts/publish-grafana-copy.sh testé et validé
protection flock pour les deux scripts
validation et retour arrière automatiques lors de la publication
contrôle testé des titres protégés avant toute modification du dashboard officiel
modèle SQLite avec observed_at / created_at / updated_at
```

Ne pas repartir de zéro. Ne pas oublier l’objectif macro complet. Ne proposer aucun déclenchement automatique de trades.

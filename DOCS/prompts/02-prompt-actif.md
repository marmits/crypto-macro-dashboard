# Prompt actif — Projet `crypto-macro-dashboard`

## État actuel du projet

Le projet Docker `crypto-macro-dashboard` est initialisé et plusieurs étapes sont maintenant validées.

Le dashboard Grafana est accessible localement sur :

```text
http://localhost:9070
````

Le projet permet actuellement de collecter des données macroéconomiques et crypto, de les stocker en SQLite, puis de les afficher dans Grafana.

La chaîne suivante est validée :

```text
FRED API -> Collector Python -> SQLite -> Grafana
```

La chaîne suivante est également validée :

```text
CoinGecko keyless API -> Collector Python -> SQLite -> Grafana
```

Le dashboard ne déclenche aucun trade automatiquement.

Il sert uniquement de filtre de contexte macro / crypto :

```text
risk-on / risk-off
```

L’approche du projet doit rester progressive, simple, lisible et pédagogique.

***

## Objectif général du projet

Créer un dashboard local permettant de suivre le contexte macroéconomique et crypto afin de mieux interpréter les signaux de mon bot Freqtrade / Hyperliquid.

Le dashboard doit aider à répondre à des questions du type :

```text
Le contexte macro est-il favorable ?
Le marché est-il plutôt risk-on ou risk-off ?
Faut-il être prudent avec les entrées Freqtrade ?
Le BTC et les actifs crypto sont-ils soutenus ou fragilisés par le contexte macro ?
```

Le dashboard ne doit pas déclencher de trades automatiquement au départ.

Il sert uniquement d’aide à la décision.

***

## Stack actuelle

La stack utilisée est :

```text
Docker
Docker Compose
Grafana
Python
SQLite
FRED API
CoinGecko API keyless
Markdown
Git
```

La base de données actuelle est :

```text
SQLite
```

Le fichier SQLite local est :

```text
data/macro.db
```

Une migration future vers PostgreSQL, InfluxDB ou Prometheus pourra être envisagée plus tard, mais ce n’est pas prioritaire.

***

## Objectif fonctionnel final du dashboard

Le but final du projet `crypto-macro-dashboard` n’est pas seulement d’afficher BTC et FEDFUNDS.

L’objectif est de construire progressivement un dashboard local permettant de suivre le contexte macroéconomique et crypto autour des grands axes suivants :

```text
Fed
taux
force du dollar
rendements US
pétrole
inflation
marché risk-on / risk-off
````

Le dashboard doit aider à interpréter les signaux de mon bot Freqtrade / Hyperliquid en fournissant un contexte global de marché.

Il ne doit pas déclencher de trades automatiquement au départ.

Il doit uniquement servir de filtre de contexte :

```text
risk-on / risk-off
```

***

## Indicateurs cibles à intégrer progressivement

Les indicateurs déjà intégrés ou à intégrer progressivement sont :

### Fed / politique monétaire

```text
FEDFUNDS
Fed Funds Rate
éventuellement taux directeurs / indicateurs de politique monétaire
```

Statut actuel :

```text
FEDFUNDS est déjà collecté depuis FRED et affiché dans Grafana.
```

***

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
Identifier les phases où les rendements montent fortement.
Mesurer la pente ou l’inversion de la courbe des taux.
```

***

### Force du dollar

À intégrer progressivement :

```text
DXY
ou équivalent gratuit / proxy dollar
```

Objectif :

```text
Suivre la force du dollar.
Un dollar fort est souvent défavorable aux actifs risqués et aux cryptos.
```

Source à discuter :

```text
source gratuite fiable pour DXY ou proxy dollar
```

***

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

Source à discuter :

```text
FRED si disponible
autre source gratuite si nécessaire
```

***

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

Source pressentie :

```text
FRED API
```

***

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

Objectif :

```text
Comparer les actifs risqués traditionnels et crypto.
Détecter un contexte risk-on, neutre ou risk-off.
```

Statut actuel crypto :

```text
BTC, ETH, SOL et HYPE sont déjà collectés depuis CoinGecko keyless et affichés dans Grafana.
```

***

## Dashboard cible à terme

Le dashboard final doit évoluer vers une structure de ce type :

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

***

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

Il ne doit pas chercher à prédire le marché parfaitement.

Son objectif est uniquement d’aider à contextualiser les signaux Freqtrade / Hyperliquid.

````

---

# Petite correction à faire aussi dans la synthèse finale

Dans la section :

```markdown
## Prochaine étape proposée
````

Je modifierais la phrase actuelle :

```text
Étape 10 — Préparer un premier score risk-on / risk-off simple
```

en une version plus complète :

````markdown
## Prochaines étapes proposées

Les prochaines étapes doivent maintenant enrichir progressivement le dashboard vers son objectif fonctionnel final :

```text
Fed
taux
force du dollar
rendements US
pétrole
inflation
marché risk-on / risk-off
````

Priorité possible :

```text
Étape 10 — Ajouter les rendements US depuis FRED : US2Y, US10Y, US30Y
Étape 11 — Ajouter la courbe 10Y - 2Y
Étape 12 — Ajouter inflation : CPI / Core CPI / PCE / Core PCE
Étape 13 — Ajouter pétrole : WTI / Brent
Étape 14 — Ajouter dollar : DXY ou proxy gratuit
Étape 15 — Ajouter VIX / Nasdaq / S&P 500 si source gratuite fiable
Étape 16 — Construire un premier score risk-on / risk-off simple
```

Le score risk-on / risk-off doit venir après quelques indicateurs macro supplémentaires, pour éviter de construire un score basé uniquement sur FEDFUNDS et les cryptos.

````

---

# Ma recommandation

Oui, il faut ajouter cette partie au prompt actif.  
Sinon, une nouvelle conversation pourrait croire que le projet est maintenant principalement :

```text
FEDFUNDS + crypto Grafana
````

alors que ton objectif final est bien plus large :

```text
macro complète + crypto + contexte risk-on / risk-off
```

## Arborescence actuelle

L’arborescence globale du projet est de ce type :

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
│     └── 02-prompt-actif-final-temporaire.md
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

***

## Services Docker

Le projet utilise au minimum deux services Docker :

```text
grafana
collector
```

### Service `grafana`

Objectif :

```text
Afficher le dashboard local sur http://localhost:9070
```

Grafana utilise le plugin SQLite :

```text
frser-sqlite-datasource
```

Le dashboard Grafana est provisionné depuis :

```text
grafana/dashboards/crypto-macro-overview.json
```

La datasource SQLite est provisionnée depuis :

```text
grafana/provisioning/datasources/sqlite.yml
```

### Service `collector`

Objectif :

```text
Collecter les données macro et crypto
Créer / migrer la base SQLite
Insérer ou mettre à jour les observations
Afficher des logs simples
Se terminer proprement
```

Le collector est actuellement un job ponctuel lancé manuellement avec :

```bash
docker compose run --rm collector
```

Il ne contient pas encore de boucle infinie ni de scheduler.

***

## Statut des étapes

### Étape 1 — Grafana local

Statut :

```text
DONE
```

Objectif :

```text
Faire tourner Grafana sur http://localhost:9070
```

Résultat :

```text
Grafana est lancé et accessible.
```

***

### Étape 2 — Collector Python minimal + SQLite

Statut :

```text
DONE
```

Objectif :

```text
Créer un collector Python minimal
Créer une base SQLite locale
Créer une table macro_series
Insérer une première donnée de test
Ajouter le service collector dans docker-compose.yml
Vérifier que le fichier data/macro.db est bien créé
```

Résultat :

```text
Le collector Dockerisé écrit correctement dans SQLite.
La base data/macro.db est créée.
La table macro_series existe.
Des données de test ont été insérées.
```

***

### Étape 3 — Première métrique FRED

Statut :

```text
DONE
```

Métrique collectée :

```text
FEDFUNDS
```

Description :

```text
Federal Funds Effective Rate
```

Source :

```text
FRED API
```

Résultat :

```text
Le collector récupère les observations FEDFUNDS via FRED.
Les données sont stockées dans SQLite dans macro_series.
Les observations sont upsertées proprement.
```

***

### Étape 4 — Grafana connecté à SQLite

Statut :

```text
DONE
```

Objectif :

```text
Configurer Grafana pour lire la base SQLite
Créer une datasource provisionnée
Créer un dashboard provisionné
Afficher FEDFUNDS dans Grafana
```

Résultat :

```text
La datasource SQLite Grafana fonctionne.
Le dashboard provisionné affiche correctement FEDFUNDS.
```

Le dashboard affiche notamment :

```text
Dernier FEDFUNDS
Courbe FEDFUNDS
Table macro_series
```

***

### Point technique résolu — Grafana SQLite

Problème rencontré :

```text
Les premiers panels Grafana affichaient No data alors que la datasource SQLite fonctionnait.
```

Cause :

```text
Le JSON du dashboard provisionné n’était pas totalement compatible avec Grafana 13 + plugin frser-sqlite-datasource.
```

Correction :

```text
Ajout des champs rawQueryText et timeColumns dans les targets du dashboard JSON,
en plus de queryText, rawSql, rawQuery et queryType.
```

Statut :

```text
FRED -> Python collector -> SQLite -> Grafana est validé.
```

***

### Étape 5 — CoinGecko BTC/USD

Statut :

```text
DONE
```

Objectif :

```text
Collecter BTC/USD via CoinGecko
Stocker BTC dans SQLite
Afficher BTC dans Grafana
```

CoinGecko est utilisé en mode :

```text
keyless public API
```

Aucune clé API CoinGecko n’est utilisée.

Base URL utilisée :

```text
https://api.coingecko.com/api/v3
```

Endpoint utilisé :

```text
/simple/price
```

Paramètres utilisés pour BTC :

```text
ids=bitcoin
vs_currencies=usd
include_24hr_change=true
include_last_updated_at=true
```

La donnée BTC est stockée dans SQLite dans `macro_series` avec :

```text
source = coingecko
symbol = BTC
name = Bitcoin
unit = usd
```

***

### Étape 6 — Panels Grafana BTC/USD

Statut :

```text
DONE
```

Le dashboard Grafana affiche maintenant :

```text
Dernier FEDFUNDS
Dernier BTC/USD
Courbe FEDFUNDS
Courbe BTC/USD
Table crypto filtrée sur source = coingecko
Table globale macro_series
```

La collecte BTC/USD via CoinGecko keyless fonctionne et plusieurs observations BTC sont stockées dans SQLite.

Remarque :

```text
Le graphe BTC/USD peut sembler vertical ou peu lisible au début,
car il y a peu de points BTC et le dashboard peut être affiché sur Last 2 years.
```

Amélioration future possible :

```text
Appliquer une période relative courte aux panels crypto, par exemple now-24h.
```

***

### Étape 7 — ETH, SOL et HYPE via CoinGecko

Statut :

```text
DONE
```

Le collector CoinGecko collecte maintenant plusieurs actifs :

```text
BTC
ETH
SOL
HYPE
```

Mapping CoinGecko utilisé :

```text
BTC  -> bitcoin
ETH  -> ethereum
SOL  -> solana
HYPE -> hyperliquid
```

Les données sont stockées dans SQLite dans `macro_series` avec :

```text
source = coingecko
symbol = BTC / ETH / SOL / HYPE
unit = usd
```

CoinGecko est utilisé en mode keyless public API, donc sans clé API.

Les appels doivent rester raisonnables, car les quotas keyless sont limités par IP.

***

### Étape 8 — Panels crypto multi-actifs Grafana

Statut :

```text
DONE
```

Le dashboard Grafana affiche maintenant un panel multi-actifs :

```text
Derniers prix crypto USD
```

Ce panel affiche :

```text
BTC_USD
ETH_USD
SOL_USD
HYPE_USD
```

Le dashboard contient également une table crypto basée sur :

```text
source = coingecko
```

Cette étape a permis de mieux visualiser les actifs crypto collectés via CoinGecko.

***

### Étape 9 — Modèle SQLite avec `updated_at`

Statut :

```text
DONE
```

La table `macro_series` contient maintenant :

```text
created_at
updated_at
```

Règle retenue :

```text
observed_at = date réelle de l’observation économique ou marché
created_at  = date de première insertion de la ligne
updated_at  = date de dernière mise à jour de la ligne
```

Cette distinction est utile car les séries FRED sont ré-upsertées à chaque collecte.

Les lignes FRED gardent le même `observed_at`, mais leur `updated_at` évolue lors des refreshs.

L’upsert SQLite ne modifie plus `created_at`.

Il met uniquement à jour :

```text
name
value
unit
updated_at
```

Petite amélioration future possible :

```text
Mettre à jour les tables Grafana pour afficher aussi updated_at.
```

***

## Structure SQLite actuelle

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

Exemples de sources :

```text
fred
coingecko
test
```

Exemples de symboles :

```text
FEDFUNDS
BTC
ETH
SOL
HYPE
TEST_MACRO_SCORE
```

Exemples d’unités :

```text
percent
usd
score
```

***

## Sources de données actuelles

### FRED API

Utilisée pour les données macro officielles.

Série actuellement collectée :

```text
FEDFUNDS
```

Objectif futur :

```text
Ajouter progressivement US2Y, US10Y, US30Y, CPI, Core CPI, PCE, Core PCE, etc.
```

***

### CoinGecko API keyless

Utilisée pour les données crypto.

Aucune clé API CoinGecko n’est utilisée.

Endpoint principal :

```text
https://api.coingecko.com/api/v3/simple/price
```

Actifs actuellement collectés :

```text
BTC
ETH
SOL
HYPE
```

Mapping CoinGecko :

```text
bitcoin     -> BTC
ethereum    -> ETH
solana      -> SOL
hyperliquid -> HYPE
```

Paramètres utilisés :

```text
vs_currencies=usd
include_24hr_change=true
include_last_updated_at=true
```

Attention :

```text
Le mode keyless est adapté au prototype local,
mais il ne faut pas faire de polling trop fréquent.
```

***

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

Le dashboard affiche actuellement :

```text
Derniers prix crypto USD
Dernier FEDFUNDS
Dernier BTC/USD
Courbe FEDFUNDS
Courbe BTC/USD
Table Données crypto
Table Dernières données macro_series
```

***

## Workflow Grafana important

Le dashboard Grafana est provisionné depuis le fichier :

```text
grafana/dashboards/crypto-macro-overview.json
```

Ce fichier est la source de vérité versionnée dans Git.

Le dashboard provisionné ne doit pas être modifié directement depuis l’UI Grafana comme source définitive.

Grafana peut refuser de sauvegarder directement le dashboard provisionné depuis l’UI et proposer :

```text
Save as copy
Copy JSON to clipboard
Save JSON to file
```

Workflow recommandé pour modifier le dashboard :

```text
1. Faire Save as copy dans Grafana
2. Modifier la copie dans l’UI Grafana
3. Sauvegarder la copie
4. Exporter la copie via l’API Grafana
5. Remplacer grafana/dashboards/crypto-macro-overview.json avec l’export
6. Forcer l’UID officiel crypto-macro-overview-sqlite-v2
7. Redémarrer Grafana
8. Vérifier que le dashboard officiel contient bien les modifications
9. Supprimer la copie dans Grafana
10. Commiter le JSON
```

Règle importante :

```text
Ne jamais considérer une modification UI comme définitive tant qu’elle n’a pas été exportée dans grafana/dashboards/crypto-macro-overview.json et commitée.
```

En résumé :

```text
Grafana UI = outil d’édition visuelle temporaire
JSON provisionné = source de vérité
Git = historique officiel
```

***

## Commandes utiles Grafana

Lister les dashboards :

```bash
curl -s -u admin:123456 "http://localhost:9070/api/search?query=Crypto" | python3 -m json.tool
```

Exporter un dashboard par UID :

```bash
curl -s -u admin:123456 \
  "http://localhost:9070/api/dashboards/uid/UID_DU_DASHBOARD" \
  | python3 -m json.tool > /tmp/crypto-macro-dashboard-export.json
```

Remplacer le JSON provisionné avec un export :

```bash
python3 - <<'PY'
import json

source = "/tmp/crypto-macro-dashboard-export.json"
target = "grafana/dashboards/crypto-macro-overview.json"

with open(source, "r", encoding="utf-8") as f:
    payload = json.load(f)

dashboard = payload["dashboard"]

dashboard["id"] = None
dashboard["uid"] = "crypto-macro-overview-sqlite-v2"
dashboard["title"] = "Crypto Macro Overview SQLite"
dashboard["version"] = 1

with open(target, "w", encoding="utf-8") as f:
    json.dump(dashboard, f, indent=2, ensure_ascii=False)

print(f"Dashboard exporté vers {target}")
PY
```

Vérifier le JSON :

```bash
python3 -m json.tool grafana/dashboards/crypto-macro-overview.json > /tmp/check-dashboard.json
```

Redémarrer Grafana :

```bash
docker compose restart grafana
```

***

## Option pratique future

Créer un script :

```text
scripts/export-grafana-dashboard.sh
```

Objectif :

```text
Automatiser l’export d’une copie Grafana vers grafana/dashboards/crypto-macro-overview.json
```

Le script pourrait faire automatiquement :

```text
export API
vérification grep
réécriture id / uid / title / version
validation JSON
```

Cela éviterait de refaire les commandes manuellement après chaque modification de dashboard.

***

## Contraintes techniques

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

Je souhaite une progression étape par étape.

Ne pas tout complexifier dès le début.

Il faut éviter :

```text
la sur-architecture prématurée
les schedulers complexes trop tôt
les bases externes tant que SQLite suffit
les automatisations de trading
```

***

## Style d’accompagnement souhaité

Je veux être accompagné en français.

Je souhaite une approche progressive :

```text
une étape à la fois
explications simples
commandes Docker/Bash claires
fichiers complets quand nécessaire
pas de sur-architecture prématurée
```

Quand tu proposes du code, donne-moi systématiquement :

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

***

## État actuel synthétique

Le projet dispose actuellement de :

```text
Grafana local opérationnel
Collector Python Dockerisé
Base SQLite locale
Table macro_series
Collecte FRED FEDFUNDS
Collecte CoinGecko BTC / ETH / SOL / HYPE
Datasource SQLite Grafana
Dashboard Grafana provisionné
Panels macro et crypto
Workflow Grafana documenté
Modèle timestamps created_at / updated_at propre
```

***

## Prochaine étape proposée

La prochaine étape logique est :

```text
Étape 10 — Préparer un premier score risk-on / risk-off simple
```

Objectif :

```text
Créer une première logique de score simple et pédagogique
Stocker le score dans SQLite
Afficher le score dans Grafana
Ne pas déclencher de trades
```

Première version possible du score :

```text
FEDFUNDS élevé ou en hausse        => prudence
BTC en baisse récente              => prudence
ETH / SOL / HYPE faibles           => prudence
Contexte crypto favorable          => score positif ou neutre
Contexte macro restrictif          => score négatif
```

Le score doit rester très simple au départ.

Interprétation possible :

```text
Score >= 0        => contexte respirable
Score entre -1/-3 => prudence
Score <= -4       => risk-off marqué
```

Ne pas chercher à faire un modèle parfait immédiatement.

L’objectif est d’obtenir un premier indicateur lisible dans Grafana.


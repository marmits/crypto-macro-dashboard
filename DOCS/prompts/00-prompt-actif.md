Voici un **prompt actif prêt à copier-coller** pour démarrer une nouvelle conversation dédiée au projet.


# Prompt actif — Projet `crypto-macro-dashboard`

Je souhaite démarrer un nouveau projet Docker appelé :

```text
crypto-macro-dashboard
```

## Objectif général

Créer un dashboard local accessible sur :

```text
http://localhost:9070
```

Le but est de suivre le contexte macroéconomique et crypto afin de mieux interpréter les signaux de mon bot Freqtrade / Hyperliquid.

Ce dashboard ne doit pas déclencher de trades automatiquement au départ.  
Il sert uniquement de **filtre de contexte risk-on / risk-off**.

***

## Stack souhaitée

Je veux construire progressivement un projet Docker avec :

```text
Grafana
+
petite collecte Python
+
FRED API
+
CoinGecko API
+
source marché complémentaire si nécessaire
```

Architecture souhaitée au départ :

```text
crypto-macro-dashboard/
├── docker-compose.yml
├── README.md
└── DOCS
    └── 00-prompt-actif.md
├── collector/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── config.py
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   └── dashboards/
│   └── dashboards/
└── data/
    └── macro.db
```

Je préfère commencer simple avec :

```text
SQLite
```

Puis éventuellement passer plus tard à :

```text
PostgreSQL
InfluxDB
Prometheus
```

si cela devient utile.

***

## Indicateurs à tracer

Je veux suivre au minimum :

```text
Fed
taux
force du dollar
rendements US
pétrole
inflation
marché risk-on / risk-off
```

Plus précisément, j’aimerais afficher progressivement mais pas du tout prioritaire (plus tard vraiment):

```text
Fed Funds Rate
US 2Y
US 10Y
US 30Y
Yield curve 10Y - 2Y
DXY ou équivalent dollar
WTI
Brent
CPI
Core CPI
PCE
Core PCE
VIX
S&P 500
Nasdaq
BTC
ETH
SOL
HYPE
```

***

## Sources de données souhaitées

### FRED API

Pour les données macro officielles :

```text
Fed Funds
rendements US
inflation
PCE
CPI
emploi éventuellement
M2 éventuellement
spreads éventuellement
```

### CoinGecko API

Pour les données crypto :

```text
BTC
ETH
SOL
HYPE
éventuellement total market cap ou autres actifs
```

### Source marché complémentaire

À discuter pour :

```text
DXY
S&P 500
Nasdaq
VIX
WTI
Brent
```

Je suis ouvert à des sources gratuites ou simples, mais je veux pas dépendre trop tôt d’API payantes.

***

## Dashboard Grafana souhaité

Je veux une première version très simple, puis enrichir ensuite.

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

Afficher une interprétation simple :

```text
Macro favorable
Macro neutre
Macro défavorable
Risk-on
Risk-off
Prudence sur les entrées Freqtrade
```

***

## Score risk-on / risk-off

Je souhaite créer progressivement un score simple.

Exemple :

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

Je veux que ce score reste simple, lisible et pédagogique au départ.

***

## Contraintes techniques

Je travaille principalement avec :

```text
Docker
Docker Compose
Linux / WSL2
Python
Grafana
Markdown
Git
```

Je souhaite une progression étape par étape.

Ne pas tout complexifier dès le début.

Priorité :

```text
1. faire tourner Grafana sur localhost:9070
2. créer le collector Python
3. stocker quelques données en SQLite
4. afficher une première métrique FRED
5. afficher une première métrique CoinGecko
6. construire un premier dashboard Grafana simple
7. enrichir progressivement
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

Quand tu proposes du code, donne-moi :

```text
le chemin du fichier
le contenu complet du fichier
la commande à exécuter
la commande de vérification
```

Pour les commits Git, les messages doivent être en français.

Exemple :

```bash
git commit -m "init: crée le squelette du dashboard macro crypto"
```

***




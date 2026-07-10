# Prompt actif — Projet `crypto-macro-dashboard`

## État actuel du projet

Le projet Docker `crypto-macro-dashboard` est initialisé.

Grafana fonctionne correctement en local sur :

```text
http://localhost:9070
````

Le conteneur Grafana démarre via Docker Compose et l’étape 1 est considérée comme validée.

Ce prompt actif sert maintenant à préparer l’étape suivante :

```text
Étape 2 — Ajouter un collector Python minimal avec SQLite
```

***

## Objectif général du projet

Créer un dashboard local permettant de suivre le contexte macroéconomique et crypto afin de mieux interpréter les signaux de mon bot Freqtrade / Hyperliquid.

Ce dashboard ne doit pas déclencher de trades automatiquement au départ.

Il sert uniquement de filtre de contexte :

```text
risk-on / risk-off
```

L’approche doit rester progressive, simple et pédagogique.

***

## Stack actuelle

La stack cible du projet est :

```text
Docker
Docker Compose
Grafana
Python
SQLite
FRED API
CoinGecko API
source marché complémentaire si nécessaire
```

Pour l’instant, seul Grafana est opérationnel.

SQLite sera ajouté à l’étape 2.

***

## Arborescence actuelle

L’arborescence actuelle du projet est :

```text
crypto-macro-dashboard/
├── collector
│   ├── config.py
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── data
├── docker-compose.yml
├── DOCS
│   ├── 00-prompt-actif.md
│   └── 01-prompt-actif.md
├── grafana
│   ├── dashboards
│   └── provisioning
│       ├── dashboards
│       └── datasources
└── README.md
```

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
TODO
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

Fichiers concernés :

```text
collector/Dockerfile
collector/requirements.txt
collector/config.py
collector/main.py
docker-compose.yml
data/macro.db
```

Contraintes :

```text
Rester simple
Pas encore d’appel API FRED
Pas encore d’appel API CoinGecko
Pas encore de dashboard Grafana complexe
Juste prouver que le collector Python écrit correctement en SQLite
```

***

### Étape 3 — Première métrique FRED

Statut :

```text
LATER
```

Objectif futur :

```text
Brancher l’API FRED
Récupérer une première métrique macro
Commencer probablement par FEDFUNDS
Stocker les observations dans SQLite
```

Métrique pressentie :

```text
FEDFUNDS
```

***

### Étape 4 — Première métrique CoinGecko

Statut :

```text
LATER
```

Objectif futur :

```text
Brancher CoinGecko
Récupérer le prix BTC
Stocker les observations dans SQLite
```

Métrique pressentie :

```text
BTC / USD
```

***

### Étape 5 — Source de données Grafana SQLite

Statut :

```text
LATER
```

Objectif futur :

```text
Configurer Grafana pour lire la base SQLite via le plugin SQLite
Créer une datasource provisionnée
Vérifier que Grafana peut interroger data/macro.db
```

***

### Étape 6 — Premier dashboard Grafana simple

Statut :

```text
LATER
```

Objectif futur :

```text
Créer un dashboard Grafana minimal
Afficher une première série temporelle depuis SQLite
Commencer avec une donnée de test ou FEDFUNDS
```

***

### Étape 7 — Score risk-on / risk-off simple

Statut :

```text
LATER
```

Objectif futur :

```text
Créer un score macro simple et lisible
Stocker ce score en SQLite
L’afficher dans Grafana
```

***

## Étape 2 demandée maintenant

Je souhaite maintenant réaliser uniquement l’étape 2 :

```text
Collector Python minimal + SQLite
```

L’objectif est de créer un conteneur collector capable de :

1. démarrer via Docker Compose ;
2. créer automatiquement une base SQLite dans :

```text
/data/macro.db
```

3. créer une table simple :

```text
macro_series
```

4. insérer une première donnée de test ;
5. afficher des logs simples pour confirmer le bon fonctionnement ;
6. terminer proprement ou rester simple selon ce qui est préférable au départ.

***

## Schéma SQLite souhaité pour démarrer

Créer une table simple nommée :

```text
macro_series
```

Structure souhaitée :

```text
id
source
symbol
name
value
unit
observed_at
created_at
```

Exemple de première donnée de test :

```text
source      = test
symbol      = TEST_MACRO_SCORE
name        = Score macro de test
value       = 0
unit        = score
observed_at = date/heure actuelle
created_at  = date/heure actuelle
```

Ce schéma pourra évoluer plus tard si nécessaire.

***

## Comportement attendu du collector

Pour l’étape 2, le collector doit rester très simple.

Il doit :

```text
ouvrir ou créer la base SQLite
créer la table macro_series si elle n’existe pas
insérer une donnée de test
afficher les lignes existantes dans les logs
se terminer sans erreur
```

Il n’est pas nécessaire pour l’instant de faire une boucle infinie ou un scheduler.

La collecte périodique pourra venir plus tard.

***

## docker-compose.yml attendu après l’étape 2

Le fichier `docker-compose.yml` doit conserver le service Grafana existant.

Il faut ajouter un service :

```text
collector
```

Le service collector doit :

```text
être construit depuis ./collector
monter le dossier ./data dans /data
dépendre éventuellement de grafana uniquement si utile
pouvoir être lancé avec docker compose up collector
```

L’objectif prioritaire est que ce service génère :

```text
data/macro.db
```

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

Priorité actuelle :

```text
1. Garder Grafana fonctionnel sur localhost:9070
2. Ajouter un collector Python minimal
3. Créer une base SQLite
4. Insérer une première donnée de test
5. Vérifier la présence de data/macro.db
6. Vérifier le contenu de la table macro_series
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

Pour les commits Git, les messages doivent être en français.

Exemple :

```bash
git commit -m "feat: ajoute le collecteur sqlite initial"
```

***

## Ce que je veux maintenant

Je veux que tu me guides pour réaliser l’étape 2.

Merci de me fournir :

```text
1. Le contenu complet de collector/Dockerfile
2. Le contenu complet de collector/requirements.txt
3. Le contenu complet de collector/config.py
4. Le contenu complet de collector/main.py
5. La modification complète de docker-compose.yml
6. Les commandes Docker à exécuter
7. Les commandes de vérification SQLite
8. Le commit Git conseillé en français
```

Ne pas encore brancher FRED.

Ne pas encore brancher CoinGecko.

Ne pas encore faire de dashboard Grafana avancé.

Objectif unique :

```text
un collector Python Dockerisé qui écrit une première donnée de test dans SQLite
```

````

---

## Mon avis sur ta question : “01 ou toutes les étapes ?”

Je te recommande cette logique :

```text
00-prompt-actif.md = mémoire initiale complète du besoin
01-prompt-actif.md = état courant après Grafana OK, préparation étape 2
02-prompt-actif.md = état courant après collector SQLite OK
03-prompt-actif.md = état courant après première métrique FRED
04-prompt-actif.md = état courant après première métrique CoinGecko
````

Donc : **oui, on garde toutes les étapes dans le prompt**, mais avec un **statut clair**.

Exemple :

```text
DONE
IN_PROGRESS
TODO
LATER
BLOCKED
```

Ça permettra de copier-coller le dernier prompt actif dans une nouvelle conversation et de reprendre exactement au bon endroit.

***

## Commande utile pour créer/modifier `01-prompt-actif.md`

Si tu veux l’éditer rapidement :

```bash
nano DOCS/01-prompt-actif.md
```

ou avec VS Code :

```bash
code DOCS/01-prompt-actif.md
```

***

## Commit conseillé

Après mise à jour du prompt actif :

```bash
git add DOCS/01-prompt-actif.md
git commit -m "docs: prépare le prompt actif pour le collecteur sqlite"
```

***

Quand tu veux, on peut enchaîner sur **l’étape 2 réelle** avec les fichiers complets du collector Docker + SQLite.

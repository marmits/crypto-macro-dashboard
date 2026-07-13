# Indicator Framework v1

## Objectif

Définir la structure des indicateurs utilisés par le Market Intelligence Engine.

Le framework garantit :

- une nomenclature cohérente ;
- une architecture extensible ;
- une séparation entre collecte et calcul ;
- une intégration simple avec Grafana ;
- une utilisation future dans Captain Cryptos.

---

# Cycle de vie

API externe
        │
        ▼
Collector
        │
        ▼
SQLite
        │
        ▼
Derived Metrics
        │
        ▼
SQLite
        │
        ▼
Grafana
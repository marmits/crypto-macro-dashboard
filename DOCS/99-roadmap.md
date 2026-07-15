# Roadmap

## Sprint 1 - Foundation ✅

### Infrastructure

- [x] Docker
- [x] Docker Compose
- [x] Grafana
- [x] SQLite

### Collecteurs

- [x] FRED
- [x] CoinGecko

### Base de donnees

- [x] Table `macro_series`
- [x] Index
- [x] Upsert

### Derived Metrics

- [x] `BTC_MCAP`
- [x] `ETH_MCAP`
- [x] `TOTAL3`

### Dashboard Macro

- [x] Macro Score
- [x] Main
- [x] Dollar
- [x] Inflation
- [x] Energy
- [x] Market
- [x] Cryptos
- [x] Datas

### Validation

- [x] SQL
- [x] Grafana
- [x] Documentation

## Sprint 2 - Crypto Market Regime V1 ✅

### Fonctionnalites implementees

- [x] 2.1 Creation de la section Crypto Market Regime
- [x] 2.2 BTC Dominance
- [x] 2.3 Stablecoin Dominance
- [x] 2.4 ETH/BTC
- [x] 2.5 TOTAL3
- [x] 2.6 Global Volume
- [ ] 2.7 BTC Trend
- [x] 2.8 Crypto Score
- [ ] 2.9 Crypto Weather
- [x] 2.10 Documentation V1

### Fiabilisation de la V1

- [x] Regroupement des prix CoinGecko dans une seule requete
- [x] Collecte des metriques globales CoinGecko
- [x] Comparaison avec le snapshot strictement precedent
- [x] Persistance des valeurs `PREVIOUS` et `CURRENT`
- [x] Calcul du score uniquement lorsque les quatre signaux sont disponibles
- [x] Selection Grafana de la derniere observation par `observed_at`, puis `id`
- [x] Filtrage explicite des sources dans les panneaux crypto
- [x] Gestion explicite des donnees absentes dans `Score Explanation`
- [ ] Tests automatises Python du contrat temporel
- [ ] Validation historique et calibration des signaux

> La V1 fonctionnelle est livree. Les elements 2.7 et 2.9 constituent des
> extensions futures et ne remettent pas en cause la fin du perimetre V1.

## Sprint 3 - Exploitation et extensions

### Captain Cryptos

- [ ] Definition du perimetre
- [ ] Integration sans rupture du contrat SQLite

### Alertes et rapports

- [ ] Alertes intelligentes
- [ ] Alertes Discord
- [ ] Rapports quotidiens automatiques

### Analyse avancee

- [ ] Crypto Regime Radar
- [ ] Backtesting des regimes
- [ ] Calibration historique des seuils
- [ ] Etude de la migration du score macro SQL vers Python

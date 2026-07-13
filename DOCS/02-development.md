# Développement

## Base de données SQLite

Afficher les dernières observations CoinGecko :

```bash
docker compose exec sqlite sqlite3 -header -column /data/macro.db "
SELECT
    symbol,
    value,
    observed_at
FROM macro_series
WHERE source='coingecko'
ORDER BY observed_at DESC;
"
```

---

Afficher les derniers enregistrements :

```bash
docker compose exec sqlite sqlite3 -header -column /data/macro.db "
SELECT *
FROM macro_series
ORDER BY id DESC
LIMIT 20;
"
```

---

Lister les symboles disponibles :

```bash
docker compose exec sqlite sqlite3 -header -column /data/macro.db "
SELECT DISTINCT symbol
FROM macro_series
ORDER BY symbol;
"
```

---

Afficher uniquement Bitcoin Dominance :

```bash
docker compose exec sqlite sqlite3 -header -column /data/macro.db "
SELECT
    observed_at,
    value
FROM macro_series
WHERE symbol='BTC_DOM'
ORDER BY observed_at;
"
```

---

Compter les observations par symbole :

```bash
docker compose exec sqlite sqlite3 -header -column /data/macro.db "
SELECT
    symbol,
    COUNT(*) AS observations
FROM macro_series
GROUP BY symbol
ORDER BY symbol;
"
```
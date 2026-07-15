# Copilot a trouvé ces points à corriger

## 5.1 Problème temporel potentiellement bloquant (fait)
## 5.2 Sélection par MAX(id) dans Score Explanation
Dans la requête du panneau `Score Explanation`, remplacer:

```sql
WITH latest AS (
    SELECT
        symbol,
        value
    FROM macro_series
    WHERE id IN (
        SELECT MAX(id)
        FROM macro_series
        GROUP BY symbol
    )
)
```

par 
```sql
WITH ranked AS (
    SELECT
        symbol,
        value,
        observed_at,
        id,
        ROW_NUMBER() OVER (
            PARTITION BY symbol
            ORDER BY observed_at DESC, id DESC
        ) AS row_number
    FROM macro_series
),
latest AS (
    SELECT
        symbol,
        value
    FROM ranked
    WHERE row_number = 1
)
```

## 5.3 Source non filtrée dans plusieurs panneaux crypto
> voir [diff_5.3.txt](diff_5.3.txt)

## 5.4 Gestion SQL des valeurs absentes
> voir [diff_5.4.txt](diff_5.4.txt)
 
## 5.5 Synchronisation contradictoire de la roadmap
> voir [diff_5.5.txt](diff_5.5.txt)

## 5.6 Commandes de diagnostic à mieux formater
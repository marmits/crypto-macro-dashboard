import os

DB_PATH = os.getenv("DB_PATH", "/data/macro.db")

FRED_API_KEY = os.getenv("FRED_API_KEY")
FRED_BASE_URL = os.getenv("FRED_BASE_URL", "https://api.stlouisfed.org/fred")

COINGECKO_BASE_URL = os.getenv(
    "COINGECKO_BASE_URL",
    "https://api.coingecko.com/api/v3",
)

# Optionnel pour plus tard.
# Pour l'instant, on peut utiliser l'API publique sans clé.
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

FRED_SERIES = {
    "FEDFUNDS": {
        "source": "fred",
        "symbol": "FEDFUNDS",
        "name": "Federal Funds Effective Rate",
        "unit": "percent",
    }
}

COINGECKO_COINS = {
    "bitcoin": {
        "source": "coingecko",
        "symbol": "BTC",
        "name": "Bitcoin",
        "unit": "usd",
    }
}
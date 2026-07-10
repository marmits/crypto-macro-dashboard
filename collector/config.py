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
        "limit": 120,
    },
    "DGS2": {
        "source": "fred",
        "symbol": "US2Y",
        "name": "US 2Y Treasury Yield",
        "unit": "percent",
        "limit": 1500,
    },
    "DGS10": {
        "source": "fred",
        "symbol": "US10Y",
        "name": "US 10Y Treasury Yield",
        "unit": "percent",
        "limit": 1500,
    },
    "DGS30": {
        "source": "fred",
        "symbol": "US30Y",
        "name": "US 30Y Treasury Yield",
        "unit": "percent",
        "limit": 1500,
    },
    "CPIAUCSL": {
        "source": "fred",
        "symbol": "CPI",
        "name": "Consumer Price Index",
        "unit": "index",
        "limit": 240,
    },
    "CPILFESL": {
        "source": "fred",
        "symbol": "CORE_CPI",
        "name": "Core Consumer Price Index",
        "unit": "index",
        "limit": 240,
    },
    "PCEPI": {
        "source": "fred",
        "symbol": "PCE",
        "name": "Personal Consumption Expenditures Price Index",
        "unit": "index",
        "limit": 240,
    },
    "PCEPILFE": {
        "source": "fred",
        "symbol": "CORE_PCE",
        "name": "Core Personal Consumption Expenditures Price Index",
        "unit": "index",
        "limit": 240,
    },
    "DCOILWTICO": {
            "source": "fred",
            "symbol": "WTI",
            "name": "Crude Oil Price WTI",
            "unit": "usd_per_barrel",
            "limit": 1500,
    },
    "DCOILBRENTEU": {
        "source": "fred",
        "symbol": "BRENT",
        "name": "Crude Oil Price Brent",
        "unit": "usd_per_barrel",
        "limit": 1500,
    },
}

COINGECKO_COINS = {
    "bitcoin": {
        "source": "coingecko",
        "symbol": "BTC",
        "name": "Bitcoin",
        "unit": "usd",
    },
    "ethereum": {
        "source": "coingecko",
        "symbol": "ETH",
        "name": "Ethereum",
        "unit": "usd",
    },
    "solana": {
        "source": "coingecko",
        "symbol": "SOL",
        "name": "Solana",
        "unit": "usd",
    },
    "hyperliquid": {
        "source": "coingecko",
        "symbol": "HYPE",
        "name": "Hyperliquid",
        "unit": "usd",
    },
}
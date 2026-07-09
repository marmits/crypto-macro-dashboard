import os

DB_PATH = os.getenv("DB_PATH", "/data/macro.db")

FRED_API_KEY = os.getenv("FRED_API_KEY")
FRED_BASE_URL = os.getenv("FRED_BASE_URL", "https://api.stlouisfed.org/fred")

FRED_SERIES = {
    "FEDFUNDS": {
        "source": "fred",
        "symbol": "FEDFUNDS",
        "name": "Federal Funds Effective Rate",
        "unit": "percent",
    }
}

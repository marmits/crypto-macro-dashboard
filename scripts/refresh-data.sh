#!/usr/bin/env bash

set -Eeuo pipefail

# PATH explicite pour une future execution depuis cron.
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH:-}"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
LOCK_FILE="${TMPDIR:-/tmp}/crypto-macro-dashboard-refresh.lock"

log() {
    printf '[%s] %s\n' "$(date --iso-8601=seconds)" "$*"
}

fail() {
    log "ERREUR: $*" >&2
    exit 1
}

on_error() {
    local exit_code=$?
    log "ERREUR: le rafraichissement a echoue (code ${exit_code})." >&2
    exit "${exit_code}"
}

trap on_error ERR

usage() {
    cat <<'EOF'
Usage:
  ./scripts/refresh-data.sh [OPTIONS]

Rafraichit les donnees FRED et CoinGecko, calcule les metriques
derivees, puis controle les series SQLite attendues par Grafana.

Options:
  -h, --help       Afficher cette aide et quitter
  --strict         Rendre bloquante l'absence de series du regime crypto
  --skip-build     Ne pas reconstruire l'image Docker du collector

Variables d'environnement:
  STRICT_DATA_CONTRACT=1
      Equivalent de --strict.

  SKIP_COLLECTOR_BUILD=1
      Equivalent de --skip-build.

Exemples:
  ./scripts/refresh-data.sh
  ./scripts/refresh-data.sh --skip-build
  ./scripts/refresh-data.sh --strict --skip-build

Codes de sortie:
  0   Collecte reussie, ou regime incomplet en mode non strict
  1   Erreur Docker, Compose, collector ou execution generale
  2   Contrat de donnees de base incomplet
  3   Contrat du regime crypto incomplet en mode strict
  64  Option de ligne de commande inconnue
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        --strict)
            export STRICT_DATA_CONTRACT=1
            shift
            ;;
        --skip-build)
            export SKIP_COLLECTOR_BUILD=1
            shift
            ;;
        --)
            shift
            break
            ;;
        *)
            printf 'Option inconnue : %s\n\n' "$1" >&2
            usage >&2
            exit 64
            ;;
    esac
done

if [[ $# -gt 0 ]]; then
    printf 'Argument inattendu : %s\n\n' "$1" >&2
    usage >&2
    exit 64
fi

command -v docker >/dev/null 2>&1 \
    || fail "Docker est introuvable dans le PATH."

command -v flock >/dev/null 2>&1 \
    || fail "La commande flock est introuvable. Installe le paquet util-linux."

[[ -f "${PROJECT_DIR}/docker-compose.yml" ]] \
    || fail "Fichier docker-compose.yml introuvable dans ${PROJECT_DIR}."

[[ -f "${PROJECT_DIR}/.env" ]] \
    || fail "Fichier .env introuvable dans ${PROJECT_DIR}."

exec 9>"${LOCK_FILE}"
flock -n 9 \
    || fail "Une collecte est deja en cours."

cd "${PROJECT_DIR}"

log "Debut du rafraichissement des donnees."
log "Projet: ${PROJECT_DIR}"

# Verifie la syntaxe et la resolution de la configuration Compose.
docker compose config --quiet

# Verifie que le moteur Docker est accessible.
docker info >/dev/null

# Reconstruit le collector pour integrer le code local le plus recent.
# Le cache Docker limite le cout lorsque les sources n'ont pas change.
if [[ "${SKIP_COLLECTOR_BUILD:-0}" == "1" ]]; then
    log "Reconstruction du collector ignoree (SKIP_COLLECTOR_BUILD=1)."
else
    log "Mise a jour de l'image du collector depuis le code local."
    docker compose build collector
fi

# Identifie le mode CoinGecko sans afficher de secret.
# L'absence de cle est valide et active la Keyless Public API.
docker compose run --rm --no-deps --entrypoint python collector - <<'PY'
import os

if os.getenv("COINGECKO_API_KEY"):
    print("Mode CoinGecko : Demo API authentifiee.")
else:
    print("Mode CoinGecko : Keyless Public API.")
    print(
        "Information : les limites keyless sont partagees par adresse IP ; "
        "un HTTP 429 peut survenir derriere un proxy ou un NAT d'entreprise."
    )
PY

log "Lancement du collector FRED, CoinGecko et des calculs derives."
docker compose run --rm --no-deps collector

log "Collecte terminee. Verification du contrat de donnees et de la fraicheur des series."

docker compose run --rm --no-deps --entrypoint python collector - <<'PY'
import sqlite3

DB_PATH = "/data/macro.db"

# Series indispensables apres une collecte reussie.
REQUIRED_SERIES = {
    "fred": {
        "FEDFUNDS", "US2Y", "US10Y", "US30Y", "CPI", "CORE_CPI",
        "PCE", "CORE_PCE", "WTI", "BRENT", "USD_BROAD", "VIX",
        "SP500", "NASDAQ",
    },
    "coingecko": {
        "BTC", "ETH", "SOL", "HYPE", "BTC_DOM", "ETH_DOM",
        "TOTAL_MCAP", "TOTAL_VOLUME", "ACTIVE_COINS", "ACTIVE_MARKETS",
        "STABLECOIN_MCAP",
    },
    "derived": {
        "BTC_MCAP", "ETH_MCAP", "STABLECOIN_DOM", "ETH_BTC", "TOTAL3",
    },
}

# Ces series necessitent un snapshot precedent coherent. Elles peuvent manquer
# au premier passage apres l'activation du regime crypto. Leur absence est un
# avertissement par defaut et devient bloquante avec STRICT_DATA_CONTRACT=1.
REGIME_SERIES = {
    "derived": {
        "BTC_DOM_SIGNAL", "STABLECOIN_SIGNAL", "ETH_BTC_SIGNAL",
        "TOTAL3_SIGNAL", "MARKET_REGIME_SCORE", "MARKET_REGIME_STATE",
        "BTC_DOM_PREVIOUS", "BTC_DOM_CURRENT",
        "STABLECOIN_DOM_PREVIOUS", "STABLECOIN_DOM_CURRENT",
        "ETH_BTC_PREVIOUS", "ETH_BTC_CURRENT",
        "TOTAL3_PREVIOUS", "TOTAL3_CURRENT",
    },
}

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

try:
    rows = conn.execute(
        """
        SELECT
            source,
            symbol,
            COUNT(*) AS total_rows,
            MAX(observed_at) AS last_observed_at,
            MAX(updated_at) AS last_updated_at
        FROM macro_series
        GROUP BY source, symbol
        ORDER BY source, symbol
        """
    ).fetchall()

    if not rows:
        raise SystemExit("Aucune serie trouvee dans macro_series.")

    print()
    print("Resume des series")
    print("-" * 118)
    print(
        f"{'SOURCE':<12} "
        f"{'SYMBOLE':<28} "
        f"{'LIGNES':>8} "
        f"{'DERNIERE OBSERVATION':<30} "
        f"{'DERNIERE MISE A JOUR':<30}"
    )
    print("-" * 118)

    for row in rows:
        print(
            f"{row['source']:<12} "
            f"{row['symbol']:<28} "
            f"{row['total_rows']:>8} "
            f"{str(row['last_observed_at'] or '-'):30.30} "
            f"{str(row['last_updated_at'] or '-'):30.30}"
        )

    print("-" * 118)
    print(f"{len(rows)} serie(s) verifiee(s).")

    available = {(row["source"], row["symbol"]) for row in rows}
    missing = [
        (source, symbol)
        for source, symbols in REQUIRED_SERIES.items()
        for symbol in sorted(symbols)
        if (source, symbol) not in available
    ]

    if missing:
        print()
        print("ERREUR: contrat de donnees de base incomplet. Series absentes :")
        for source, symbol in missing:
            print(f"  - {source}/{symbol}")
        raise SystemExit(2)

    regime_missing = [
        (source, symbol)
        for source, symbols in REGIME_SERIES.items()
        for symbol in sorted(symbols)
        if (source, symbol) not in available
    ]

    print()
    print("Contrat de donnees de base valide.")

    if regime_missing:
        print()
        print("AVERTISSEMENT: regime crypto incomplet. Series absentes :")
        for source, symbol in regime_missing:
            print(f"  - {source}/{symbol}")
        print(
            "Un premier snapshot peut seulement initialiser les metriques. "
            "Relance la collecte plus tard pour produire une comparaison."
        )
        print(
            "Si ces series restent absentes apres plusieurs snapshots, "
            "verifie la selection des valeurs precedentes dans derived.py."
        )

        import os
        if os.getenv("STRICT_DATA_CONTRACT") == "1":
            raise SystemExit(3)
    else:
        print("Contrat du regime crypto valide.")
finally:
    conn.close()
PY

log "Rafraichissement termine avec succes."
log "Grafana relira automatiquement data/macro.db; aucun redemarrage n'est necessaire."

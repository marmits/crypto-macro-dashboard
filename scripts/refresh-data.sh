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

log "Lancement du collector FRED et CoinGecko."
docker compose run --rm collector

log "Collecte terminee. Verification de la fraicheur des series."

docker compose run --rm --entrypoint python collector - <<'PY'
import sqlite3

DB_PATH = "/data/macro.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

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
print("-" * 108)
print(
    f"{'SOURCE':<12} "
    f"{'SYMBOLE':<14} "
    f"{'LIGNES':>8} "
    f"{'DERNIERE OBSERVATION':<30} "
    f"{'DERNIERE MISE A JOUR':<30}"
)
print("-" * 108)

for row in rows:
    print(
        f"{row['source']:<12} "
        f"{row['symbol']:<14} "
        f"{row['total_rows']:>8} "
        f"{str(row['last_observed_at'] or '-'):30.30} "
        f"{str(row['last_updated_at'] or '-'):30.30}"
    )

print("-" * 108)
print(f"{len(rows)} serie(s) verifiee(s).")

conn.close()
PY

log "Rafraichissement termine avec succes."
log "Grafana relira automatiquement data/macro.db; aucun redemarrage n'est necessaire."

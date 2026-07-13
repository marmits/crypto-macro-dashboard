#!/usr/bin/env bash

set -Eeuo pipefail

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH:-}"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
DASHBOARD_FILE="${PROJECT_DIR}/grafana/dashboards/crypto-macro-overview.json"
DASHBOARD_UID="crypto-macro-overview-sqlite-v2"
DASHBOARD_TITLE="Crypto Macro Overview SQLite"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:9070}"
GRAFANA_USER="${GRAFANA_USER:-admin}"
GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-123456}"
LOCK_FILE="${TMPDIR:-/tmp}/crypto-macro-dashboard-publish.lock"
WORK_DIR=""
SELECTED_UID=""
SELECTED_TITLE=""
AUTO_DELETE=false
ASSUME_YES=false

log() {
    printf '[%s] %s\n' "$(date --iso-8601=seconds)" "$*"
}

fail() {
    log "ERREUR: $*" >&2
    exit 1
}

cleanup() {
    if [[ -n "${WORK_DIR}" && -d "${WORK_DIR}" ]]; then
        rm -rf -- "${WORK_DIR}"
    fi
}

on_error() {
    local exit_code=$?
    log "ERREUR: publication interrompue (code ${exit_code})." >&2
    exit "${exit_code}"
}

trap cleanup EXIT
trap on_error ERR

usage() {
    cat <<'EOF'
Usage:
  ./scripts/publish-grafana-copy.sh
  ./scripts/publish-grafana-copy.sh --uid UID_DE_LA_COPIE
  ./scripts/publish-grafana-copy.sh --uid UID_DE_LA_COPIE --delete-copy
  ./scripts/publish-grafana-copy.sh --uid UID_DE_LA_COPIE --delete-copy --yes

Options:
  --uid UID       Selectionne directement une copie Grafana.
  --delete-copy   Propose la suppression de la copie apres validation complete.
  --yes           Confirme automatiquement les questions de publication/suppression.
  --help          Affiche cette aide.

Variables d'environnement:
  GRAFANA_URL       Par defaut: http://localhost:9070
  GRAFANA_USER      Par defaut: admin
  GRAFANA_PASSWORD  Par defaut: 123456
EOF
}

while (($# > 0)); do
    case "$1" in
        --uid)
            (($# >= 2)) || fail "L'option --uid attend une valeur."
            SELECTED_UID="$2"
            shift 2
            ;;
        --delete-copy)
            AUTO_DELETE=true
            shift
            ;;
        --yes)
            ASSUME_YES=true
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            fail "Option inconnue: $1"
            ;;
    esac
done

for command in docker curl python3 flock; do
    command -v "${command}" >/dev/null 2>&1 \
        || fail "Commande introuvable: ${command}"
done

[[ -f "${PROJECT_DIR}/docker-compose.yml" ]] \
    || fail "docker-compose.yml introuvable dans ${PROJECT_DIR}."

[[ -f "${DASHBOARD_FILE}" ]] \
    || fail "Dashboard provisionne introuvable: ${DASHBOARD_FILE}."

exec 9>"${LOCK_FILE}"
flock -n 9 || fail "Une publication Grafana est deja en cours."

WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/crypto-macro-publish.XXXXXX")"
SEARCH_JSON="${WORK_DIR}/search.json"
EXPORT_JSON="${WORK_DIR}/copy-export.json"
CANDIDATE_JSON="${WORK_DIR}/candidate.json"
OFFICIAL_API_JSON="${WORK_DIR}/official-api.json"
OFFICIAL_JSON="${WORK_DIR}/official.json"
BACKUP_FILE="${WORK_DIR}/crypto-macro-overview.before.json"

cd "${PROJECT_DIR}"

api_get() {
    local path="$1"
    local output="$2"
    local status

    status="$(curl --silent --show-error \
        --user "${GRAFANA_USER}:${GRAFANA_PASSWORD}" \
        --output "${output}" \
        --write-out '%{http_code}' \
        "${GRAFANA_URL}${path}")"

    [[ "${status}" == "200" ]] \
        || fail "GET ${path} a retourne HTTP ${status}."
}

confirm() {
    local prompt="$1"
    local answer

    if [[ "${ASSUME_YES}" == true ]]; then
        return 0
    fi

    read -r -p "${prompt} [o/N] " answer
    [[ "${answer}" =~ ^[oOyY]$ ]]
}

log "Verification de Grafana: ${GRAFANA_URL}"
api_get "/api/health" "${WORK_DIR}/health.json"

log "Recherche des copies du dashboard."
api_get "/api/search?type=dash-db" "${SEARCH_JSON}"

mapfile -t COPY_LINES < <(
    python3 - "${SEARCH_JSON}" "${DASHBOARD_UID}" <<'PY'
import json
import sys

path, official_uid = sys.argv[1:]
with open(path, encoding="utf-8") as file:
    dashboards = json.load(file)

copies = []
for item in dashboards:
    if item.get("type") != "dash-db":
        continue
    uid = item.get("uid")
    title = item.get("title", "")
    if uid == official_uid:
        continue
    if "crypto macro overview sqlite" not in title.lower():
        continue
    copies.append((title.lower(), uid, title))

for _, uid, title in sorted(copies):
    print(f"{uid}\t{title}")
PY
)

((${#COPY_LINES[@]} > 0)) \
    || fail "Aucune copie du dashboard Crypto Macro Overview SQLite n'a ete trouvee."

if [[ -z "${SELECTED_UID}" ]]; then
    if ((${#COPY_LINES[@]} == 1)); then
        IFS=$'\t' read -r SELECTED_UID SELECTED_TITLE <<<"${COPY_LINES[0]}"
        log "Une seule copie trouvee: ${SELECTED_TITLE} (${SELECTED_UID})."
    else
        printf '\nCopies disponibles:\n'
        for index in "${!COPY_LINES[@]}"; do
            IFS=$'\t' read -r uid title <<<"${COPY_LINES[$index]}"
            printf '  %d) %s [%s]\n' "$((index + 1))" "${title}" "${uid}"
        done
        printf '\n'

        while true; do
            read -r -p "Numero de la copie a publier: " choice
            if [[ "${choice}" =~ ^[0-9]+$ ]] \
                && ((choice >= 1 && choice <= ${#COPY_LINES[@]})); then
                IFS=$'\t' read -r SELECTED_UID SELECTED_TITLE \
                    <<<"${COPY_LINES[$((choice - 1))]}"
                break
            fi
            printf 'Choix invalide.\n' >&2
        done
    fi
else
    match_found=false
    for line in "${COPY_LINES[@]}"; do
        IFS=$'\t' read -r uid title <<<"${line}"
        if [[ "${uid}" == "${SELECTED_UID}" ]]; then
            SELECTED_TITLE="${title}"
            match_found=true
            break
        fi
    done
    [[ "${match_found}" == true ]] \
        || fail "L'UID ${SELECTED_UID} ne correspond a aucune copie eligible."
fi

log "Copie selectionnee: ${SELECTED_TITLE} (${SELECTED_UID})."

confirm "Publier cette copie vers le dashboard officiel ?" \
    || fail "Publication annulee par l'utilisateur."

log "Export de la copie."
api_get "/api/dashboards/uid/${SELECTED_UID}" "${EXPORT_JSON}"

log "Preparation du JSON provisionne."
python3 - "${EXPORT_JSON}" "${CANDIDATE_JSON}" <<'PY'
import json
import sys

source, target = sys.argv[1:]
with open(source, encoding="utf-8") as file:
    payload = json.load(file)

dashboard = payload.get("dashboard")
if not isinstance(dashboard, dict):
    raise SystemExit("L'export Grafana ne contient pas d'objet dashboard valide.")

panels = dashboard.get("panels")
if not isinstance(panels, list) or not panels:
    raise SystemExit("Le dashboard exporte ne contient aucun panel.")

dashboard["id"] = None
dashboard["uid"] = "crypto-macro-overview-sqlite-v2"
dashboard["title"] = "Crypto Macro Overview SQLite"
dashboard["version"] = 1

with open(target, "w", encoding="utf-8") as file:
    json.dump(dashboard, file, ensure_ascii=False, indent=2)
    file.write("\n")
PY

log "Validation structurelle du candidat."
python3 -m json.tool "${CANDIDATE_JSON}" >/dev/null

python3 - "${CANDIDATE_JSON}" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as file:
    dashboard = json.load(file)

if dashboard.get("uid") != "crypto-macro-overview-sqlite-v2":
    raise SystemExit("UID officiel incorrect.")
if dashboard.get("title") != "Crypto Macro Overview SQLite":
    raise SystemExit("Titre officiel incorrect.")

ids = []
titles = []
target_errors = []

def walk(panels):
    for panel in panels:
        panel_id = panel.get("id")
        if panel_id is not None:
            ids.append(panel_id)
        titles.append(panel.get("title"))
        for target in panel.get("targets", []):
            if target.get("datasource", {}).get("uid") == "macro-sqlite":
                for key in ("queryText", "rawQueryText", "timeColumns"):
                    if key not in target:
                        target_errors.append(
                            f"panel={panel.get('title')!r}, target={target.get('refId')}, cle={key}"
                        )
        walk(panel.get("panels", []))

walk(dashboard.get("panels", []))

if len(ids) != len(set(ids)):
    raise SystemExit("Des identifiants de panels sont dupliques.")
if target_errors:
    raise SystemExit("Targets SQLite incompletes:\n" + "\n".join(target_errors))

import unicodedata


def normalize_title(value):
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " ".join(value.casefold().split())


required_titles = {
    normalize_title("Macro Score"): "Macro Score",
    normalize_title("Score macro risk-on/off"): "Score macro risk-on/off",
    normalize_title("Détails du score macro"): "Détails du score macro",
}
normalized_titles = {normalize_title(title) for title in titles if title}
missing = [
    display_name
    for normalized_name, display_name in required_titles.items()
    if normalized_name not in normalized_titles
]

if missing:
    print("Titres trouves dans la copie:", file=sys.stderr)
    for title in titles:
        if title:
            print(f"  - {title}", file=sys.stderr)
    raise SystemExit(
        "Elements obligatoires absents: " + ", ".join(sorted(missing))
    )

print(f"Validation OK: {len(ids)} panels, {len(titles)} titres inspectes.")
PY

cp -- "${DASHBOARD_FILE}" "${BACKUP_FILE}"
cp -- "${CANDIDATE_JSON}" "${DASHBOARD_FILE}"

log "Validation du fichier final."
python3 -m json.tool "${DASHBOARD_FILE}" >/dev/null

git diff --check -- "${DASHBOARD_FILE}"

git_diff_stat="$(git diff --stat -- "${DASHBOARD_FILE}" || true)"
printf '\nModification preparee:\n%s\n\n' "${git_diff_stat:-Aucune difference Git detectee.}"

log "Redemarrage de Grafana."
docker compose restart grafana

log "Attente de la disponibilite de Grafana."
ready=false
for attempt in {1..30}; do
    if curl --silent --fail \
        --user "${GRAFANA_USER}:${GRAFANA_PASSWORD}" \
        "${GRAFANA_URL}/api/health" >/dev/null; then
        ready=true
        break
    fi
    sleep 2
done

if [[ "${ready}" != true ]]; then
    cp -- "${BACKUP_FILE}" "${DASHBOARD_FILE}"
    docker compose restart grafana >/dev/null 2>&1 || true
    fail "Grafana n'est pas redevenu disponible; le JSON precedent a ete restaure."
fi

log "Verification du dashboard officiel via l'API."
api_get "/api/dashboards/uid/${DASHBOARD_UID}" "${OFFICIAL_API_JSON}"

python3 - "${OFFICIAL_API_JSON}" "${OFFICIAL_JSON}" <<'PY'
import json
import sys

source, target = sys.argv[1:]
with open(source, encoding="utf-8") as file:
    payload = json.load(file)

dashboard = payload.get("dashboard")
if not isinstance(dashboard, dict):
    raise SystemExit("Reponse officielle invalide.")

with open(target, "w", encoding="utf-8") as file:
    json.dump(dashboard, file, ensure_ascii=False, indent=2)
    file.write("\n")
PY

if ! python3 - "${DASHBOARD_FILE}" "${OFFICIAL_JSON}" <<'PY'
import json
import sys

expected_path, actual_path = sys.argv[1:]
with open(expected_path, encoding="utf-8") as file:
    expected = json.load(file)
with open(actual_path, encoding="utf-8") as file:
    actual = json.load(file)

for dashboard in (expected, actual):
    dashboard.pop("id", None)
    dashboard.pop("version", None)

if expected != actual:
    raise SystemExit("Le dashboard officiel differe du JSON provisionne.")

print("Le dashboard officiel correspond au JSON provisionne.")
PY
then
    cp -- "${BACKUP_FILE}" "${DASHBOARD_FILE}"
    docker compose restart grafana >/dev/null 2>&1 || true
    fail "Validation officielle echouee; le JSON precedent a ete restaure."
fi

log "Publication validee."
log "Le fichier provisionne est pret pour git: ${DASHBOARD_FILE}"

if [[ "${AUTO_DELETE}" == true ]]; then
    if confirm "Supprimer maintenant la copie ${SELECTED_TITLE} (${SELECTED_UID}) ?"; then
        delete_status="$(curl --silent --show-error \
            --user "${GRAFANA_USER}:${GRAFANA_PASSWORD}" \
            --request DELETE \
            --output "${WORK_DIR}/delete.json" \
            --write-out '%{http_code}' \
            "${GRAFANA_URL}/api/dashboards/uid/${SELECTED_UID}")"

        [[ "${delete_status}" == "200" ]] \
            || fail "La suppression de la copie a retourne HTTP ${delete_status}."

        if curl --silent --output /dev/null \
            --user "${GRAFANA_USER}:${GRAFANA_PASSWORD}" \
            --write-out '%{http_code}' \
            "${GRAFANA_URL}/api/dashboards/uid/${SELECTED_UID}" \
            | grep -qx '404'; then
            log "Copie supprimee et absence confirmee via l'API."
        else
            fail "La copie semble encore accessible apres suppression."
        fi
    else
        log "Copie conservee."
    fi
else
    log "Copie conservee par securite. Relancer avec --delete-copy apres validation visuelle."
fi

printf '\nEtapes Git recommandees:\n'
printf '  git diff --check\n'
printf '  git diff --stat\n'
printf '  git diff -- %q\n' "${DASHBOARD_FILE#${PROJECT_DIR}/}"
printf '  git add %q\n' "${DASHBOARD_FILE#${PROJECT_DIR}/}"
printf '  git commit -m "fix: met a jour le dashboard grafana provisionne"\n'

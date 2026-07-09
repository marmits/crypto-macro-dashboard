# Note — Workflow de modification du dashboard Grafana

Le dashboard Grafana principal est provisionné depuis le fichier :

```text
grafana/dashboards/crypto-macro-overview.json
```

Ce fichier est la **source de vérité** du dashboard et doit rester versionné dans Git.

Comme le dashboard est provisionné par fichier, Grafana ne permet pas toujours de sauvegarder directement les modifications depuis l’UI sur le dashboard original.  
Il peut proposer uniquement :

```text
Save as copy
Copy JSON to clipboard
Save JSON to file
```

## Workflow recommandé

À chaque modification du dashboard Grafana :

```text
1. Ouvrir le dashboard officiel dans Grafana
2. Faire Save as copy si Grafana ne permet pas la sauvegarde directe
3. Modifier la copie dans l’UI Grafana
4. Sauvegarder la copie
5. Exporter la copie via l’API Grafana
6. Remplacer grafana/dashboards/crypto-macro-overview.json avec l’export
7. Forcer l’UID officiel du dashboard
8. Redémarrer Grafana
9. Vérifier que le dashboard officiel contient bien les modifications
10. Supprimer la copie dans Grafana
11. Commiter le JSON dans Git
```

***

# Commandes utiles

## 1. Lister les dashboards

```bash
curl -s -u admin:123456 "http://localhost:9070/api/search?query=Crypto" | python3 -m json.tool
```

Repérer l’UID de la copie, par exemple :

```text
Crypto Macro Overview SQLite Copy
```

***

## 2. Exporter la copie

Remplacer `UID_DU_COPY` par l’UID réel :

```bash
curl -s -u admin:123456 \
  "http://localhost:9070/api/dashboards/uid/UID_DU_COPY" \
  | python3 -m json.tool > /tmp/crypto-macro-dashboard-export.json
```

***

## 3. Vérifier que l’export contient bien les modifications

Exemple :

```bash
grep -n "Derniers prix crypto USD\|ETH_USD\|SOL_USD\|HYPE_USD" /tmp/crypto-macro-dashboard-export.json
```

Si le `grep` ne retourne rien, ce n’est pas le bon dashboard exporté ou la copie n’a pas été sauvegardée.

***

## 4. Remplacer le JSON provisionné

```bash
python3 - <<'PY'
import json

source = "/tmp/crypto-macro-dashboard-export.json"
target = "grafana/dashboards/crypto-macro-overview.json"

with open(source, "r", encoding="utf-8") as f:
    payload = json.load(f)

dashboard = payload["dashboard"]

dashboard["id"] = None
dashboard["uid"] = "crypto-macro-overview-sqlite-v2"
dashboard["title"] = "Crypto Macro Overview SQLite"
dashboard["version"] = 1

with open(target, "w", encoding="utf-8") as f:
    json.dump(dashboard, f, indent=2, ensure_ascii=False)

print(f"Dashboard exporté vers {target}")
PY
```

***

## 5. Vérifier le JSON final

```bash
python3 -m json.tool grafana/dashboards/crypto-macro-overview.json > /tmp/check-dashboard.json
```

Puis vérifier les éléments attendus :

```bash
grep -n "Derniers prix crypto USD\|ETH_USD\|SOL_USD\|HYPE_USD" grafana/dashboards/crypto-macro-overview.json
```

***

## 6. Redémarrer Grafana

```bash
docker compose restart grafana
```

Puis recharger le navigateur :

```text
CTRL + F5
```

Vérifier que le dashboard officiel :

```text
Crypto Macro Overview SQLite
```

contient bien les modifications.

***

## 7. Supprimer la copie

Une fois le dashboard officiel validé, supprimer la copie depuis l’UI Grafana, ou via API :

```bash
curl -s -u admin:123456 \
  -X DELETE "http://localhost:9070/api/dashboards/uid/UID_DU_COPY" \
  | python3 -m json.tool
```

***

## 8. Commit Git

```bash
git status
git add grafana/dashboards/crypto-macro-overview.json
git commit -m "feat: met à jour le dashboard grafana"
```

***

# Règle à retenir

```text
Ne jamais considérer une modification UI comme définitive tant qu’elle n’a pas été exportée dans grafana/dashboards/crypto-macro-overview.json et commitée.
```

En résumé :

```text
Grafana UI = outil d’édition visuelle temporaire
JSON provisionné = source de vérité
Git = historique officiel
```

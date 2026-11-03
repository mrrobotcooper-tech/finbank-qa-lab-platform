#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
COMPOSE=(docker compose)

restore() {
  "${COMPOSE[@]}" start redis >/dev/null
  echo "redis restaurado"
}
trap restore EXIT

echo "== Chaos Redis: stop → /ready 503 =="
"${COMPOSE[@]}" stop redis >/dev/null
code="000"
body=""
for _ in $(seq 1 20); do
  body="$(curl -sS -m 8 http://127.0.0.1:8000/ready || true)"
  code="$(curl -sS -m 8 -o /tmp/finbank-ready.json -w '%{http_code}' http://127.0.0.1:8000/ready || true)"
  if [[ "$code" == "503" ]]; then
    break
  fi
  sleep 1
done

if [[ "$code" != "503" ]]; then
  echo "Esperaba HTTP 503 con Redis caído; obtuve $code"
  echo "$body"
  cat /tmp/finbank-ready.json 2>/dev/null || true
  exit 1
fi

python3 - <<'PY'
import json
payload = json.load(open("/tmp/finbank-ready.json"))
assert payload.get("status") != "ok"
redis = next(item for item in payload["components"] if item["name"] == "redis")
assert redis["status"] == "down", redis
print("ready=503 redis=down")
PY

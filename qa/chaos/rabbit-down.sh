#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
COMPOSE=(docker compose)

EMAIL="${FINBANK_PERF_EMAIL:-ana@finbank.test}"
PASSWORD="${FINBANK_PERF_PASSWORD:-Customer1!}"
DEST="${FINBANK_PERF_DEST:-32200000000000000003}"
API="${FINBANK_API_URL:-http://127.0.0.1:8000}"

restore() {
  "${COMPOSE[@]}" start rabbitmq >/dev/null
  echo "rabbitmq restaurado"
}
trap restore EXIT

echo "== Chaos Rabbit: stop → transferencia COMPLETED (FR-NTF-003) =="
login="$(curl -sS -m 10 -X POST "$API/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")"
token="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["access_token"])' <<<"$login")"
source_id="$(curl -sS -m 10 "$API/api/v1/accounts" -H "Authorization: Bearer $token" \
  | python3 -c 'import json,sys; rows=json.load(sys.stdin); print(next(a["id"] for a in rows if a["currency"]=="ARS" and a["type"]=="CHECKING"))')"

"${COMPOSE[@]}" stop rabbitmq >/dev/null
sleep 2

idemp="chaos-$(date +%s)-$RANDOM"
curl -sS -m 20 -X POST "$API/api/v1/transfers" \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $idemp" \
  -d "{\"source_account_id\":\"$source_id\",\"destination_account_number\":\"$DEST\",\"amount\":1,\"currency\":\"ARS\"}" \
  -o /tmp/finbank-chaos-transfer.json

python3 - <<'PY'
import json
payload = json.load(open("/tmp/finbank-chaos-transfer.json"))
assert payload.get("status") == "COMPLETED", payload
print(f"transfer {payload.get('id')} status=COMPLETED con Rabbit caído")
PY

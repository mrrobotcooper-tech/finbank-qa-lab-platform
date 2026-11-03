#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BACKEND="$ROOT/apps/backend"
PYTEST=(pytest -q --tb=line)

if [[ -x "$BACKEND/.venv/bin/pytest" ]]; then
  PYTEST=("$BACKEND/.venv/bin/pytest" -q --tb=line)
fi

cd "$BACKEND"

DETECTORS=(
  "DEF-FUN-001|tests/unit/domain/test_transfers.py::test_rejects_insufficient_funds"
  "DEF-AUT-001|tests/unit/domain/test_authz.py::test_only_customer_moves_money"
  "DEF-DAT-001|tests/unit/domain/test_transfers.py::test_completes_when_funds_and_limits_allow"
  "DEF-VAL-001|tests/unit/domain/test_transfers.py::test_rejects_non_positive_amount"
  "DEF-SEC-001|tests/unit/test_security.py::test_verify_password_rejects_mismatch"
  "DEF-REL-001|tests/unit/test_defects.py::test_outbox_is_written_when_lab_off"
  "DEF-AUD-001|tests/unit/test_defects.py::test_audit_is_written_when_lab_off"
)

echo "== Lab OFF: detectores deben pasar =="
APP_ENV=test FINBANK_DEFECTS="" "${PYTEST[@]}" \
  tests/unit/domain/test_transfers.py::test_rejects_insufficient_funds \
  tests/unit/domain/test_authz.py::test_only_customer_moves_money \
  tests/unit/domain/test_transfers.py::test_completes_when_funds_and_limits_allow \
  tests/unit/domain/test_transfers.py::test_rejects_non_positive_amount \
  tests/unit/test_security.py::test_verify_password_rejects_mismatch \
  tests/unit/test_defects.py::test_outbox_is_written_when_lab_off \
  tests/unit/test_defects.py::test_audit_is_written_when_lab_off

echo "== Lab ON: cada defecto debe romper su detector =="
failed=0
for row in "${DETECTORS[@]}"; do
  id="${row%%|*}"
  test_id="${row#*|}"
  set +e
  APP_ENV=test FINBANK_DEFECTS="$id" "${PYTEST[@]}" "$test_id" >/tmp/finbank-lab-on.out 2>&1
  code=$?
  set -e
  if [[ "$code" -eq 0 ]]; then
    echo "FAIL: $id no rompió $test_id"
    cat /tmp/finbank-lab-on.out
    failed=1
  else
    echo "DETECTADO: $id rompe $test_id (pytest exit $code)"
  fi
done

if [[ "$failed" -ne 0 ]]; then
  echo "Hay defectos sin detector efectivo."
  exit 1
fi

echo "Matriz de detección OK (7/7)."

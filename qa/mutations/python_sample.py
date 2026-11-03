#!/usr/bin/env python3
"""Apply one mutant to require_positive_amount, expect unit tests to kill it."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "apps/backend/src/finbank/domain/money.py"
ORIGINAL = TARGET.read_text(encoding="utf-8")
MUTANT = ORIGINAL.replace(
    "if amount <= 0 and not defect_on(\"DEF-VAL-001\"):",
    "if amount <= 0 and not defect_on(\"DEF-VAL-001\") and False:",
    1,
)
if MUTANT == ORIGINAL:
    print("No se aplicó el mutante; el ancla cambió.", file=sys.stderr)
    sys.exit(2)

pytest = ROOT / "apps/backend/.venv/bin/pytest"
cmd = [
    str(pytest if pytest.exists() else "pytest"),
    "-q",
    "tests/unit/domain/test_money.py::test_require_positive_amount_rejects_non_positive",
]
try:
    TARGET.write_text(MUTANT, encoding="utf-8")
    result = subprocess.run(cmd, cwd=ROOT / "apps/backend", check=False)
finally:
    TARGET.write_text(ORIGINAL, encoding="utf-8")

if result.returncode == 0:
    print("SOBREVIVIÓ: el mutante no fue detectado.")
    sys.exit(1)
print(f"KILLED: pytest exit {result.returncode} con require_positive_amount mutado.")

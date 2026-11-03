#!/usr/bin/env python3
"""NFR-CI-004: a required job that failed or was skipped fails the gate."""

from __future__ import annotations

import json
import os
import sys


def evaluate(needs: dict[str, object]) -> list[str]:
    bad: list[str] = []
    for name, payload in needs.items():
        result = ""
        if isinstance(payload, dict):
            raw = payload.get("result")
            result = str(raw) if raw is not None else ""
        if result != "success":
            bad.append(f"{name}={result or 'missing'}")
    return bad


def main(argv: list[str]) -> int:
    if argv[1:] == ["--self-test"]:
        assert evaluate({"lint": {"result": "success"}}) == []
        assert evaluate({"lint": {"result": "failure"}}) == ["lint=failure"]
        assert evaluate({"lint": {"result": "skipped"}}) == ["lint=skipped"]
        assert evaluate({"lint": {"result": "cancelled"}}) == ["lint=cancelled"]
        assert evaluate({"lint": {}}) == ["lint=missing"]
        print("require-jobs self-test OK")
        return 0

    raw = os.environ.get("NEEDS_JSON", "")
    if not raw.strip():
        print("NEEDS_JSON vacío", file=sys.stderr)
        return 2
    needs = json.loads(raw)
    if not isinstance(needs, dict) or not needs:
        print("NEEDS_JSON no es un objeto de jobs", file=sys.stderr)
        return 2
    bad = evaluate(needs)
    if bad:
        print("NFR-CI-004: un job crítico no quedó en success:")
        for item in bad:
            print(f"  - {item}")
        print("La pipeline no puede publicarse como verde.")
        return 1
    print("Quality gate OK:", ", ".join(sorted(needs)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

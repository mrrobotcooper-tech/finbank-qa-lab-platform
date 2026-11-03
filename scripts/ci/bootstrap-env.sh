#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
if [[ ! -f .env ]]; then
  cp .env.example .env
fi
mkdir -p qa/reports/allure-results qa/reports/perf qa/reports/zap qa/reports/deps

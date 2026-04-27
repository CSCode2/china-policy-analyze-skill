#!/bin/bash
# Run smoke tests to verify system is working
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${REPO_ROOT}/.venv/bin/activate"

REPORT_DIR="${REPO_ROOT}/reports"
mkdir -p "${REPORT_DIR}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SMOKE_REPORT="${REPORT_DIR}/smoke_${TIMESTAMP}.txt"

echo "Running smoke tests..." | tee "${SMOKE_REPORT}"

python -m pytest "${REPO_ROOT}/tests/" -v -m "not slow and not integration" --tb=short 2>&1 | tee -a "${SMOKE_REPORT}"

EXIT_CODE=${PIPESTATUS[0]}

echo "" | tee -a "${SMOKE_REPORT}"
echo "Smoke test exit code: ${EXIT_CODE}" | tee -a "${SMOKE_REPORT}"

exit ${EXIT_CODE}

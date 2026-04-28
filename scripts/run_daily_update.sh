#!/bin/bash
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${REPO_ROOT}/venv/bin/activate"

python "${REPO_ROOT}/scripts/_run_daily_update.py" "$@"

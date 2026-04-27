#!/bin/bash
# Bootstrap the China Policy Analyze Skill project
set -e

echo "=== Bootstrapping China Policy Analyze Skill ==="

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv"

mkdir -p "${REPO_ROOT}/corpus/raw/central"
mkdir -p "${REPO_ROOT}/corpus/raw/ministries"
mkdir -p "${REPO_ROOT}/corpus/raw/local"
mkdir -p "${REPO_ROOT}/corpus/raw/legal"
mkdir -p "${REPO_ROOT}/corpus/raw/court"
mkdir -p "${REPO_ROOT}/corpus/raw/police"
mkdir -p "${REPO_ROOT}/corpus/raw/procuratorate"
mkdir -p "${REPO_ROOT}/corpus/raw/regulators"
mkdir -p "${REPO_ROOT}/corpus/raw/meetings"
mkdir -p "${REPO_ROOT}/corpus/raw/speeches"
mkdir -p "${REPO_ROOT}/corpus/raw/data"
mkdir -p "${REPO_ROOT}/corpus/raw/seed"
mkdir -p "${REPO_ROOT}/corpus/processed/markdown"
mkdir -p "${REPO_ROOT}/corpus/processed/json"
mkdir -p "${REPO_ROOT}/corpus/processed/seed"
mkdir -p "${REPO_ROOT}/corpus/metadata"
mkdir -p "${REPO_ROOT}/rag/bm25_index"
mkdir -p "${REPO_ROOT}/rag/vector_index"
mkdir -p "${REPO_ROOT}/reports"
mkdir -p "${REPO_ROOT}/cache/content"
mkdir -p "${REPO_ROOT}/cache/index"
mkdir -p "${REPO_ROOT}/cache/graph"
mkdir -p "${REPO_ROOT}/cache/phrases"
mkdir -p "${REPO_ROOT}/cache/forecasts"
mkdir -p "${REPO_ROOT}/cache/incidents"
mkdir -p "${REPO_ROOT}/cache/metrics"
mkdir -p "${REPO_ROOT}/cache/questions"

if ! command -v uv &>/dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "Creating virtual environment..."
uv venv "${VENV_DIR}" --python python3.10

echo "Installing dependencies..."
uv pip install -e "${REPO_ROOT}[dev]" --python "${VENV_DIR}/bin/python"

echo "Downloading seed corpus..."
bash "${REPO_ROOT}/scripts/bootstrap_seed_corpus.sh"

echo "Building initial indexes..."
bash "${REPO_ROOT}/scripts/rebuild_index.sh"

echo "=== Bootstrap complete ==="

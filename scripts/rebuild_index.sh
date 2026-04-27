#!/bin/bash
# Rebuild BM25 and optional vector indexes
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${REPO_ROOT}/.venv/bin/activate"

CHUNKS_PATH="${REPO_ROOT}/rag/bm25_index/chunks.jsonl"

if [ ! -f "${CHUNKS_PATH}" ]; then
    echo "No chunks.jsonl found, building chunks first..."
    python -c "
from china_policy_skill.index.build_chunks import ChunkBuilder
import glob, json, os

builder = ChunkBuilder()
all_chunks = []
for md_file in sorted(glob.glob('${REPO_ROOT}/corpus/processed/markdown/*.md')):
    with open(md_file) as f:
        text = f.read()
    meta_file = md_file.replace('.md', '.meta.json')
    meta = {}
    if os.path.exists(meta_file):
        with open(meta_file) as f:
            meta = json.load(f)
    chunks = builder.build_from_document(meta, text)
    all_chunks.extend(chunks)
builder.write_chunks(all_chunks, '${REPO_ROOT}/rag/bm25_index')
print(f'Built {len(all_chunks)} chunks')
"
fi

echo "Building BM25 index..."
python -c "
from china_policy_skill.index.build_bm25_index import BM25IndexBuilder
indexer = BM25IndexBuilder('${REPO_ROOT}/rag/bm25_index')
indexer.build('${REPO_ROOT}/rag/bm25_index/chunks.jsonl')
"

if [ "${1}" = "--with-vectors" ]; then
    echo "Building vector index..."
    python -c "
from china_policy_skill.index.build_vector_index import VectorIndexBuilder
builder = VectorIndexBuilder()
builder.build('${REPO_ROOT}/rag/bm25_index/chunks.jsonl')
"
fi

echo "Index rebuild complete."

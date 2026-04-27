#!/bin/bash
# Run daily policy update - fetch, parse, dedup, score, report
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${REPO_ROOT}/.venv/bin/activate"

TODAY=$(date +%Y-%m-%d)
REPORT_DIR="${REPO_ROOT}/reports"
mkdir -p "${REPORT_DIR}"

python -m china_policy_skill.fetch.fetch_html --mode daily
python -m china_policy_skill.fetch.fetch_pdf --mode daily
python -m china_policy_skill.fetch.fetch_rss --mode daily

python -m china_policy_skill.parse.html_to_md --input "${REPO_ROOT}/corpus/raw" --output "${REPO_ROOT}/corpus/processed/markdown"
python -m china_policy_skill.parse.pdf_to_md --input "${REPO_ROOT}/corpus/raw" --output "${REPO_ROOT}/corpus/processed/markdown"
python -m china_policy_skill.parse.extract_metadata --input "${REPO_ROOT}/corpus/processed/markdown" --output "${REPO_ROOT}/corpus/metadata"
python -m china_policy_skill.parse.normalize_text --input "${REPO_ROOT}/corpus/processed/markdown" --output "${REPO_ROOT}/corpus/processed/markdown"

python -m china_policy_skill.utils.hashing --mode dedup --corpus "${REPO_ROOT}/corpus"

python -c "
from china_policy_skill.index.build_chunks import ChunkBuilder
from china_policy_skill.index.build_bm25_index import BM25IndexBuilder
import glob, json

builder = ChunkBuilder()
all_chunks = []
for md_file in sorted(glob.glob('${REPO_ROOT}/corpus/processed/markdown/*.md')):
    with open(md_file) as f:
        text = f.read()
    meta_file = md_file.replace('.md', '.meta.json')
    meta = {}
    import os
    if os.path.exists(meta_file):
        with open(meta_file) as f:
            meta = json.load(f)
    chunks = builder.build_from_document(meta, text)
    all_chunks.extend(chunks)
builder.write_chunks(all_chunks, '${REPO_ROOT}/rag/bm25_index')

indexer = BM25IndexBuilder('${REPO_ROOT}/rag/bm25_index')
indexer.build('${REPO_ROOT}/rag/bm25_index/chunks.jsonl')
"

python -c "
from china_policy_skill.report.daily_update import DailyUpdateGenerator
import json, glob

docs = []
for f in glob.glob('${REPO_ROOT}/corpus/metadata/*.json'):
    with open(f) as fh:
        docs.append(json.load(fh))

errors = []
error_log = '${REPO_ROOT}/cache/incidents/fetch_errors.jsonl'
import os
if os.path.exists(error_log):
    with open(error_log) as fh:
        for line in fh:
            line = line.strip()
            if line:
                errors.append(json.loads(line))

gen = DailyUpdateGenerator()
report = gen.generate(docs, errors)
with open('${REPO_ROOT}/reports/daily_${TODAY}.md', 'w') as fh:
    fh.write(report)
"

echo "Daily update complete. Report: ${REPORT_DIR}/daily_${TODAY}.md"

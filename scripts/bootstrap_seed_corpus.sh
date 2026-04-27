#!/bin/bash
# Download and process seed corpus documents
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${REPO_ROOT}/.venv/bin/activate"

SEED_RAW="${REPO_ROOT}/corpus/raw/seed"
SEED_PROCESSED="${REPO_ROOT}/corpus/processed/seed"
SEED_METADATA="${REPO_ROOT}/corpus/metadata"
mkdir -p "${SEED_RAW}" "${SEED_PROCESSED}" "${SEED_METADATA}"

MANIFEST="${REPO_ROOT}/corpus/seed_manifest.yaml"
if [ ! -f "${MANIFEST}" ]; then
    echo "Seed manifest not found: ${MANIFEST}"
    exit 1
fi

python -c "
import yaml, json, os, sys

with open('${MANIFEST}') as f:
    manifest = yaml.safe_load(f)

from china_policy_skill.fetch.fetch_html import HTMLFetcher
from china_policy_skill.fetch.fetch_pdf import PDFFetcher
from china_policy_skill.parse.html_to_md import HTMLToMarkdown
from china_policy_skill.parse.pdf_to_md import PDFToMarkdown
from china_policy_skill.parse.extract_metadata import MetadataExtractor
from china_policy_skill.parse.normalize_text import TextNormalizer
from china_policy_skill.index.build_chunks import ChunkBuilder
from china_policy_skill.index.build_bm25_index import BM25IndexBuilder
from china_policy_skill.utils.hashing import content_hash, is_duplicate, record_hash

html_fetcher = HTMLFetcher(timeout=30)
pdf_fetcher = PDFFetcher(timeout=60)
html_converter = HTMLToMarkdown()
pdf_converter = PDFToMarkdown()
metadata_extractor = MetadataExtractor()
text_normalizer = TextNormalizer()
chunk_builder = ChunkBuilder()

hash_store = '${REPO_ROOT}/cache/content/hash_store.json'
all_chunks = []

entries = manifest.get('entries', [])
total = len(entries)
success = 0
failed = 0

for i, entry in enumerate(entries):
    doc_id = entry.get('doc_id', f'seed_{i}')
    url = entry.get('source_url', '')
    doc_type = entry.get('doc_type', 'html')
    required = entry.get('required', False)
    parser_type = entry.get('parser', 'auto')

    print(f'[{i+1}/{total}] {entry.get(\"title\", doc_id)}')

    if not url:
        print(f'  SKIP: no URL')
        if required:
            print(f'  WARNING: required document missing URL')
        continue

    try:
        if doc_type == 'pdf':
            result = pdf_fetcher.fetch(url, save_to=os.path.join('${SEED_RAW}', f'{doc_id}.pdf'))
            if result.error:
                print(f'  ERROR: {result.error}')
                failed += 1
                if required:
                    print(f'  CRITICAL: required document failed')
                continue
            markdown = pdf_converter.convert(result.file_path or result.content)
        else:
            result = html_fetcher.fetch(url)
            if result.error:
                print(f'  ERROR: {result.error}')
                failed += 1
                if required:
                    print(f'  CRITICAL: required document failed')
                continue
            markdown = html_converter.convert(result.html, url)

        if not markdown or not markdown.strip():
            print(f'  ERROR: empty content after parsing')
            failed += 1
            continue

        h = content_hash(markdown)
        if is_duplicate(h, hash_store):
            print(f'  SKIP: duplicate content')
            continue
        record_hash(h, doc_id, hash_store)

        markdown = text_normalizer.normalize(markdown)
        markdown = text_normalizer.clean_noise(markdown)

        md_path = os.path.join('${SEED_PROCESSED}', f'{doc_id}.md')
        with open(md_path, 'w', encoding='utf-8') as fh:
            fh.write(markdown)

        metadata = metadata_extractor.extract(result.html or '', url)
        meta_dict = {
            'doc_id': doc_id,
            'title': entry.get('title', metadata.title),
            'source_name': entry.get('source_name', ''),
            'source_url': url,
            'source_level': entry.get('source_level', ''),
            'doc_type': entry.get('doc_type', ''),
            'topic_tags': entry.get('topic_tags', []),
            'publish_date': metadata.publish_date,
            'organization': metadata.organization or entry.get('source_name', ''),
            'authority_level': entry.get('source_level', ''),
        }

        meta_path = os.path.join('${SEED_METADATA}', f'{doc_id}.meta.json')
        with open(meta_path, 'w', encoding='utf-8') as fh:
            json.dump(meta_dict, fh, ensure_ascii=False, indent=2)

        chunks = chunk_builder.build_from_document(meta_dict, markdown)
        all_chunks.extend(chunks)

        success += 1
        print(f'  OK: {len(chunks)} chunks')

    except Exception as e:
        print(f'  ERROR: {e}')
        failed += 1
        if required:
            print(f'  CRITICAL: required document failed')

print(f'\\nSeed corpus: {success} succeeded, {failed} failed out of {total}')

if all_chunks:
    chunk_builder.write_chunks(all_chunks, '${REPO_ROOT}/rag/bm25_index')
    indexer = BM25IndexBuilder('${REPO_ROOT}/rag/bm25_index')
    indexer.build('${REPO_ROOT}/rag/bm25_index/chunks.jsonl')
    print(f'Built index with {len(all_chunks)} chunks')
"

echo "Seed corpus bootstrap complete."

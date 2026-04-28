#!/usr/bin/env python3
"""List all new documents with full metadata for briefing."""
import json, os, glob

META_DIR = 'corpus/metadata'
docs = []
for f in glob.glob(os.path.join(META_DIR, '*.json')):
    with open(f) as fh:
        m = json.load(fh)
    docs.append(m)

# Sort by publish_date desc
docs.sort(key=lambda x: x.get('publish_date', ''), reverse=True)

print(f"Total: {len(docs)} docs\n")
# Show last 15
for d in docs[:15]:
    title = d.get('title', '??')[:60]
    date = d.get('publish_date', '??')
    body = d.get('issuing_body', '??')
    level = d.get('authority_level', '?')
    doc_num = d.get('doc_number', '')
    dtype = d.get('doc_type', '')
    print(f"[{level}] {title}")
    print(f"    日期:{date} 发文:{body} 类型:{dtype} 文号:{doc_num}")
    print()

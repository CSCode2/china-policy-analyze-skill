#!/usr/bin/env python3
"""Read key new docs for briefing."""
import json, os, glob

META_DIR = 'corpus/metadata'
MD_DIR = 'corpus/processed/markdown'

# Find the 5 important S-level docs (中办国办 files)
for f in sorted(glob.glob(os.path.join(META_DIR, '*.json'))):
    with open(f) as fh:
        m = json.load(fh)
    if '中共中央办公厅' in m.get('title', '') or '碳达峰' in m.get('title', '') or '新就业群体' in m.get('title', ''):
        doc_id = m['doc_id']
        md_path = os.path.join(MD_DIR, f'{doc_id}.md')
        print(f"\n{'='*60}")
        print(f"标题: {m['title']}")
        print(f"日期: {m['publish_date']}")
        print(f"文号: {m.get('doc_number','')}")
        print(f"发文: {m.get('issuing_body','')}")
        print(f"URL: {m.get('url','')}")
        if os.path.exists(md_path):
            with open(md_path) as fh:
                content = fh.read()
            # Print first 800 chars
            print(f"内容摘要:\n{content[:800]}")
        else:
            print("(无正文)")

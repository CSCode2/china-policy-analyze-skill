#!/usr/bin/env python3
"""Fix dates for gov.cn docs by extracting from content."""
import json, os, re, glob

META_DIR = 'corpus/metadata'
MD_DIR = 'corpus/processed/markdown'

for f in glob.glob(os.path.join(META_DIR, '*.json')):
    with open(f) as fh:
        m = json.load(fh)
    
    doc_id = m.get('doc_id', '')
    
    # Only fix docs with wrong date pattern (2026-04-04 from earlier bug)
    if m.get('publish_date') == '2026-04-04' and 'gov.cn' in m.get('url', ''):
        # Try to find date from markdown content
        md_path = os.path.join(MD_DIR, f'{doc_id}.md')
        if os.path.exists(md_path):
            with open(md_path) as fh:
                content = fh.read()[:3000]
            
            # Look for Chinese date format: 2026年4月XX日 or 二〇二六年四月XX日
            date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', content)
            if date_match:
                y, mo, d = date_match.groups()
                correct_date = f"{y}-{int(mo):02d}-{int(d):02d}"
                print(f"Fix date: {m['publish_date']} → {correct_date} ({m['title'][:40]})")
                m['publish_date'] = correct_date
            else:
                # Try from URL: /202604/ → 2026-04, but day unknown, use 2026-04-28 as best guess
                url_date = re.search(r'/(\d{6})/content_', m.get('url',''))
                if url_date:
                    ym = url_date.group(1)
                    m['publish_date'] = f"20{ym[:2]}-{ym[2:4]}-28"
                    print(f"Fix date from URL: → {m['publish_date']} ({m['title'][:40]})")
                else:
                    print(f"Cannot fix date for: {m['title'][:40]}")
        
        with open(f, 'w') as fh:
            json.dump(m, fh, ensure_ascii=False, indent=2)

# Also fix doc_ids to match correct dates
for f in glob.glob(os.path.join(META_DIR, '*.json')):
    with open(f) as fh:
        m = json.load(fh)
    
    old_doc_id = m.get('doc_id', '')
    if old_doc_id.startswith('20260404'):
        new_doc_id = old_doc_id.replace('20260404', m['publish_date'].replace('-',''))
        if new_doc_id != old_doc_id:
            # Rename all files
            for subdir, ext in [('corpus/metadata', '.json'), ('corpus/raw', '.html'), 
                               ('corpus/processed/markdown', '.md'), ('corpus/processed/text', '.txt')]:
                old_path = os.path.join(subdir, f'{old_doc_id}{ext}')
                new_path = os.path.join(subdir, f'{new_doc_id}{ext}')
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    print(f"Rename: {old_doc_id}{ext} → {new_doc_id}{ext}")
            
            m['doc_id'] = new_doc_id
            with open(os.path.join('corpus/metadata', f'{new_doc_id}.json'), 'w') as fh:
                json.dump(m, fh, ensure_ascii=False, indent=2)
            # Remove old json if different
            old_json = os.path.join('corpus/metadata', f'{old_doc_id}.json')
            if os.path.exists(old_json) and old_doc_id != new_doc_id:
                os.remove(old_json)

print("\nDone fixing dates and doc_ids.")

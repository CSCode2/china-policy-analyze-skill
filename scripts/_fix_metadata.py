#!/usr/bin/env python3
"""Fix metadata: clean titles and correct dates."""
import json, os, re, glob

META_DIR = 'corpus/metadata'

for f in glob.glob(os.path.join(META_DIR, '*.json')):
    with open(f) as fh:
        m = json.load(fh)
    
    changed = False
    
    # Fix date: 2026-26-04 → 2026-04-26
    if m.get('publish_date') and re.match(r'2026-26-', m['publish_date']):
        old = m['publish_date']
        m['publish_date'] = old.replace('2026-26-', '2026-04-')
        print(f"Fix date: {old} → {m['publish_date']} ({m['title'][:30]})")
        changed = True
    
    # Fix date: 2026-04-28 that should be from URL pattern
    # Check doc_id for actual date info
    doc_id = m.get('doc_id', '')
    
    # Clean title: remove suffixes
    for suffix in ['_最新政策', '_政策解读', '_中华人民共和国商务部', '_中国证券监督管理委员会',
                   '_中国政府网', '——中国政府网']:
        if suffix in m.get('title', ''):
            m['title'] = m['title'].replace(suffix, '').strip()
            print(f"Clean title: removed '{suffix}'")
            changed = True
    
    # Clean title: remove leading/trailing whitespace/underscores
    title = m.get('title', '').strip().strip('_').strip()
    if title != m.get('title', ''):
        m['title'] = title
        changed = True
    
    if changed:
        with open(f, 'w') as fh:
            json.dump(m, fh, ensure_ascii=False, indent=2)

print("\nDone fixing metadata.")

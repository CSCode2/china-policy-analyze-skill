#!/usr/bin/env python3
"""Quick status check for daily update."""
import json, os, glob

meta_dir = 'corpus/metadata'
files = glob.glob(os.path.join(meta_dir, '*.json'))
dates = []
for f in files:
    try:
        with open(f) as fh:
            m = json.load(fh)
            if m.get('publish_date'):
                dates.append(m['publish_date'])
    except:
        pass

dates.sort(reverse=True)
print(f'Total docs: {len(files)}')
print(f'Latest 10 dates:')
for d in dates[:10]:
    print(f'  {d}')

report = 'reports/daily_2026-04-28.md'
if os.path.exists(report):
    with open(report) as f:
        print(f'\nToday report ({len(f.read())} chars)')

err_file = 'corpus/metadata/fetch_errors.jsonl'
if os.path.exists(err_file):
    with open(err_file) as f:
        lines = f.readlines()
    print(f'\nFetch errors: {len(lines)} total')
    if lines:
        for l in lines[-3:]:
            print(f'  {l.strip()}')

#!/usr/bin/env python3
"""Fetch latest gov.cn policy documents."""
import sys, os, json, hashlib, re
from datetime import datetime

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from china_policy_skill.fetch.fetch_html import HTMLFetcher
from china_policy_skill.parse.html_to_md import HTMLToMarkdown

fetcher = HTMLFetcher(timeout=15, rate_limit_delay=1.5)
md_converter = HTMLToMarkdown()

META_DIR = os.path.join(REPO_ROOT, 'corpus', 'metadata')
RAW_DIR = os.path.join(REPO_ROOT, 'corpus', 'raw')
MD_DIR = os.path.join(REPO_ROOT, 'corpus', 'processed', 'markdown')
TXT_DIR = os.path.join(REPO_ROOT, 'corpus', 'processed', 'text')
REPORT = []

for d in [META_DIR, RAW_DIR, MD_DIR, TXT_DIR]:
    os.makedirs(d, exist_ok=True)

def load_existing_hashes():
    hashes = set()
    for f in os.listdir(META_DIR):
        if f.endswith('.json'):
            try:
                with open(os.path.join(META_DIR, f)) as fh:
                    m = json.load(fh)
                    if m.get('content_hash'):
                        hashes.add(m['content_hash'])
            except:
                pass
    return hashes

def save_document(url, title, content, publish_date, doc_number, issuing_body, doc_type, authority_level):
    existing_hashes = load_existing_hashes()
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    if content_hash in existing_hashes:
        print(f"  SKIP (duplicate): {title[:40]}")
        return False
    
    doc_id = f"{publish_date.replace('-','')}_{content_hash[:8]}"
    
    with open(os.path.join(RAW_DIR, f'{doc_id}.html'), 'w') as f:
        f.write(f'<!-- fetched from {url} -->\n')
    
    md_content = f"# {title}\n\n{content}"
    with open(os.path.join(MD_DIR, f'{doc_id}.md'), 'w') as f:
        f.write(md_content)
    
    with open(os.path.join(TXT_DIR, f'{doc_id}.txt'), 'w') as f:
        f.write(content)
    
    meta = {
        'doc_id': doc_id,
        'title': title,
        'publish_date': publish_date,
        'doc_number': doc_number or '',
        'issuing_body': issuing_body,
        'doc_type': doc_type,
        'organization': issuing_body,
        'authority_level': authority_level,
        'url': url,
        'content_hash': content_hash,
        'fetched_at': datetime.now().isoformat()
    }
    with open(os.path.join(META_DIR, f'{doc_id}.json'), 'w') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    print(f"  SAVED: {title[:60]} ({publish_date})")
    REPORT.append(meta)
    return True

# --- Gov.cn: resolve relative links ---
print("=== Fetching gov.cn latest policies ===")
r = fetcher.fetch('https://www.gov.cn/zhengce/')
if r.html:
    # Match both relative and absolute links
    rel_links = re.findall(r'href="\./(\d{6}/content_\d+\.htm)"', r.html)
    abs_links = re.findall(r'href="(https://www\.gov\.cn/zhengce/content/\d{6}/content_\d+\.htm)"', r.html)
    
    # Convert relative to absolute
    all_links = [f'https://www.gov.cn/zhengce/{l}' for l in rel_links] + abs_links
    # Deduplicate by content_ID
    seen_ids = set()
    unique_links = []
    for l in all_links:
        cid = re.search(r'content_(\d+)', l)
        if cid and cid.group(1) not in seen_ids:
            seen_ids.add(cid.group(1))
            unique_links.append(l)
    
    print(f"  Found {len(unique_links)} unique policy links")
    
    for url in unique_links[:5]:
        try:
            ar = fetcher.fetch(url)
            if ar.error or not ar.html or len(ar.html) < 200:
                print(f"  Skip {url}: {ar.error or 'too short'}")
                continue
            md_text = md_converter.convert(ar.html)
            if len(md_text.strip()) < 200:
                print(f"  Skip {url}: md too short")
                continue
            
            # Extract title
            title_match = re.search(r'<title>([^<]+)</title>', ar.html)
            title = title_match.group(1).replace('_中国政府网','').strip() if title_match else url.split('/')[-1]
            
            # Extract date from URL
            date_match = re.search(r'/(\d{6})/content_', url)
            if date_match:
                ym = date_match.group(1)
                publish_date = f"20{ym[:2]}-{ym[2:4]}-{ym[4:6]}" if ym[:2] == '26' else f"2026-{ym[2:4]}-{ym[4:6]}"
            else:
                publish_date = '2026-04-28'
            
            # Try to extract doc number from content
            doc_num_match = re.search(r'国(?:办)?发〔\d{4}〕\d+号|国令第\d+号', md_text[:2000])
            doc_number = doc_num_match.group(0) if doc_num_match else ''
            
            save_document(url, title, md_text.strip(), publish_date, doc_number, '国务院', '政策文件', 'S')
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
else:
    print(f"  ERROR: {r.error}")

print(f"\n=== New gov.cn docs: {len(REPORT)} ===")
for r in REPORT:
    print(f"  {r['title'][:60]} ({r['publish_date']}) - {r.get('doc_number','')}")

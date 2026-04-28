#!/usr/bin/env python3
"""Manually fetch latest policies from key sources not covered by daily script."""
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

def fetch_and_process(source_name, list_url, link_pattern, base_url, issuing_body, doc_type, authority_level, max_links=3, date_default='2026-04-28'):
    print(f"=== Fetching {source_name} ===")
    try:
        result = fetcher.fetch(list_url)
        if result.error or not result.html:
            print(f"  ERROR: {result.error or 'no html'}")
            return
        html = result.html
        links = re.findall(link_pattern, html)
        if base_url and not list_url.startswith('http'):
            links = [f'{base_url}{l}' if l.startswith('/') else l for l in links]
        elif base_url:
            links = [f'{base_url}{l}' if l.startswith('/') else l for l in links]
        links = list(set(links))[:max_links]
        print(f"  Found {len(links)} links")
        for url in links:
            try:
                ar = fetcher.fetch(url)
                if ar.error or not ar.html or len(ar.html) < 200:
                    continue
                md_text = md_converter.convert(ar.html)
                if len(md_text.strip()) < 200:
                    continue
                title_match = re.search(r'<title>([^<]+)</title>', ar.html)
                title = title_match.group(1).strip() if title_match else url.split('/')[-1]
                # Clean common suffixes
                for suffix in ['_中国政府网', '_中华人民共和国商务部', '_中华人民共和国工业和信息化部', 
                              '_中华人民共和国外交部', '_国家统计局', '_中国证监会', '_中国人民银行',
                              '_中华人民共和国司法部', '_中华人民共和国最高人民法院', '_中华人民共和国最高人民检察院',
                              '_国家市场监督管理总局', '_中华人民共和国生态环境部', '_国家金融监督管理总局']:
                    title = title.replace(suffix, '')
                title = title.strip()
                save_document(url, title, md_text.strip(), date_default, '', issuing_body, doc_type, authority_level)
            except Exception as e:
                print(f"  Error fetching {url}: {e}")
    except Exception as e:
        print(f"  Error: {e}")

# Source 1: gov.cn/zhengce/ 
fetch_and_process('gov.cn政策文件', 'https://www.gov.cn/zhengce/',
    r'href="(https?://www\.gov\.cn/zhengce/\d{6}/content_\d+\.htm)"',
    '', '国务院', '政策文件', 'S', max_links=3)

# Source 2: mofcom
fetch_and_process('商务部', 'https://www.mofcom.gov.cn/xwfb/',
    r'href="([^"]*\.shtml)"',
    'https://www.mofcom.gov.cn', '商务部', '新闻发布', 'A', max_links=2)

# Source 3: MIIT homepage
fetch_and_process('工信部', 'https://www.miit.gov.cn/',
    r'href="(/xwdt/[^"]*art/\d{4}/art_\d+\.html)"',
    'https://www.miit.gov.cn', '工信部', '新闻发布', 'A', max_links=2)

# Source 4: MOJ homepage
fetch_and_process('司法部', 'https://www.moj.gov.cn/',
    r'href="(/pub/sfbgw/zwgkzt/[^"]*)"',
    'https://www.moj.gov.cn', '司法部', '政务公开', 'A', max_links=2)

# Source 5: MFA
fetch_and_process('外交部', 'https://www.mfa.gov.cn/wjbxw/',
    r'href="(/web/wjbxw_[^"]*t\d+\.shtml)"',
    'https://www.mfa.gov.cn', '外交部', '外交新闻', 'A', max_links=2)

# Source 6: stats.gov.cn
fetch_and_process('国家统计局', 'https://www.stats.gov.cn/sj/zxfb/',
    r'href="(/sj/zxfb/\d{6}/t\d+\.html)"',
    'https://www.stats.gov.cn', '国家统计局', '统计数据', 'A', max_links=2)

# Source 7: CSRC
fetch_and_process('证监会', 'https://www.csrc.gov.cn/csrc/c100032/',
    r'href="(/csrc/c\d+/c\d+/content\.shtml)"',
    'https://www.csrc.gov.cn', '证监会', '监管公告', 'A', max_links=2)

# Source 8: PBC (full column paths)
for col_url, col_type in [
    ('https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html', '新闻发布'),
    ('https://www.pbc.gov.cn/zhengcehuobisi/125057/125089/index.html', '货币政策'),
]:
    fetch_and_process(f'央行{col_type}', col_url,
        r'href="(/goutongjiaoliu/[^"]*|/zhengcehuobisi/[^"]*)"',
        'https://www.pbc.gov.cn', '央行', col_type, 'A', max_links=2)

# Source 9: SPC (Supreme People's Court)
fetch_and_process('最高法', 'https://www.court.gov.cn/',
    r'href="(/zixun/[^"]*content_\d+\.html)"',
    'https://www.court.gov.cn', '最高法', '司法新闻', 'A', max_links=2)

# Source 10: SPP (Supreme People's Procuratorate)
fetch_and_process('最高检', 'https://www.spp.gov.cn/',
    r'href="(/spp/xwfb/[^"]*\.shtml)"',
    'https://www.spp.gov.cn', '最高检', '检察新闻', 'A', max_links=2)

# Source 11: SAMR
fetch_and_process('市监总局', 'https://www.samr.gov.cn/',
    r'href="(/xw/zj/art/\d{4}/art_\d+\.html)"',
    'https://www.samr.gov.cn', '市监总局', '新闻发布', 'A', max_links=2)

# Source 12: MEE
fetch_and_process('生态环境部', 'https://www.mee.gov.cn/',
    r'href="(/ywdt/hjzx/[^"]*t\d+\.shtml)"',
    'https://www.mee.gov.cn', '生态环境部', '环境新闻', 'A', max_links=2)

# Source 13: NFRA
fetch_and_process('金融监管总局', 'https://www.nfra.gov.cn/xwzx/',
    r'href="(/xwzx/[^"]*art/\d{4}/art_\d+\.html)"',
    'https://www.nfra.gov.cn', '金融监管总局', '监管新闻', 'A', max_links=2)

# Source 14: NDRC
fetch_and_process('发改委', 'https://www.ndrc.gov.cn/xwdt/xwfb/',
    r'href="(/xwdt/\d{6}/t\d+\.html)"',
    'https://www.ndrc.gov.cn', '发改委', '新闻发布', 'A', max_links=2)

print(f"\n=== Total new docs saved: {len(REPORT)} ===")
for r in REPORT:
    print(f"  {r['title'][:50]} ({r['publish_date']}) - {r['issuing_body']}")

#!/usr/bin/env python3
"""Debug link extraction from gov.cn."""
import sys, os, re
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))
from china_policy_skill.fetch.fetch_html import HTMLFetcher

f = HTMLFetcher(timeout=15, rate_limit_delay=1.0)
r = f.fetch('https://www.gov.cn/zhengce/')
if r.html:
    links = re.findall(r'href="(.*?content_\d+.*?)"', r.html)
    print(f'Found {len(links)} content links')
    for l in links[:10]:
        print(f'  {l}')
    
    links2 = re.findall(r'href="(.*?)"', r.html)
    zhengce = [l for l in links2 if 'zhengce' in l and len(l) > 20]
    print(f'\nZhengce links: {len(zhengce)}')
    for l in zhengce[:10]:
        print(f'  {l}')
else:
    print(f'Error: {r.error}')

#!/usr/bin/env python3
"""Geopolitical risk monitor - fetch MFA, MOFCOM, JHSJK, gov.cn"""
import sys, re, json
from china_policy_skill.fetch.fetch_html import HTMLFetcher

fetcher = HTMLFetcher()

def fetch_mfa():
    """Fetch MFA homepage, extract spokesperson and news links"""
    print("=== FETCHING MFA ===")
    r = fetcher.fetch('https://www.mfa.gov.cn/')
    if not r or not r.html:
        print("MFA homepage: FAILED")
        return []
    
    print(f"MFA homepage: {len(r.html)} chars")
    
    results = []
    # Spokesperson links
    sp_links = re.findall(r'href="(\./fyrbt_673021/\d{6}/t\d+_\d+\.shtml)"', r.html)
    # Ministry news links
    news_links = re.findall(r'href="(\./wjbxw_new/\d{6}/t\d+_\d+\.shtml)"', r.html)
    
    all_links = [(l.replace('./','https://www.mfa.gov.cn/'), 'spokesperson' if 'fyrbt' in l else 'news') for l in sp_links[:5] + news_links[:5]]
    
    for url, link_type in all_links:
        print(f"  Fetching {link_type}: {url}")
        ar = fetcher.fetch(url)
        if not ar or not ar.html:
            print(f"    FAILED")
            continue
        
        # Extract title from h1
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', ar.html, re.DOTALL)
        title = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip() if h1_match else "No title"
        
        # Extract date
        date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', ar.html)
        date_str = f"{date_match.group(1)}-{int(date_match.group(2)):02d}-{int(date_match.group(3)):02d}" if date_match else "unknown"
        
        # Extract body from <p> tags
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', ar.html, re.DOTALL)
        body = '\n'.join(re.sub(r'<[^>]+>', '', p).strip() for p in paragraphs if re.sub(r'<[^>]+>', '', p).strip())
        
        print(f"    Title: {title}")
        print(f"    Date: {date_str}")
        print(f"    Body length: {len(body)} chars")
        results.append({
            'source': 'MFA',
            'type': link_type,
            'title': title,
            'date': date_str,
            'url': url,
            'body': body[:3000],
            'body_len': len(body)
        })
    
    return results

def fetch_mofcom():
    """Fetch MOFCOM homepage for trade news"""
    print("\n=== FETCHING MOFCOM ===")
    r = fetcher.fetch('https://www.mofcom.gov.cn/')
    if not r or not r.html:
        print("MOFCOM homepage: FAILED")
        return []
    
    print(f"MOFCOM homepage: {len(r.html)} chars")
    
    results = []
    # Spokesperson links
    sp_links = re.findall(r'href="(/xwfb/xwfyrth/art/\d{4}/art_\w+\.html)"', r.html)
    # Daily news links
    daily_links = re.findall(r'href="(/xwfb/rcxwfb/art/\d{4}/art_\w+\.html)"', r.html)
    # Leadership news
    leader_links = re.findall(r'href="(/syxwfb/art/\d{4}/art_\w+\.html)"', r.html)
    
    all_links = []
    for l in sp_links[:3]:
        all_links.append((f"https://www.mofcom.gov.cn{l}", 'spokesperson'))
    for l in daily_links[:3]:
        all_links.append((f"https://www.mofcom.gov.cn{l}", 'daily'))
    for l in leader_links[:2]:
        all_links.append((f"https://www.mofcom.gov.cn{l}", 'leadership'))
    
    for url, link_type in all_links:
        print(f"  Fetching {link_type}: {url}")
        ar = fetcher.fetch(url)
        if not ar or not ar.html:
            print(f"    FAILED")
            continue
        
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', ar.html, re.DOTALL)
        title = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip() if h1_match else "No title"
        
        date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', ar.html)
        date_str = f"{date_match.group(1)}-{int(date_match.group(2)):02d}-{int(date_match.group(3)):02d}" if date_match else "unknown"
        
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', ar.html, re.DOTALL)
        body = '\n'.join(re.sub(r'<[^>]+>', '', p).strip() for p in paragraphs if re.sub(r'<[^>]+>', '', p).strip())
        
        print(f"    Title: {title}")
        print(f"    Date: {date_str}")
        print(f"    Body length: {len(body)} chars")
        results.append({
            'source': 'MOFCOM',
            'type': link_type,
            'title': title,
            'date': date_str,
            'url': url,
            'body': body[:3000],
            'body_len': len(body)
        })
    
    return results

def fetch_jhsjk():
    """Fetch JHSJK (Xi Jinping speeches database)"""
    print("\n=== FETCHING JHSJK ===")
    r = fetcher.fetch('https://jhsjk.people.cn/')
    if not r or not r.html:
        print("JHSJK homepage: FAILED")
        return []
    
    print(f"JHSJK homepage: {len(r.html)} chars")
    
    results = []
    ids = list(set(re.findall(r'article/(\d+)', r.html)))
    
    for aid in ids[:5]:
        url = f"https://jhsjk.people.cn/article/{aid}"
        print(f"  Fetching article: {url}")
        ar = fetcher.fetch(url)
        if not ar or not ar.html:
            print(f"    FAILED")
            continue
        
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', ar.html, re.DOTALL)
        title = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip() if h1_match else "No title"
        
        date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', ar.html)
        date_str = f"{date_match.group(1)}-{int(date_match.group(2)):02d}-{int(date_match.group(3)):02d}" if date_match else "unknown"
        
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', ar.html, re.DOTALL)
        body = '\n'.join(re.sub(r'<[^>]+>', '', p).strip() for p in paragraphs if re.sub(r'<[^>]+>', '', p).strip())
        
        print(f"    Title: {title}")
        print(f"    Date: {date_str}")
        print(f"    Body length: {len(body)} chars")
        results.append({
            'source': 'JHSJK',
            'type': 'xi_speech',
            'title': title,
            'date': date_str,
            'url': url,
            'body': body[:3000],
            'body_len': len(body)
        })
    
    return results

def fetch_govcn():
    """Fetch gov.cn for latest policy docs"""
    print("\n=== FETCHING GOV.CN ===")
    r = fetcher.fetch('https://www.gov.cn/zhengce/')
    if not r or not r.html:
        print("gov.cn/zhengce/: FAILED")
        return []
    
    print(f"gov.cn/zhengce/: {len(r.html)} chars")
    
    results = []
    links = re.findall(r'href="(\.\/\d{6}/content_\d+\.htm)"', r.html)
    
    for l in links[:5]:
        url = l.replace('./', 'https://www.gov.cn/zhengce/')
        print(f"  Fetching: {url}")
        ar = fetcher.fetch(url)
        if not ar or not ar.html:
            print(f"    FAILED")
            continue
        
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', ar.html, re.DOTALL)
        title = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip() if h1_match else "No title"
        # Clean title
        title = re.sub(r'_中国政府网$', '', title).strip()
        
        date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', ar.html)
        date_str = f"{date_match.group(1)}-{int(date_match.group(2)):02d}-{int(date_match.group(3)):02d}" if date_match else "unknown"
        
        doc_num_match = re.search(r'国[务办]发〔\d{4}〕\d+号', ar.html)
        doc_num = doc_num_match.group(0) if doc_num_match else ""
        
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', ar.html, re.DOTALL)
        body = '\n'.join(re.sub(r'<[^>]+>', '', p).strip() for p in paragraphs if re.sub(r'<[^>]+>', '', p).strip())
        
        print(f"    Title: {title}")
        print(f"    Date: {date_str}")
        print(f"    Doc#: {doc_num}")
        print(f"    Body length: {len(body)} chars")
        results.append({
            'source': 'gov.cn',
            'type': 'policy',
            'title': title,
            'date': date_str,
            'doc_number': doc_num,
            'url': url,
            'body': body[:3000],
            'body_len': len(body)
        })
    
    return results

if __name__ == '__main__':
    all_results = []
    all_results.extend(fetch_mfa())
    all_results.extend(fetch_mofcom())
    all_results.extend(fetch_jhsjk())
    all_results.extend(fetch_govcn())
    
    print("\n\n==============================")
    print("ALL RESULTS SUMMARY")
    print("==============================")
    for r in all_results:
        print(f"\n[{r['source']}] {r['title']}")
        print(f"  Date: {r['date']} | Type: {r['type']} | Body: {r['body_len']} chars")
        print(f"  URL: {r['url']}")
        if r.get('doc_number'):
            print(f"  Doc#: {r['doc_number']}")
        # Print first 500 chars of body
        if r['body']:
            print(f"  Preview: {r['body'][:500]}...")

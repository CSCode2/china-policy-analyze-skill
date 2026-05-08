#!/usr/bin/env python3
"""
MFA Geopolitical Risk Monitor Script
Extracts latest MFA article links for risk observation generation.
"""

import re
import json
from datetime import datetime
from china_policy_skill.fetch.fetch_html import HTMLFetcher

def main():
    # Initialize fetcher
    fetcher = HTMLFetcher()
    
    # Fetch MFA homepage
    print("Fetching MFA homepage...")
    try:
        html = fetcher.fetch("https://www.mfa.gov.cn/").text
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return
    
    # Clean HTML for regex matching
    html = html.replace('\r', '').replace('\n', ' ').replace('\t', ' ')
    
    # Extract article links using regex patterns
    patterns = {
        'spokesperson': r'href="(\./fyrbt_673021/\d{6}/t\d+_\d+\.shtml)"',
        'ministry_news': r'href="(\./wjbxw_new/\d{6}/t\d+_\d+\.shtml)"',
        'important_news': r'href="(\./zyxw/\d{6}/t\d+_\d+\.shtml)"',
        'leadership_activities': r'href="(\./wjbzhd/\d{6}/t\d+_\d+\.shtml)"'
    }
    
    found_links = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, html)
        # Remove the ./ prefix and build full URL
        full_urls = []
        for match in matches:
            url = match.replace('./', 'https://www.mfa.gov.cn/')
            full_urls.append(url)
        if full_urls:
            found_links[key] = full_urls
    
    # Also extract article IDs from JHSJK for leader-to-leader calls
    print("Fetching JHSJK homepage for leader calls...")
    try:
        jhsjk_html = fetcher.fetch("https://jhsjk.people.cn/")
        # Extract article IDs
        ids = re.findall(r'href="/article/(\d+)"', jhsjk_html)
        unique_ids = list(set(ids))[:10]  # Take up to 10 unique IDs
        jhsjk_articles = [f"https://jhsjk.people.cn/article/{aid}" for aid in unique_ids]
        found_links['jhsjk_leader_calls'] = jhsjk_articles
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return
    
    # Output results
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "spokesperson_links": found_links.get('spokesperson', []),
        "ministry_news_links": found_links.get('ministry_news', []),
        "important_news_links": found_links.get('important_news', []),
        "leadership_activity_links": found_links.get('leadership_activities', []),
        "jhsjk_leader_call_links": found_links.get('jhsjk_leader_calls', [])
    }
    
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
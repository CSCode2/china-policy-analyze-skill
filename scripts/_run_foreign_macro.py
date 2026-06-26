#!/usr/bin/env python3
"""Foreign macro policy source fetcher.

Fetches latest press releases / policy statements from foreign central banks
and government sources that have different HTML structures than Chinese
government sites. Saves results as markdown reports for the Hermes agent
to review and create PRs.

Works alongside _run_daily_update.py (Chinese sources) — does NOT share
the same crawler because foreign sites need different link extraction logic.
"""

import json
import os
import re
import sys
import time
from datetime import datetime, date, timedelta
from urllib.parse import urljoin

from china_policy_skill.fetch.fetch_html import HTMLFetcher

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORT_DIR = os.path.join(REPO_ROOT, "reports")
HASH_STORE = os.path.join(REPO_ROOT, "corpus", "metadata", "hash_store.json")

fetcher = HTMLFetcher(timeout=12, rate_limit_delay=0.5)

# Each source: (name, url, link_pattern, title_group_index)
# link_pattern is a regex with a capture group for the URL path
FOREIGN_SOURCES = [
    {
        "name": "美国财政部",
        "url": "https://home.treasury.gov/news/press-releases",
        "link_regex": r'href="(/news/press-releases/[a-z]{2}\d+)"[^>]*>\s*([^<]{15,})',
        "base": "https://home.treasury.gov",
        "max_links": 5,
    },
    {
        "name": "美联储",
        "url": "https://www.federalreserve.gov/newsevents/pressreleases/2026-press.htm",
        "link_regex": r'href="(/newsevents/pressreleases/\w+\d+[a-z]?\.htm)"',
        "base": "https://www.federalreserve.gov",
        "title_from_url": True,
        "max_links": 5,
    },
    {
        "name": "美国联邦公报",
        "url": "https://www.federalregister.gov/api/v1/documents.json?per_page=5&order=newest&conditions[agencies][]=treasury-department",
        "is_json": True,
        "is_api": True,
        "max_links": 3,
    },
    {
        "name": "日本银行",
        "url": "https://www.boj.or.jp/en/about/press/index.htm",
        "link_regex": r'href="(/en/about/press/koen_\d+/ko\d+[a-z]\.htm)"',
        "base": "https://www.boj.or.jp",
        "max_links": 3,
    },
    {
        "name": "日本银行货币政策决定",
        "url": "https://www.boj.or.jp/en/mopo/mpmdeci/index.htm",
        "link_regex": r'href="(/en/mopo/mpmdeci/\d+/k\d+[a-z]\.htm)"',
        "base": "https://www.boj.or.jp",
        "max_links": 3,
    },
]


def _is_duplicate(url: str) -> bool:
    from china_policy_skill.utils.hashing import content_hash, is_duplicate
    h = content_hash(url)
    return is_duplicate(h, HASH_STORE)


def _record_hash(url: str, doc_id: str):
    from china_policy_skill.utils.hashing import content_hash, record_hash
    h = content_hash(url)
    record_hash(h, doc_id, HASH_STORE)


def fetch_treasury(source):
    """US Treasury press releases."""
    result = fetcher.fetch(source["url"])
    if result.error:
        return [], f"Treasury error: {result.error}"
    html = result.html or ""
    matches = re.findall(source["link_regex"], html)
    items = []
    seen = set()
    for url_path, title in matches:
        full_url = urljoin(source["base"], url_path)
        if full_url in seen or _is_duplicate(full_url):
            continue
        seen.add(full_url)
        items.append((title.strip(), full_url, source["name"]))
        if len(items) >= source["max_links"]:
            break
    return items, None


def fetch_fedreserve(source):
    """Federal Reserve press releases."""
    result = fetcher.fetch(source["url"])
    if result.error:
        return [], f"Fed error: {result.error}"
    html = result.html or ""
    links = re.findall(source["link_regex"], html)
    items = []
    seen = set()
    for url_path in links:
        full_url = urljoin(source["base"], url_path)
        if full_url in seen or _is_duplicate(full_url):
            continue
        seen.add(full_url)
        title = url_path.split("/")[-1].replace(".htm", "").replace("-", " ")
        items.append((title, full_url, source["name"]))
        if len(items) >= source["max_links"]:
            break
    return items, None


def fetch_fedregister(source):
    """Federal Register JSON API."""
    import urllib.request
    url = source["url"]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            html = resp.read().decode("utf-8")
    except Exception as e:
        return [], f"FedRegister error: {e}"
    try:
        data = json.loads(html)
    except json.JSONDecodeError:
        return [], "FedRegister: not JSON"
    items = []
    for doc in data.get("results", [])[:source["max_links"]]:
        title = doc.get("title", "")
        url = doc.get("html_url", "")
        if url and not _is_duplicate(url):
            items.append((title, url, source["name"]))
    return items, None


def fetch_boj(source):
    """Bank of Japan press releases."""
    result = fetcher.fetch(source["url"])
    if result.error:
        return [], f"BOJ error: {result.error}"
    html = result.html or ""
    links = re.findall(source["link_regex"], html)
    items = []
    seen = set()
    for url_path in links:
        full_url = urljoin(source["base"], url_path)
        if full_url in seen or _is_duplicate(full_url):
            continue
        seen.add(full_url)
        filename = url_path.split("/")[-1].replace(".htm", "")
        items.append((f"BOJ {filename}", full_url, source["name"]))
        if len(items) >= source["max_links"]:
            break
    return items, None


FETCHERS = {
    "美国财政部": fetch_treasury,
    "美联储": fetch_fedreserve,
    "美国联邦公报": fetch_fedregister,
    "日本银行": fetch_boj,
    "日本银行货币政策决定": fetch_boj,
}


def fetch_article_content(url, title, source_name):
    """Fetch article content and extract text + real title."""
    result = fetcher.fetch(url)
    if result.error:
        return None, None, result.error
    html = result.html or ""

    from china_policy_skill.parse.html_to_md import HTMLToMarkdown
    from lxml import html as lxml_html

    real_title = title
    tree = lxml_html.fromstring(html)
    og_title = tree.xpath("//meta[@property='og:title']/@content")
    if og_title and og_title[0].strip():
        real_title = og_title[0].strip()
    else:
        for title_tag in tree.xpath("//title/text()"):
            t = title_tag.strip()
            if t and len(t) > 10:
                real_title = t.split("|")[0].split(" - ")[0].strip()
                break

    md_text = ""
    parser_inst = HTMLToMarkdown()
    md_text = parser_inst.convert(html, url)

    if len(md_text) < 200:
        paragraphs = tree.xpath("//p//text()")
        para_text = "\n\n".join(p.strip() for p in paragraphs if p.strip() and len(p.strip()) > 20)
        if len(para_text) > 200:
            md_text = f"Source: {url}\n\n{real_title}\n\n{para_text}"

    if len(md_text) < 150:
        return None, None, "too short"
    return md_text, real_title, None


def main():
    from china_policy_skill.utils.hashing import content_hash, is_duplicate, record_hash

    print("=== Foreign Macro Policy Update ===")
    print(f"Time: {datetime.now().isoformat()}")

    cutoff = date.today() - timedelta(days=7)
    all_items = []
    errors = []

    for source in FOREIGN_SOURCES:
        name = source["name"]
        fetcher_func = FETCHERS.get(name)
        if not fetcher_func:
            continue
        print(f"\n  Fetching: {name}...")
        items, error = fetcher_func(source)
        if error:
            print(f"    ERROR: {error}")
            errors.append({"source": name, "error": error})
            continue
        print(f"    Found {len(items)} new items")
        for title, url, src in items:
            all_items.append((title, url, src))

    print(f"\n  Total new items: {len(all_items)}")

    if not all_items:
        print("\n=== No new foreign macro items ===")
        return

    # Fetch content for each item
    docs = []
    for title, url, src in all_items[:10]:
        print(f"  Fetching content: {title[:60]}...")
        md_text, real_title, error = fetch_article_content(url, title, src)
        if error:
            print(f"    SKIP: {error}")
            errors.append({"source": src, "url": url, "error": error})
            continue

        h = content_hash(url)
        doc_id = f"fmac_{h[:12]}"

        raw_path = os.path.join(REPO_ROOT, "corpus", "raw", f"{doc_id}.html")
        md_dir = os.path.join(REPO_ROOT, "corpus", "processed", "markdown")
        os.makedirs(md_dir, exist_ok=True)
        md_path = os.path.join(md_dir, f"{doc_id}.md")
        meta_dir = os.path.join(REPO_ROOT, "corpus", "metadata")
        meta_path = os.path.join(meta_dir, f"{doc_id}.json")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_text)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "doc_id": doc_id,
                "title": real_title,
                "source_name": src,
                "publish_date": "",
                "url": url,
                "authority_level": "FP-E",
                "doc_type": "foreign_macro",
                "content_hash": h,
            }, f, ensure_ascii=False, indent=2)

        record_hash(h, doc_id, HASH_STORE)
        docs.append({"title": real_title, "url": url, "source": src, "chars": len(md_text)})
        print(f"    OK: {real_title[:60]} ({len(md_text)} chars)")

    # Generate report
    today_str = date.today().isoformat()
    report_path = os.path.join(REPORT_DIR, f"foreign_macro_{today_str}.md")

    lines = [f"# Foreign Macro Policy Update — {today_str}\n"]
    lines.append(f"## Summary\n")
    lines.append(f"- **New Items**: {len(docs)}")
    lines.append(f"- **Errors**: {len(errors)}\n")

    if docs:
        lines.append("## New Items\n")
        for d in docs:
            lines.append(f"- **{d['title']}** ({d['source']}) — [{d['url'][:80]}]({d['url']})")
        lines.append("")

    if errors:
        lines.append("## Errors\n")
        for e in errors:
            lines.append(f"- {e.get('source','')}: {e.get('error','')}")

    lines.append(f"\n---\n*Generated at {datetime.now().isoformat()}*")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n=== Done. {len(docs)} items saved. Report: {report_path} ===")


if __name__ == "__main__":
    main()

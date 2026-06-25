#!/usr/bin/env python3
"""Local policy watcher for Chinese city government sources.

Crawls city government websites in rotating batches (10 per day, 4-day cycle)
and also checks 本地宝 (bendibao.com) as an E-level discovery lead.
All 本地宝 findings must be verified against official government sources.
"""

import json
import os
import re
import sys
import time
from datetime import datetime, date, timedelta
from urllib.parse import urljoin, urlparse

from china_policy_skill.fetch.fetch_html import HTMLFetcher
from china_policy_skill.parse.html_to_md import HTMLToMarkdown
from china_policy_skill.utils.hashing import content_hash, is_duplicate, record_hash
from lxml import etree

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORT_DIR = os.path.join(REPO_ROOT, "reports")
HASH_STORE = os.path.join(REPO_ROOT, "corpus", "metadata", "hash_store.json")

CITY_SOURCES = [
    ("北京", "https://www.beijing.gov.cn/zhengce/"),
    ("上海", "https://www.shanghai.gov.cn"),
    ("天津", "https://www.tj.gov.cn/zwgk/"),
    ("重庆", "https://www.cq.gov.cn/zwgk/zfxxgkml/szfwj/"),
    ("深圳", "https://www.sz.gov.cn/cn/xxgk/zfxxgj/tzgg/index.html"),
    ("广州", "https://www.gz.gov.cn/zwgk/zfwj/"),
    ("成都", "https://www.chengdu.gov.cn/"),
    ("杭州", "https://www.hangzhou.gov.cn"),
    ("武汉", "https://www.wuhan.gov.cn/zwgk_57/xxgk/xxgkml/szfwj/"),
    ("南京", "https://www.nanjing.gov.cn"),
    ("苏州", "https://www.suzhou.gov.cn/szsrmzf/zfwj/"),
    ("青岛", "https://www.qingdao.gov.cn/zwgk/zfwj/szfwj/"),
    ("厦门", "https://www.xm.gov.cn/zwgk/zfwj/"),
    ("大连", "https://www.dl.gov.cn/col/col45293/index.html"),
    ("宁波", "https://www.ningbo.gov.cn/col/col1229096905/index.html"),
    ("济南", "https://www.jinan.gov.cn/col/col39/index.html"),
    ("沈阳", "https://www.shenyang.gov.cn/zwgk/zfgb/"),
    ("无锡", "https://www.wuxi.gov.cn/zwgk/zfwj/szfwj/"),
    ("珠海", "https://www.zhuhai.gov.cn/zwgk/zfwj/"),
    ("东莞", "https://www.dg.gov.cn/zwgk/zfwj/"),
    ("佛山", "https://www.foshan.gov.cn/zwgk/zfwj/szfbgtwj/"),
    ("温州", "https://www.wenzhou.gov.cn/col/col1229455060/index.html"),
    ("石家庄", "https://www.sjz.gov.cn/columns/6055140e-a315-47cc-b985-8ae22c26d4b8/"),
    ("太原", "https://www.taiyuan.gov.cn/zwgk/zfxxgkml/szfbgtwj/"),
    ("呼和浩特", "https://www.huhhot.gov.cn/zwgknew/fdzdgknr/zdlyxx/"),
    ("长春", "http://www.changchun.gov.cn/zwgk/szfwj/"),
    ("哈尔滨", "https://www.harbin.gov.cn/zwgk/szfzwgk/"),
    ("福州", "https://www.fuzhou.gov.cn/zwgk/zfwj/szfwj/"),
    ("南昌", "https://www.nc.gov.cn/ncszf/xxgknl/"),
    ("南宁", "https://www.nanning.gov.cn/zwgk/zfwj/szfwj/"),
    ("海口", "https://www.haikou.gov.cn/zwgk/zfwj/"),
    ("贵阳", "https://www.guiyang.gov.cn/zwgk/zfwj/"),
    ("昆明", "https://www.km.gov.cn/zwgk/zfwj/"),
    ("拉萨", "https://www.lasa.gov.cn/zwgk/zfwj/"),
    ("西安", "https://www.xa.gov.cn/zwgk/zfwj/"),
    ("兰州", "https://www.lanzhou.gov.cn/zwgk/zfwj/"),
    ("西宁", "https://www.xining.gov.cn/zwgk/zfwj/"),
    ("银川", "https://www.yinchuan.gov.cn/zwgk/zfwj/"),
    ("乌鲁木齐", "https://www.wlmq.gov.cn/wlmqs/c119066/zfxxgk_xxgkzn.shtml"),
    ("香港", "https://www.gov.hk/tc/about/govdirectory/govwebsites.htm"),
    ("澳门", "https://www.gov.mo/zh-hant/"),
]

BATCH_SIZE = 10
CYCLE_DAYS = 4


def get_today_batch():
    """Get today's batch of cities based on day-of-year rotation."""
    day_of_year = date.today().timetuple().tm_yday
    batch_index = (day_of_year % CYCLE_DAYS)
    start = batch_index * BATCH_SIZE
    end = start + BATCH_SIZE
    return CITY_SOURCES[start:end]


def fetch_city_listings(cities):
    """Fetch listing pages for a batch of cities."""
    fetcher = HTMLFetcher(timeout=10, rate_limit_delay=0.3)
    all_urls = []
    cutoff = date.today() - timedelta(days=7)

    for city_name, listing_url in cities:
        print(f"  Fetching: {city_name} ({listing_url})")
        result = fetcher.fetch(listing_url)
        if result.error:
            print(f"    ERROR: {result.error}")
            continue

        html = result.html or ""
        if len(html) > 500000:
            html = html[:500000]

        try:
            parser = etree.HTMLParser(encoding="utf-8")
            tree = etree.fromstring(html.encode("utf-8"), parser)
            parsed = urlparse(listing_url)
            base = f"{parsed.scheme}://{parsed.netloc}"

            link_count = 0
            for li in tree.xpath("//li"):
                if link_count >= 10:
                    break
                a_el = li.xpath(".//a[@href]")
                if not a_el:
                    continue
                a_el = a_el[0]
                href = a_el.get("href", "")
                text = (a_el.text or "").strip()
                if not text or len(text) < 5:
                    continue

                if href.startswith("/"):
                    href = f"{base}{href}"
                elif not href.startswith("http"):
                    href = urljoin(listing_url, href)

                is_doc = (
                    "/content" in href
                    or "/art/" in href
                    or ".shtml" in href
                    or ".html" in href
                    or ".htm" in href
                    or "/info/" in href
                    or "/xxgk" in href
                    or "/zfwj" in href
                )

                same_site = parsed.netloc in href or href.startswith("/")
                if not (is_doc and same_site):
                    continue

                link_date = None
                for span in li.xpath(".//span"):
                    span_text = (span.text or "").strip()
                    if span_text and len(span_text) >= 8:
                        try:
                            link_date = datetime.strptime(span_text[:10], "%Y-%m-%d").date()
                            break
                        except ValueError:
                            pass

                if link_date and link_date < cutoff:
                    continue

                all_urls.append((text, href, city_name, link_date))
                link_count += 1
        except Exception as e:
            print(f"    Parse error: {e}")

    print(f"  Found {len(all_urls)} document URLs from cities")
    return all_urls


def fetch_and_process(docs):
    """Fetch and process document content."""
    fetcher = HTMLFetcher(timeout=10, rate_limit_delay=0.3)
    parser = HTMLToMarkdown()
    new_docs = []
    deadline = time.time() + 60

    for title, url, city, link_date in docs[:10]:
        if time.time() > deadline:
            break
        h = content_hash(url)
        if is_duplicate(h, HASH_STORE):
            continue

        print(f"  Fetching ({city}): {title[:50]}...")
        result = fetcher.fetch(url)
        if result.error:
            print(f"    ERROR: {result.error}")
            continue

        md_text = parser.convert(result.html or "", url)
        if len(md_text) < 200:
            print(f"    SKIP: too short")
            continue

        doc_id = f"local_{h[:12]}"
        doc_meta = {
            "doc_id": doc_id,
            "title": title,
            "source_name": f"{city}市政府",
            "publish_date": link_date.strftime("%Y-%m-%d") if link_date else "",
            "url": url,
            "authority_level": "B",
            "doc_type": "地方政策",
            "content_hash": h,
        }

        md_path = os.path.join(REPO_ROOT, "corpus", "processed", "markdown", f"{doc_id}.md")
        meta_path = os.path.join(REPO_ROOT, "corpus", "metadata", f"{doc_id}.json")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_text)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(doc_meta, f, ensure_ascii=False, indent=2)

        record_hash(h, doc_id, HASH_STORE)
        new_docs.append(doc_meta)
        print(f"    OK: {len(md_text)} chars")

    print(f"  Processed {len(new_docs)} new documents")
    return new_docs


def main():
    print("=== Local Policy Watch ===")
    print(f"Time: {datetime.now().isoformat()}")

    batch = get_today_batch()
    print(f"\n[1/2] Fetching city listings (batch: {len(batch)} cities)...")
    doc_urls = fetch_city_listings(batch)

    print(f"\n[2/2] Fetching and processing documents...")
    new_docs = fetch_and_process(doc_urls)

    today_str = date.today().isoformat()
    report_path = os.path.join(REPORT_DIR, f"local_policy_{today_str}.md")

    lines = [f"# Local Policy Watch — {today_str}\n"]
    lines.append("## Summary\n")
    lines.append(f"- **New Documents**: {len(new_docs)}")
    cities_checked = [c[0] for c in batch]
    lines.append(f"- **Cities Checked**: {', '.join(cities_checked)}\n")

    if new_docs:
        lines.append("## New Documents\n")
        for d in new_docs:
            lines.append(f"- **{d['title']}** ({d.get('publish_date','日期不详')}) — {d['source_name']} [Link]({d['url']})")
        lines.append("")
    else:
        lines.append("No new local policy documents found in this batch.\n")

    lines.append("\n---\n")
    lines.append(f"*本报告由地方政策监控器自动生成 at {datetime.now().isoformat()}*")
    lines.append(f"\n注意：本地宝(bendibao.com)为E级线索源，所有信息需回查政府官网验证后才能引用。")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n=== Done. {len(new_docs)} documents. Report: {report_path} ===")


if __name__ == "__main__":
    main()

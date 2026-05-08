import json
import os
import sys
import glob
import time
from datetime import datetime, date, timedelta

import yaml

from china_policy_skill.fetch.fetch_html import HTMLFetcher
from china_policy_skill.parse.html_to_md import HTMLToMarkdown
from china_policy_skill.parse.extract_metadata import MetadataExtractor
from china_policy_skill.parse.normalize_text import TextNormalizer
from china_policy_skill.utils.hashing import content_hash, is_duplicate, record_hash
from china_policy_skill.report.daily_update import DailyUpdateGenerator

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

LISTING_URLS = [
    ("gov.cn", "https://www.gov.cn/zhengce/"),
    ("ndrc", "https://www.ndrc.gov.cn/xwdt/xwfb/"),
    ("mofcom", "https://www.mofcom.gov.cn/xwfb/"),
    ("miit", "https://www.miit.gov.cn/"),
    ("moj", "https://www.moj.gov.cn/"),
    ("court", "https://www.court.gov.cn/"),
    ("spp", "https://www.spp.gov.cn/"),
    ("samr", "https://www.samr.gov.cn/"),
    ("mee", "https://www.mee.gov.cn/"),
    ("mfa", "https://www.mfa.gov.cn/wjbxw/"),
    ("stats", "https://www.stats.gov.cn/sj/zxfb/"),
    ("nfra", "https://www.nfra.gov.cn/"),
    ("csrc", "https://www.csrc.gov.cn/csrc/c100032/"),
    ("pbc", "https://www.pbc.gov.cn/"),
    ("jhsjk", "http://jhsjk.people.cn"),
    ("mof", "https://www.mof.gov.cn/"),
    ("mot", "https://www.mot.gov.cn/"),
    ("mca", "https://www.mca.gov.cn/"),
    ("mnr", "https://www.mnr.gov.cn/"),
    ("moa", "https://www.moa.gov.cn/"),
    ("nhc", "https://www.nhc.gov.cn/"),
    ("nhsa", "https://www.nhsa.gov.cn/"),
    ("nea", "https://www.nea.gov.cn/"),
    ("chinatax", "https://www.chinatax.gov.cn/"),
    ("mem", "https://www.mem.gov.cn/"),
    ("safe", "https://www.safe.gov.cn/"),
    ("moe", "https://www.moe.gov.cn/"),
    ("mct", "https://www.mct.gov.cn/"),
    ("mohurd", "https://www.mohurd.gov.cn/"),
    ("mva", "https://www.mva.gov.cn/"),
    ("audit", "https://www.audit.gov.cn/"),
    ("nea", "https://www.nea.gov.cn/"),
    ("nda", "https://www.nda.gov.cn/"),
    ("scio", "https://www.scio.gov.cn/"),
]

SKIP_SOURCES = {"customs.gov.cn", "mps.gov.cn", "most.gov.cn", "mohrss.gov.cn", "jhsjk.org.cn", "jhsjk.people.cn", "scio.gov.cn", "mohurd.gov.cn"}

HASH_STORE = os.path.join(REPO_ROOT, "corpus", "metadata", "hash_store.json")

MAX_DOCS = int(os.environ.get("CPI_MAX_DOCS", "20"))


def _ensure_dirs():
    for d in [
        "corpus/raw",
        "corpus/processed/markdown",
        "corpus/processed/text",
        "corpus/metadata",
        "reports",
    ]:
        os.makedirs(os.path.join(REPO_ROOT, d), exist_ok=True)


def _log_fetch_error(source: str, url: str, message: str):
    error_log_dir = os.path.join(REPO_ROOT, "corpus", "metadata")
    os.makedirs(error_log_dir, exist_ok=True)
    error_log = os.path.join(error_log_dir, "fetch_errors.jsonl")
    entry = {
        "source": source,
        "url": url,
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }
    with open(error_log, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def fetch_list_pages():
    html_fetcher = HTMLFetcher(timeout=8, rate_limit_delay=0.3)
    doc_urls = []
    deadline = time.time() + 80
    recent_cutoff = date.today() - timedelta(days=3)

    for source_name, source_url in LISTING_URLS:
        if time.time() > deadline:
            print(f"  ⏰ Time limit reached, skipping remaining sources")
            break
        if any(skip in source_url for skip in SKIP_SOURCES):
            continue
        print(f"  Fetching listing page: {source_name} ({source_url})")
        result = html_fetcher.fetch(source_url)
        if result.error:
            print(f"    ERROR: {result.error}")
            _log_fetch_error(source_name, source_url, result.error)
            continue

        from lxml import etree
        from urllib.parse import urljoin, urlparse

        try:
            html_content = result.html or ""
            if len(html_content) > 500000:
                print(f"    Large page ({len(html_content)} chars), truncating for link extraction")
                html_content = html_content[:500000]
            parser = etree.HTMLParser(encoding="utf-8")
            tree = etree.fromstring(html_content.encode("utf-8"), parser)
            parsed_base = urlparse(source_url)
            base = f"{parsed_base.scheme}://{parsed_base.netloc}"

            link_count = 0
            for li in tree.xpath("//li"):
                if link_count >= 200:
                    break
                
                a_el = li.xpath(".//a[@href]")
                if not a_el:
                    continue
                a_el = a_el[0]
                
                href = a_el.get("href", "")
                text = (a_el.text or "").strip()
                if not text or len(text) < 5:
                    continue
                    
                if href.startswith("./"):
                    href = urljoin(source_url, href)
                elif href.startswith("/"):
                    href = f"{base}{href}"
                elif not href.startswith("http"):
                    href = urljoin(source_url, href)

                is_article = (
                    "/content_" in href
                    or "/zhengce/content" in href
                    or "/xwdt/" in href
                    or "/art/" in href
                    or "/t20" in href
                    or ".shtml" in href
                    or "/content.shtml" in href
                    or "/pub/" in href
                    or "/zixun/" in href
                    or "/xwzx/" in href
                    or "/sj/zxfb/" in href
                    or "/ywdt/" in href
                    or "/xwfb/" in href
                    or "/wjbxw/" in href
                )

                same_site = parsed_base.netloc in href or href.startswith("/")
                if not (is_article and same_site):
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
                
                if link_date and link_date < recent_cutoff:
                    continue
                if not link_date:
                    continue
                
                doc_urls.append((text, href, source_name, link_date))
                link_count += 1
        except Exception as e:
            print(f"    Parse error: {e}")
            _log_fetch_error(source_name, source_url, str(e))

    print(f"  Found {len(doc_urls)} document URLs")
    return doc_urls


PUBLISH_DATE_CUTOFF_DAYS = 7

def fetch_and_process_docs(doc_urls):
    html_fetcher = HTMLFetcher(timeout=10, rate_limit_delay=0.3)
    html_parser = HTMLToMarkdown()
    meta_extractor = MetadataExtractor()
    text_normalizer = TextNormalizer()

    new_docs_metadata = []
    processed_count = 0
    deadline = time.time() + 40

    for item in doc_urls[:MAX_DOCS]:
        if time.time() > deadline:
            print(f"  ⏰ Time limit reached, stopping document processing")
            break
        
        if len(item) >= 4:
            title, url, source, link_date = item
        else:
            title, url, source = item[:3]
            link_date = None
            
        h = content_hash(url)
        if is_duplicate(h, HASH_STORE):
            continue

        date_str = link_date.strftime("%Y-%m-%d") if link_date else "日期未知"
        print(f"  Fetching document ({date_str}): {title[:50]}...")
        result = html_fetcher.fetch(url)
        if result.error:
            print(f"    ERROR: {result.error}")
            _log_fetch_error(source, url, result.error)
            continue

        md_text = html_parser.convert(result.html or "", url)
        if len(md_text) < 200:
            print(f"    SKIP: too short ({len(md_text)} chars)")
            continue

        meta = meta_extractor.extract(result.html or "", url)

        publish_cutoff = date.today() - timedelta(days=PUBLISH_DATE_CUTOFF_DAYS)
        if meta.publish_date:
            try:
                pub_dt = datetime.strptime(meta.publish_date[:10], "%Y-%m-%d").date()
                if pub_dt < publish_cutoff:
                    print(f"    SKIP: publish_date too old ({meta.publish_date}), cutoff={publish_cutoff}")
                    record_hash(h, f"skipped_old_{h[:12]}", HASH_STORE)
                    continue
            except ValueError:
                pass

        doc_id = f"doc_{h[:12]}"
        doc_meta = {
            "doc_id": doc_id,
            "title": meta.title or title,
            "source_name": source,
            "publish_date": meta.publish_date or "",
            "url": url,
            "authority_level": "S" if "gov.cn" in source else "A",
            "doc_type": meta.doc_type,
            "organization": meta.organization,
            "issuing_body": meta.issuing_body,
            "doc_number": meta.doc_number,
            "content_hash": h,
        }

        cleaned_text = text_normalizer.normalize(md_text)
        cleaned_text = text_normalizer.clean_noise(cleaned_text)

        raw_path = os.path.join(REPO_ROOT, "corpus", "raw", f"{doc_id}.html")
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(result.html or "")

        md_path = os.path.join(
            REPO_ROOT, "corpus", "processed", "markdown", f"{doc_id}.md"
        )
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        txt_path = os.path.join(
            REPO_ROOT, "corpus", "processed", "text", f"{doc_id}.txt"
        )
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        meta_path = os.path.join(
            REPO_ROOT, "corpus", "metadata", f"{doc_id}.json"
        )
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(doc_meta, f, ensure_ascii=False, indent=2)

        record_hash(h, doc_id, HASH_STORE)
        new_docs_metadata.append(doc_meta)
        processed_count += 1
        print(f"    OK: {len(cleaned_text)} chars")

    print(f"  Processed {processed_count} new documents")
    return new_docs_metadata


def generate_report(new_docs):
    gen = DailyUpdateGenerator()

    today_str = date.today().isoformat()
    errors = []
    error_log = os.path.join(REPO_ROOT, "corpus", "metadata", "fetch_errors.jsonl")
    if os.path.exists(error_log):
        with open(error_log, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        ts = entry.get("timestamp", "")
                        if ts.startswith(today_str):
                            errors.append(entry)
                    except json.JSONDecodeError:
                        pass

    report = gen.generate(new_docs, errors)

    today = datetime.now().strftime("%Y-%m-%d")
    report_dir = os.path.join(REPO_ROOT, "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"daily_{today}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"  Report: {report_path}")
    return report_path


def main():
    print("=== Daily Policy Update ===")
    print(f"Time: {datetime.now().isoformat()}")

    _ensure_dirs()

    print("\n[1/3] Fetching listing pages...")
    doc_urls = fetch_list_pages()

    print("\n[2/3] Fetching and processing documents...")
    new_docs = fetch_and_process_docs(doc_urls)

    print("\n[3/3] Generating daily report...")
    report_path = generate_report(new_docs)

    print(f"\n=== Done. New documents: {len(new_docs)} ===")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()

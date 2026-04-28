import json
import os
import sys
import glob
from datetime import datetime

from china_policy_skill.fetch.fetch_html import HTMLFetcher
from china_policy_skill.parse.html_to_md import HTMLToMarkdown
from china_policy_skill.parse.extract_metadata import MetadataExtractor
from china_policy_skill.parse.normalize_text import TextNormalizer
from china_policy_skill.utils.hashing import content_hash, is_duplicate, record_hash
from china_policy_skill.report.daily_update import DailyUpdateGenerator

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SOURCE_URLS = [
    "https://www.gov.cn/zhengce/",
    "https://www.ndrc.gov.cn",
    "http://jhsjk.people.cn",
]

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
    html_fetcher = HTMLFetcher(timeout=15, rate_limit_delay=1.0)
    doc_urls = []

    for source_url in SOURCE_URLS:
        print(f"  Fetching listing page: {source_url}")
        result = html_fetcher.fetch(source_url)
        if result.error:
            print(f"    ERROR: {result.error}")
            _log_fetch_error(source_url, source_url, result.error)
            continue

        from lxml import etree

        try:
            parser = etree.HTMLParser(encoding="utf-8")
            tree = etree.fromstring((result.html or "").encode("utf-8"), parser)
            for a_el in tree.xpath("//a[@href]"):
                href = a_el.get("href", "")
                text = (a_el.text or "").strip()
                if not text or len(text) < 5:
                    continue
                if href.startswith("./"):
                    from urllib.parse import urljoin
                    href = urljoin(source_url, href)
                elif href.startswith("/"):
                    from urllib.parse import urlparse

                    parsed = urlparse(source_url)
                    href = f"{parsed.scheme}://{parsed.netloc}{href}"
                if (
                    "/content_" in href
                    or "/zhengce/content" in href
                    or "/xwdt/" in href
                ):
                    doc_urls.append((text, href, source_url))
        except Exception as e:
            print(f"    Parse error: {e}")
            _log_fetch_error(source_url, source_url, str(e))

    print(f"  Found {len(doc_urls)} document URLs")
    return doc_urls


def fetch_and_process_docs(doc_urls):
    html_fetcher = HTMLFetcher(timeout=15, rate_limit_delay=1.0)
    html_parser = HTMLToMarkdown()
    meta_extractor = MetadataExtractor()
    text_normalizer = TextNormalizer()

    new_docs_metadata = []
    processed_count = 0

    for title, url, source in doc_urls[:MAX_DOCS]:
        h = content_hash(url)
        if is_duplicate(h, HASH_STORE):
            continue

        print(f"  Fetching document: {title[:50]}...")
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

    errors = []
    error_log = os.path.join(REPO_ROOT, "corpus", "metadata", "fetch_errors.jsonl")
    if os.path.exists(error_log):
        with open(error_log, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        errors.append(json.loads(line))
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

import re
from datetime import datetime, timedelta
from typing import Optional


def parse_chinese_date(text: str) -> Optional[datetime]:
    match = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日?", text)
    if match:
        try:
            return datetime(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
            )
        except ValueError:
            pass

    match = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月", text)
    if match:
        try:
            return datetime(int(match.group(1)), int(match.group(2)), 1)
        except ValueError:
            pass

    return None


def parse_iso_date(text: str) -> Optional[datetime]:
    patterns = [
        r"(\d{4})-(\d{1,2})-(\d{1,2})",
        r"(\d{4})/(\d{1,2})/(\d{1,2})",
        r"(\d{4})\.(\d{1,2})\.(\d{1,2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return datetime(
                    int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3)),
                )
            except ValueError:
                continue

    match = re.search(r"(\d{4})(\d{2})(\d{2})", text)
    if match:
        try:
            return datetime(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
            )
        except ValueError:
            pass

    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text.strip(), fmt)
        except ValueError:
            continue

    return None


def is_recent(date: datetime, days: int = 90) -> bool:
    cutoff = datetime.now() - timedelta(days=days)
    return date >= cutoff


def format_date(date: datetime, fmt: str = "%Y-%m-%d") -> str:
    return date.strftime(fmt)


def format_doc_citation(meta: dict) -> str:
    """Format a document reference with 《》, doc_number, date, issuing_body.

    Output examples:
      《关于新能源汽车车辆购置税政策的公告》（财税〔2026〕12号，2026年4月2日） — 财政部
      《道路机动车辆生产企业及产品》新批次公告（2026年3月28日）
      《十五五规划纲要》（2026年3月13日） — 国务院
    """
    title = meta.get("title", "Untitled")
    if "《" not in title:
        title = f"《{title}》"
    doc_number = meta.get("doc_number", "")
    publish_date = meta.get("publish_date", "")
    issuing_body = meta.get("issuing_body", meta.get("source_name", ""))

    if publish_date and len(publish_date) == 10 and "-" in publish_date:
        y, m, d = publish_date.split("-")
        date_display = f"{y}年{int(m)}月{int(d)}日"
    elif publish_date and publish_date != "Unknown":
        date_display = publish_date
    else:
        date_display = ""

    paren_parts: list[str] = []
    if doc_number:
        paren_parts.append(doc_number)
    if date_display:
        paren_parts.append(date_display)

    result = title
    if paren_parts:
        result += f"（{'，'.join(paren_parts)}）"
    if issuing_body:
        result += f" — {issuing_body}"
    return result

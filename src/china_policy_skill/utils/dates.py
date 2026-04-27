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

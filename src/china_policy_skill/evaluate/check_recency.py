from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from china_policy_skill.evaluate.run_eval import EvalResult


class RecencyChecker:
    def check(
        self,
        answer: str,
        sources: List[dict],
        max_age_days: int = 90,
    ) -> EvalResult:
        if not sources:
            return EvalResult(
                check_name="recency_check",
                passed=True,
                score=1.0,
                details="No sources to check recency",
            )

        now = datetime.now()
        cutoff = now - timedelta(days=max_age_days)
        stale_sources: List[dict] = []
        recent_count = 0
        total = 0

        for src in sources:
            date_str = src.get("publish_date", src.get("date", ""))
            if not date_str:
                stale_sources.append({"source": src.get("title", "Unknown"), "reason": "No date"})
                total += 1
                continue

            parsed = self._parse_date(date_str)
            if parsed is None:
                stale_sources.append({"source": src.get("title", "Unknown"), "reason": f"Unparseable date: {date_str}"})
                total += 1
                continue

            total += 1
            if parsed >= cutoff:
                recent_count += 1
            else:
                stale_sources.append({"source": src.get("title", "Unknown"), "date": date_str, "age_days": (now - parsed).days})

        score = recent_count / total if total > 0 else 1.0
        passed = score >= 0.8

        return EvalResult(
            check_name="recency_check",
            passed=passed,
            score=round(score, 3),
            details=f"{recent_count}/{total} sources within {max_age_days}-day window",
            items=stale_sources,
        )

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y年%m月%d日",
            "%Y.%m.%d",
            "%Y%m%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str[: len(datetime(2000, 1, 1).strftime(fmt))], fmt)
            except (ValueError, TypeError):
                continue
        try:
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            pass
        return None

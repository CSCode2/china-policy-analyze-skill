from __future__ import annotations

from typing import Dict, Tuple


_DOC_TYPE_PATTERNS: Dict[str, Tuple[str, ...]] = {
    "five_year_plan": (
        "五年规划",
        "五年计划",
        "国民经济和社会发展第",
        "五年规划纲要",
    ),
    "government_work_report": (
        "政府工作报告",
        "国务院政府工作报告",
    ),
    "decision_opinion_outline_plan": (
        "决定",
        "意见",
        "纲要",
        "若干意见",
    ),
    "implementation_plan": (
        "实施方案",
        "实施办法",
        "实施细则",
    ),
    "action_plan": (
        "行动计划",
        "行动方案",
        "专项行动",
    ),
    "notice": (
        "通知",
        "通报",
        "公告",
    ),
    "interpretation": (
        "解读",
        "政策解读",
        "答记者问",
        "释义",
    ),
    "news": (
        "新闻",
        "报道",
        "讯",
    ),
    "law": (
        "法",
        "法律",
    ),
    "regulation": (
        "条例",
        "规定",
        "办法",
        "行政法规",
    ),
    "judicial_interpretation": (
        "司法解释",
        "最高人民法院关于",
        "最高人民检察院关于",
    ),
    "typical_case": (
        "典型案例",
        "指导性案例",
        "案例",
    ),
    "enforcement_notice": (
        "执法通知",
        "执法公告",
        "责令",
        "行政处罚",
        "处罚决定",
    ),
}

_PRIORITY_ORDER = [
    "judicial_interpretation",
    "law",
    "five_year_plan",
    "government_work_report",
    "decision_opinion_outline_plan",
    "action_plan",
    "implementation_plan",
    "regulation",
    "enforcement_notice",
    "typical_case",
    "interpretation",
    "notice",
    "news",
]


class DocTypeClassifier:
    def classify(self, title: str, text: str = "") -> str:
        if not title:
            return "notice"
        combined = f"{title} {text}".strip()
        candidates: list[str] = []
        for doc_type in _PRIORITY_ORDER:
            patterns = _DOC_TYPE_PATTERNS[doc_type]
            for pattern in patterns:
                if pattern in combined:
                    candidates.append(doc_type)
                    break
        if not candidates:
            return "notice"
        return candidates[0]

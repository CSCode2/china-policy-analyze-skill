from __future__ import annotations

import re
from typing import List

from china_policy_skill.evaluate.run_eval import EvalResult


_SENSITIVE_NUMBER_PATTERNS = [
    re.compile(r"\d{2,}[,.]?\d*%"),
    re.compile(r"\d{4}年"),
    re.compile(r"\d+亿元|\d+万元|\d+万|\d+亿"),
]

_FUZZY_CLAIM_MARKERS = [
    "据说",
    "听说",
    "可能",
    "大概",
    "应该",
    "据说",
    "传闻",
    "传闻称",
    "allegedly",
    "reportedly",
    "supposedly",
]


class HallucinationChecker:
    def check(self, answer: str, sources: List[dict]) -> EvalResult:
        if not answer:
            return EvalResult(
                check_name="hallucination_check",
                passed=True,
                score=1.0,
                details="Empty answer",
            )

        source_texts: List[str] = []
        for src in sources:
            text = src.get("text", src.get("snippet", ""))
            if text:
                source_texts.append(text.lower())

        combined_source = " ".join(source_texts)

        sentences = re.split(r"[。！？.!?]\s*", answer)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return EvalResult(
                check_name="hallucination_check",
                passed=True,
                score=1.0,
                details="No verifiable sentences",
            )

        flagged: List[dict] = []
        verified = 0

        for sentence in sentences:
            if not sentence or len(sentence) < 5:
                continue

            has_fuzzy_claim = any(marker in sentence for marker in _FUZZY_CLAIM_MARKERS)
            if has_fuzzy_claim:
                flagged.append({"claim": sentence[:150], "reason": "Fuzzy/uncertain claim"})
                continue

            has_number = any(pat.search(sentence) for pat in _SENSITIVE_NUMBER_PATTERNS)
            if has_number:
                numbers = []
                for pat in _SENSITIVE_NUMBER_PATTERNS:
                    numbers.extend(pat.findall(sentence))
                number_backed = all(n.lower() in combined_source for n in numbers)
                if not number_backed:
                    flagged.append({"claim": sentence[:150], "reason": f"Number not found in sources: {numbers}"})
                    continue

            key_phrases = self._extract_key_phrases(sentence)
            if not key_phrases:
                verified += 1
                continue

            phrase_matches = sum(1 for p in key_phrases if p.lower() in combined_source)
            coverage = phrase_matches / len(key_phrases) if key_phrases else 1.0

            if coverage >= 0.4:
                verified += 1
            else:
                flagged.append({"claim": sentence[:150], "reason": f"Low source coverage: {coverage:.0%}"})

        score = verified / len(sentences) if sentences else 1.0
        passed = score >= 0.8

        return EvalResult(
            check_name="hallucination_check",
            passed=passed,
            score=round(score, 3),
            details=f"{verified}/{len(sentences)} sentences verified against sources",
            items=flagged,
        )

    def _extract_key_phrases(self, sentence: str) -> List[str]:
        stopwords = {"的", "了", "在", "是", "和", "与", "也", "都", "将", "于", "对", "等", "为", "中", "或", "其", "及", "这", "那", "有", "不"}
        words = re.findall(r"[\u4e00-\u9fff]{2,}|[a-zA-Z]{3,}", sentence)
        return [w for w in words if w not in stopwords]

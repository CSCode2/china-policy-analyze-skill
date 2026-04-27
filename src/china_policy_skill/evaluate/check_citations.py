from __future__ import annotations

import re
from typing import List

from china_policy_skill.evaluate.run_eval import EvalResult


class CitationChecker:
    def check(self, answer: str, sources: List[dict]) -> EvalResult:
        if not answer:
            return EvalResult(
                check_name="citation_check",
                passed=True,
                score=1.0,
                details="Empty answer, nothing to verify",
            )

        if not sources:
            return EvalResult(
                check_name="citation_check",
                passed=False,
                score=0.0,
                details="No sources provided for verification",
            )

        source_texts: List[str] = []
        source_titles: List[str] = []
        for src in sources:
            text = src.get("text", src.get("snippet", ""))
            if text:
                source_texts.append(text)
            title = src.get("title", "")
            if title:
                source_titles.append(title)

        combined_source = " ".join(source_texts).lower()
        combined_titles = " ".join(source_titles).lower()

        citation_pattern = re.compile(r"\[(\d+)\]|\[来源\d*\]|\[Source\d*\]|\【[\d]+】", re.IGNORECASE)
        citations = citation_pattern.findall(answer)

        sentences = re.split(r"[。！？.!?]\s*", answer)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return EvalResult(
                check_name="citation_check",
                passed=True,
                score=1.0,
                details="No verifiable claims in answer",
            )

        backed = 0
        unbacked_claims: List[dict] = []

        for sentence in sentences:
            is_backed = False
            stripped = re.sub(r"\[(\d+)\]|\【[\d]+】", "", sentence).strip()
            if not stripped:
                continue

            key_phrases = self._extract_key_phrases(stripped)
            matched_count = 0
            for phrase in key_phrases:
                if phrase.lower() in combined_source or phrase.lower() in combined_titles:
                    matched_count += 1

            if len(key_phrases) > 0 and matched_count / len(key_phrases) >= 0.5:
                is_backed = True
            elif self._has_citation_marker(sentence):
                is_backed = True

            if is_backed:
                backed += 1
            else:
                unbacked_claims.append({"claim": stripped[:100]})

        score = backed / len(sentences) if sentences else 1.0
        passed = score >= 0.8

        return EvalResult(
            check_name="citation_check",
            passed=passed,
            score=round(score, 3),
            details=f"{backed}/{len(sentences)} claims backed by sources",
            items=unbacked_claims,
        )

    def _extract_key_phrases(self, sentence: str) -> List[str]:
        stopwords = {"的", "了", "在", "是", "和", "与", "也", "都", "将", "于", "对", "等", "为", "中", "或", "其", "及", "the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to", "for", "of", "and", "or", "by"}
        words = re.findall(r"[\u4e00-\u9fff]{2,}|[a-zA-Z]{3,}", sentence)
        return [w for w in words if w not in stopwords]

    def _has_citation_marker(self, sentence: str) -> bool:
        return bool(re.search(r"\[\d+\]|\【[\d]+】|\[Source\d*\]|\[来源\d*\]", sentence, re.IGNORECASE))

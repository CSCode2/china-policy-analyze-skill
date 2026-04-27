from __future__ import annotations

import yaml
import re
from typing import Dict, List, Optional


_DEFAULT_LEXICON: Dict[str, dict] = {
    "必须": {"strength": 5, "explanation": "Mandatory requirement with no flexibility", "stage": "implementation"},
    "应当": {"strength": 4, "explanation": "Strong obligation, expected to be followed", "stage": "implementation"},
    "严禁": {"strength": 5, "explanation": "Strictly prohibited, no exceptions", "stage": "enforcement"},
    "不得": {"strength": 5, "explanation": "Must not, absolute prohibition", "stage": "enforcement"},
    "禁止": {"strength": 5, "explanation": "Prohibited", "stage": "enforcement"},
    "推进": {"strength": 3, "explanation": "Push forward, policy encouragement", "stage": "implementation"},
    "推动": {"strength": 3, "explanation": "Promote or drive forward", "stage": "planning"},
    "鼓励": {"strength": 2, "explanation": "Encouraged but not required", "stage": "guidance"},
    "支持": {"strength": 2, "explanation": "Supported, favorable policy", "stage": "guidance"},
    "引导": {"strength": 2, "explanation": "Guide or steer in a direction", "stage": "guidance"},
    "探索": {"strength": 1, "explanation": "Explore or trial, low commitment", "stage": "pilot"},
    "试点": {"strength": 1, "explanation": "Pilot program, limited scope", "stage": "pilot"},
    "研究": {"strength": 1, "explanation": "Under study, no action required yet", "stage": "research"},
    "加快": {"strength": 3, "explanation": "Accelerate, signals urgency", "stage": "implementation"},
    "深化": {"strength": 3, "explanation": "Deepen existing reform", "stage": "implementation"},
    "完善": {"strength": 3, "explanation": "Improve or perfect an existing system", "stage": "implementation"},
    "落实": {"strength": 4, "explanation": "Implement or carry out existing policy", "stage": "implementation"},
    "确保": {"strength": 4, "explanation": "Ensure, strong commitment to outcome", "stage": "implementation"},
    "力争": {"strength": 3, "explanation": "Strive to achieve, target-oriented", "stage": "planning"},
    "统筹": {"strength": 3, "explanation": "Coordinate across areas", "stage": "planning"},
    "规范": {"strength": 3, "explanation": "Standardize or regulate", "stage": "implementation"},
    "优化": {"strength": 3, "explanation": "Optimize, improve efficiency", "stage": "implementation"},
    "加强": {"strength": 3, "explanation": "Strengthen, increase emphasis", "stage": "implementation"},
    "积极": {"strength": 2, "explanation": "Actively pursue, positive tone", "stage": "guidance"},
    "稳妥": {"strength": 2, "explanation": "Prudent and steady approach", "stage": "guidance"},
    "有序": {"strength": 2, "explanation": "In an orderly manner", "stage": "planning"},
    "逐步": {"strength": 2, "explanation": "Step by step, gradual approach", "stage": "planning"},
    "依法": {"strength": 4, "explanation": "According to law, legal basis required", "stage": "implementation"},
    "严厉": {"strength": 5, "explanation": "Severe, strict enforcement", "stage": "enforcement"},
    "坚决": {"strength": 5, "explanation": "Resolute, no compromise", "stage": "enforcement"},
    "全面": {"strength": 3, "explanation": "Comprehensive, across all areas", "stage": "implementation"},
    "大力": {"strength": 3, "explanation": "Vigorously, high intensity", "stage": "implementation"},
    "着力": {"strength": 3, "explanation": "Focus efforts on", "stage": "implementation"},
    "切实": {"strength": 4, "explanation": "Earnestly, concrete action expected", "stage": "implementation"},
    "严格": {"strength": 4, "explanation": "Strict, rigorous enforcement", "stage": "enforcement"},
    "限期": {"strength": 5, "explanation": "Within a deadline, time-bound mandate", "stage": "enforcement"},
    "取缔": {"strength": 5, "explanation": "Ban and eliminate", "stage": "enforcement"},
    "制止": {"strength": 5, "explanation": "Stop or prevent", "stage": "enforcement"},
}

_RISK_TERMS = {"严禁", "禁止", "不得", "取缔", "制止", "严厉", "坚决", "限期", "严格"}
_OPPORTUNITY_TERMS = {"鼓励", "支持", "推进", "推动", "加快", "试点", "探索", "积极", "大力发展"}
_UNCERTAINTY_TERMS = {"研究", "探索", "试点", "研究制定", "视情况", "适时"}


class PolicyStrengthClassifier:
    def __init__(self, lexicon_path: Optional[str] = None) -> None:
        self._lexicon: Dict[str, dict] = dict(_DEFAULT_LEXICON)
        if lexicon_path:
            self._load_lexicon(lexicon_path)

    def _load_lexicon(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not data:
            return
        if isinstance(data, dict):
            for phrase, info in data.items():
                if isinstance(info, dict):
                    self._lexicon[phrase] = info

    def classify_language_strength(
        self,
        sentence: str,
        document_metadata: dict,
    ) -> dict:
        if not sentence:
            return self._empty_result()

        best_match: Optional[str] = None
        best_strength = 0
        all_matches: List[str] = []

        sorted_phrases = sorted(self._lexicon.keys(), key=len, reverse=True)
        for phrase in sorted_phrases:
            if phrase in sentence:
                all_matches.append(phrase)
                entry = self._lexicon[phrase]
                if entry["strength"] > best_strength:
                    best_match = phrase
                    best_strength = entry["strength"]

        if not best_match:
            return self._empty_result()

        entry = self._lexicon[best_match]
        risk_signals: List[str] = []
        opportunity_signals: List[str] = []
        uncertainties: List[str] = []

        for matched in all_matches:
            if matched in _RISK_TERMS:
                risk_signals.append(matched)
            if matched in _OPPORTUNITY_TERMS:
                opportunity_signals.append(matched)
            if matched in _UNCERTAINTY_TERMS:
                uncertainties.append(matched)

        doc_type = document_metadata.get("doc_type", "")
        authority = document_metadata.get("authority_level", "")
        adjusted_strength = self._adjust_strength(best_strength, doc_type, authority)

        return {
            "phrase": best_match,
            "strength_level": adjusted_strength,
            "plain_language_explanation": entry.get("explanation", ""),
            "implementation_stage": entry.get("stage", "unknown"),
            "risk_signal": risk_signals[0] if risk_signals else "",
            "opportunity_signal": opportunity_signals[0] if opportunity_signals else "",
            "uncertainty": uncertainties[0] if uncertainties else "",
        }

    def _adjust_strength(self, base_strength: int, doc_type: str, authority: str) -> int:
        adjusted = base_strength
        if authority in ("S", "A"):
            adjusted = min(5, adjusted + 0)
        elif authority in ("D", "E"):
            adjusted = max(1, adjusted - 1)
        if doc_type == "interpretation" or doc_type == "news":
            adjusted = max(1, adjusted - 1)
        if doc_type == "law" or doc_type == "regulation":
            adjusted = min(5, adjusted + 0)
        return adjusted

    def _empty_result(self) -> dict:
        return {
            "phrase": "",
            "strength_level": 0,
            "plain_language_explanation": "",
            "implementation_stage": "",
            "risk_signal": "",
            "opportunity_signal": "",
            "uncertainty": "",
        }

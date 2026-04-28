from __future__ import annotations

from datetime import datetime
from typing import List

from ..utils.dates import format_doc_citation


class PolicySignalCardGenerator:
    def generate(self, topic: str, documents: List[dict]) -> str:
        if not topic:
            return ""

        sections = [
            f"# Policy Signal: {topic}",
            "",
            "## Signal Summary",
            "",
        ]

        doc_count = len(documents)
        authority_dist: dict = {}
        doc_type_dist: dict = {}
        all_phrases: List[str] = []
        max_strength = 0
        latest_date = ""
        risk_signals: List[str] = []
        opportunity_signals: List[str] = []

        for doc in documents:
            authority = doc.get("authority_level", "Unknown")
            authority_dist[authority] = authority_dist.get(authority, 0) + 1

            doc_type = doc.get("doc_type", "Unknown")
            doc_type_dist[doc_type] = doc_type_dist.get(doc_type, 0) + 1

            for phrase_info in doc.get("policy_phrases", []):
                if isinstance(phrase_info, dict):
                    phrase = phrase_info.get("phrase", "")
                    strength = phrase_info.get("strength_level", 0)
                    if strength > max_strength:
                        max_strength = strength
                    if phrase:
                        all_phrases.append(phrase)
                    if phrase_info.get("risk_signal"):
                        risk_signals.append(phrase_info["risk_signal"])
                    if phrase_info.get("opportunity_signal"):
                        opportunity_signals.append(phrase_info["opportunity_signal"])
                elif isinstance(phrase_info, str):
                    all_phrases.append(phrase_info)

            pub_date = doc.get("publish_date", "")
            if pub_date and (not latest_date or pub_date > latest_date):
                latest_date = pub_date

        signal_direction = "Stable"
        if max_strength >= 4:
            signal_direction = "Strong/Firm"
        elif max_strength >= 3:
            signal_direction = "Moderate/Active"
        elif max_strength >= 2:
            signal_direction = "Encouraging"
        elif max_strength >= 1:
            signal_direction = "Exploratory"

        sections.append(f"Based on {doc_count} document(s), the policy signal for **{topic}** is **{signal_direction}**.")
        if latest_date:
            sections.append(f"Latest document date: {latest_date}.")

        sections.extend(["", "## Signal Strength", "", f"| Metric | Value |", f"|--------|-------|", f"| Max Strength Level | {max_strength}/5 |", f"| Signal Direction | {signal_direction} |", f"| Document Count | {doc_count} |"])

        sections.extend(["", "## Authority Distribution", ""])
        for level in sorted(authority_dist.keys()):
            sections.append(f"- **{level}**: {authority_dist[level]} document(s)")

        sections.extend(["", "## Document Type Distribution", ""])
        for dtype in sorted(doc_type_dist.keys()):
            sections.append(f"- **{dtype}**: {doc_type_dist[dtype]} document(s)")

        if all_phrases:
            unique_phrases = list(dict.fromkeys(all_phrases))
            sections.extend(["", "## Key Policy Language", ""])
            for p in unique_phrases[:10]:
                sections.append(f"- {p}")

        if risk_signals:
            unique_risks = list(dict.fromkeys(risk_signals))
            sections.extend(["", "## Risk Signals", ""])
            for r in unique_risks[:5]:
                sections.append(f"- {r}")

        if opportunity_signals:
            unique_opps = list(dict.fromkeys(opportunity_signals))
            sections.extend(["", "## Opportunity Signals", ""])
            for o in unique_opps[:5]:
                sections.append(f"- {o}")

        sections.extend(["", "## Source Documents", ""])
        for idx, doc in enumerate(documents, 1):
            citation = format_doc_citation(doc)
            url = doc.get("url", "")
            entry = f"{idx}. **{citation}**"
            if url:
                entry += f" [Link]({url})"
            sections.append(entry)

        return "\n".join(sections)

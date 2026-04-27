from __future__ import annotations

from datetime import datetime, timedelta
from typing import List


class WeeklyDigestGenerator:
    def generate(self, weekly_documents: List[dict], signal_cards: List[str]) -> str:
        now = datetime.now()
        week_start = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        week_end = now.strftime("%Y-%m-%d")

        sections = [
            f"# Weekly Policy Digest — {week_start} to {week_end}",
            "",
        ]

        doc_count = len(weekly_documents)
        sections.extend([
            "## Overview",
            "",
            f"This digest covers **{doc_count}** policy documents from the past week.",
            "",
        ])

        if weekly_documents:
            sections.extend(["## Documents by Authority Level", ""])
            by_authority: dict[str, List[dict]] = {}
            for doc in weekly_documents:
                authority = doc.get("authority_level", "Unknown")
                by_authority.setdefault(authority, []).append(doc)
            for level in sorted(by_authority.keys()):
                docs = by_authority[level]
                sections.append(f"### Level {level} ({len(docs)} document(s))")
                sections.append("")
                for doc in docs:
                    title = doc.get("title", "Untitled")
                    source = doc.get("source_name", "Unknown")
                    date = doc.get("publish_date", "Unknown")
                    doc_type = doc.get("doc_type", "")
                    url = doc.get("url", "")
                    entry = f"- **{title}** — {source} ({date})"
                    if doc_type:
                        entry += f" [{doc_type}]"
                    if url:
                        entry += f" [Link]({url})"
                    sections.append(entry)
                sections.append("")

            sections.extend(["## Key Topics This Week", ""])
            topic_counts: dict[str, int] = {}
            for doc in weekly_documents:
                for topic in doc.get("topics", []):
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            for topic, count in sorted_topics[:10]:
                sections.append(f"- **{topic}**: {count} document(s)")
            sections.append("")

            sections.extend(["## Document Types", ""])
            type_counts: dict[str, int] = {}
            for doc in weekly_documents:
                doc_type = doc.get("doc_type", "Unknown")
                type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
            for dtype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                sections.append(f"- **{dtype}**: {count}")
            sections.append("")

            all_phrases: List[str] = []
            all_risks: List[str] = []
            all_opps: List[str] = []
            for doc in weekly_documents:
                for p in doc.get("policy_phrases", []):
                    if isinstance(p, dict):
                        phrase = p.get("phrase", "")
                        if phrase:
                            all_phrases.append(phrase)
                        rs = p.get("risk_signal", "")
                        if rs:
                            all_risks.append(rs)
                        os_ = p.get("opportunity_signal", "")
                        if os_:
                            all_opps.append(os_)
                    elif isinstance(p, str):
                        all_phrases.append(p)

            if all_phrases:
                unique_phrases = list(dict.fromkeys(all_phrases))
                sections.extend(["## Notable Policy Language", ""])
                for ph in unique_phrases[:20]:
                    sections.append(f"- {ph}")
                sections.append("")

            if all_risks:
                unique_risks = list(dict.fromkeys(all_risks))
                sections.extend(["### Risk Signals", ""])
                for r in unique_risks[:10]:
                    sections.append(f"- {r}")
                sections.append("")

            if all_opps:
                unique_opps = list(dict.fromkeys(all_opps))
                sections.extend(["### Opportunity Signals", ""])
                for o in unique_opps[:10]:
                    sections.append(f"- {o}")
                sections.append("")

        if signal_cards:
            sections.extend(["## Policy Signal Cards", ""])
            for card in signal_cards:
                sections.append(card)
                sections.append("")

        sections.extend(["---", f"*Generated at {now.isoformat()}*"])

        return "\n".join(sections)

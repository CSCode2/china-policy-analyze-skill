from __future__ import annotations

from datetime import datetime
from typing import Dict, List


class MonthlySynthesisGenerator:
    def generate(self, monthly_data: dict) -> str:
        now = datetime.now()
        month_label = monthly_data.get("month", now.strftime("%Y-%m"))

        sections = [
            f"# Monthly Policy Synthesis — {month_label}",
            "",
        ]

        total_docs = monthly_data.get("total_documents", 0)
        new_topics = monthly_data.get("new_topics", [])
        trending_topics = monthly_data.get("trending_topics", [])
        documents = monthly_data.get("documents", [])
        policy_signals = monthly_data.get("policy_signals", [])
        regional_breakdown = monthly_data.get("regional_breakdown", {})
        sector_breakdown = monthly_data.get("sector_breakdown", {})

        sections.extend([
            "## Executive Summary",
            "",
            f"This month **{total_docs}** policy documents were tracked.",
            "",
        ])

        if trending_topics:
            sections.extend(["## Trending Topics", ""])
            if isinstance(trending_topics, list):
                items = trending_topics[:10]
                if items and isinstance(items[0], dict):
                    for item in items:
                        topic = item.get("topic", "")
                        count = item.get("count", "")
                        change = item.get("change", "")
                        entry = f"- **{topic}**"
                        if count:
                            entry += f": {count} documents"
                        if change:
                            entry += f" ({change})"
                        sections.append(entry)
                else:
                    for topic in items:
                        sections.append(f"- **{topic}**")
            elif isinstance(trending_topics, dict):
                for topic, count in sorted(trending_topics.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True)[:10]:
                    sections.append(f"- **{topic}**: {count}")
            sections.append("")

        if new_topics:
            sections.extend(["## New Topics Emerged", ""])
            if isinstance(new_topics, list):
                if new_topics and isinstance(new_topics[0], dict):
                    for nt in new_topics:
                        topic = nt.get("topic", "")
                        sections.append(f"- **{topic}**")
                else:
                    for topic in new_topics:
                        sections.append(f"- **{topic}**")
            sections.append("")

        if documents:
            sections.extend(["## Key Documents This Month", ""])
            by_type: Dict[str, List[dict]] = {}
            for doc in documents:
                doc_type = doc.get("doc_type", "Other")
                by_type.setdefault(doc_type, []).append(doc)

            for dtype in sorted(by_type.keys()):
                docs = by_type[dtype]
                sections.append(f"### {dtype} ({len(docs)})")
                sections.append("")
                for doc in sorted(docs, key=lambda d: d.get("publish_date", ""), reverse=True)[:20]:
                    title = doc.get("title", "Untitled")
                    source = doc.get("source_name", "Unknown")
                    date = doc.get("publish_date", "Unknown")
                    url = doc.get("url", "")
                    entry = f"- **{title}** — {source} ({date})"
                    if url:
                        entry += f" [Link]({url})"
                    sections.append(entry)
                if len(docs) > 20:
                    sections.append(f"  - ... and {len(docs) - 20} more")
                sections.append("")

        if policy_signals:
            sections.extend(["## Policy Signal Analysis", ""])
            if isinstance(policy_signals, list):
                for signal in policy_signals[:15]:
                    if isinstance(signal, dict):
                        topic = signal.get("topic", "")
                        strength = signal.get("strength_level", signal.get("avg_strength", ""))
                        direction = signal.get("direction", "")
                        entry = f"- **{topic}**: Strength {strength}/5"
                        if direction:
                            entry += f", Direction: {direction}"
                        sections.append(entry)
                    elif isinstance(signal, str):
                        sections.append(f"- {signal}")
            elif isinstance(policy_signals, str):
                sections.append(policy_signals)
            sections.append("")

        if regional_breakdown:
            sections.extend(["## Regional Breakdown", ""])
            if isinstance(regional_breakdown, dict):
                sorted_regions = sorted(regional_breakdown.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True)
                for region, count in sorted_regions[:15]:
                    sections.append(f"- **{region}**: {count}")
            sections.append("")

        if sector_breakdown:
            sections.extend(["## Sector Breakdown", ""])
            if isinstance(sector_breakdown, dict):
                sorted_sectors = sorted(sector_breakdown.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True)
                for sector, count in sorted_sectors[:15]:
                    sections.append(f"- **{sector}**: {count}")
            sections.append("")

        sections.extend(["## Outlook", "", "Review next month's expected policy calendar and monitor ongoing developments.", "", "---", f"*Generated at {now.isoformat()}*"])

        return "\n".join(sections)

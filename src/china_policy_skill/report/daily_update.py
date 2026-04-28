from __future__ import annotations

from datetime import datetime
from typing import List


class DailyUpdateGenerator:
    @staticmethod
    def _format_doc_entry(doc: dict) -> str:
        title = doc.get("title", "Untitled")
        date = doc.get("publish_date", "")
        doc_number = doc.get("doc_number", "")
        issuing_body = doc.get("issuing_body", "")
        url = doc.get("url", "")

        if "《" not in title:
            title = f"《{title}》"

        parts = [title]
        if doc_number:
            parts.append(doc_number)
        if date:
            parts.append(f"({date})")

        entry = "  - " + " ".join(parts)
        if issuing_body:
            entry += f" — {issuing_body}"
        if url:
            entry += f" [Link]({url})"
        return entry

    def generate(self, new_documents: List[dict], errors: List[dict]) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        sections = [
            f"# Daily Policy Analysis Update — {today}",
            "",
        ]

        doc_count = len(new_documents)
        error_count = len(errors)

        sections.extend([
            "## Summary",
            "",
            f"- **New Documents**: {doc_count}",
            f"- **Errors**: {error_count}",
            "",
        ])

        if new_documents:
            sections.extend(["## New Documents", ""])

            by_authority: dict[str, List[dict]] = {}
            by_type: dict[str, List[dict]] = {}

            for doc in new_documents:
                authority = doc.get("authority_level", "Unknown")
                by_authority.setdefault(authority, []).append(doc)
                doc_type = doc.get("doc_type", "Unknown")
                by_type.setdefault(doc_type, []).append(doc)

            sections.append(f"### By Authority Level")
            sections.append("")
            for level in sorted(by_authority.keys()):
                docs = by_authority[level]
                sections.append(f"**{level}** ({len(docs)} document(s)):")
                for doc in docs:
                    sections.append(self._format_doc_entry(doc))
                sections.append("")

            sections.append(f"### By Document Type")
            sections.append("")
            for dtype in sorted(by_type.keys()):
                docs = by_type[dtype]
                sections.append(f"**{dtype}** ({len(docs)} document(s)):")
                for doc in docs:
                    sections.append(self._format_doc_entry(doc))
                sections.append("")

            all_phrases: List[str] = []
            for doc in new_documents:
                for p in doc.get("policy_phrases", []):
                    if isinstance(p, dict):
                        phrase = p.get("phrase", "")
                        if phrase:
                            all_phrases.append(phrase)
                    elif isinstance(p, str):
                        all_phrases.append(p)

            if all_phrases:
                unique_phrases = list(dict.fromkeys(all_phrases))
                sections.extend(["### Notable Policy Language", ""])
                for ph in unique_phrases[:15]:
                    sections.append(f"- {ph}")
                sections.append("")
        else:
            sections.append("No new documents collected today.")
            sections.append("")

        if errors:
            sections.extend(["## Errors", ""])
            for err in errors:
                source = err.get("source", "Unknown")
                message = err.get("message", err.get("error", "Unknown error"))
                timestamp = err.get("timestamp", "")
                entry = f"- **{source}**: {message}"
                if timestamp:
                    entry += f" ({timestamp})"
                sections.append(entry)
            sections.append("")

        sections.extend(["---", f"*Generated at {datetime.now().isoformat()}*"])

        return "\n".join(sections)

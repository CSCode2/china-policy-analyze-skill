from __future__ import annotations

from typing import Optional

from ..utils.dates import format_doc_citation


class FileCardGenerator:
    def generate(self, doc_metadata: dict, processed_text: str) -> str:
        source_name = doc_metadata.get("source_name", "Unknown")
        publish_date = doc_metadata.get("publish_date", "Unknown")
        url = doc_metadata.get("url", "")
        authority_level = doc_metadata.get("authority_level", "Unknown")
        doc_type = doc_metadata.get("doc_type", "Unknown")
        doc_number = doc_metadata.get("doc_number", "")
        issuing_body = doc_metadata.get("issuing_body", "")
        topics = doc_metadata.get("topics", [])
        policy_phrases = doc_metadata.get("policy_phrases", [])
        summary = doc_metadata.get("summary", "")

        topics_str = ", ".join(topics) if isinstance(topics, list) else str(topics)
        phrases_str = ", ".join(policy_phrases) if isinstance(policy_phrases, list) else str(policy_phrases)

        text_preview = processed_text[:500] if processed_text else ""

        formatted_title = format_doc_citation(doc_metadata)

        sections = [
            f"# {formatted_title}",
            "",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| Source | {source_name} |",
            f"| Publish Date | {publish_date} |",
            f"| Document Number | {doc_number or 'N/A'} |",
            f"| Issuing Body | {issuing_body or source_name} |",
            f"| Authority Level | {authority_level} |",
            f"| Document Type | {doc_type} |",
            f"| Topics | {topics_str} |",
            f"| Policy Phrases | {phrases_str} |",
        ]

        if url:
            sections.append(f"| URL | {url} |")

        if summary:
            sections.extend(["", "## Summary", "", summary])

        if text_preview:
            sections.extend(["", "## Key Content", "", text_preview])

        return "\n".join(sections)

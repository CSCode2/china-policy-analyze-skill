from __future__ import annotations

from typing import List

from ..utils.dates import format_doc_citation


class ConceptCardGenerator:
    def generate(self, concept: str, documents: List[dict]) -> str:
        if not concept:
            return ""

        sections = [
            f"# Concept: {concept}",
            "",
            "## Definition",
            "",
            f"The concept **{concept}** as reflected in Chinese policy documents.",
            "",
            "## Document Evidence",
            "",
        ]

        if not documents:
            sections.append("No documents found for this concept.")
        else:
            for idx, doc in enumerate(documents, 1):
                citation = format_doc_citation(doc)
                url = doc.get("url", "")
                relevance = doc.get("relevance_score", "")
                authority = doc.get("authority_level", "")

                entry = f"{idx}. **{citation}**"
                if authority:
                    entry += f" [Authority: {authority}]"
                if relevance:
                    entry += f" [Relevance: {relevance}]"
                if url:
                    entry += f" [Link]({url})"
                sections.append(entry)

        sections.extend(["", "## Key Themes", ""])

        themes = set()
        for doc in documents:
            for topic in doc.get("topics", []):
                themes.add(topic)
        if themes:
            for theme in sorted(themes):
                sections.append(f"- {theme}")
        else:
            sections.append("- No themes identified.")

        return "\n".join(sections)

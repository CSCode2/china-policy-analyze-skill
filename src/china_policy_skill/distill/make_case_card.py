from __future__ import annotations

from typing import List

from ..utils.dates import format_doc_citation


class CaseCardGenerator:
    def generate(self, case_data: dict) -> str:
        if not case_data:
            return ""

        case_name = case_data.get("case_name", case_data.get("title", "Untitled Case"))
        if "《" not in case_name:
            case_name = f"《{case_name}》"
        case_number = case_data.get("case_number", "")
        court = case_data.get("court", "")
        date = case_data.get("judgment_date", case_data.get("date", "Unknown"))
        case_type = case_data.get("case_type", "")
        document_type = case_data.get("document_type", "")
        parties = case_data.get("parties", [])
        legal_basis = case_data.get("legal_basis", [])
        facts = case_data.get("facts", "")
        holding = case_data.get("holding", case_data.get("judgment", ""))
        reasoning = case_data.get("reasoning", "")
        penalty = case_data.get("penalty", case_data.get("sanction", ""))
        significance = case_data.get("significance", "")
        industry = case_data.get("industry", "")
        topics = case_data.get("topics", [])
        url = case_data.get("url", "")
        authority_level = case_data.get("authority_level", "")

        date_str = str(date) if date else "日期不详"
        title_line = case_name
        if case_number:
            title_line += f"（{case_number}，{date_str}）"
        else:
            title_line += f"（{date_str}）"

        sections = [
            f"# {title_line}",
            "",
            "| Field | Value |",
            "|-------|-------|",
        ]

        if case_number:
            sections.append(f"| Case Number | {case_number} |")
        if court:
            sections.append(f"| Court | {court} |")
        sections.append(f"| Date | {date} |")
        if case_type:
            sections.append(f"| Case Type | {case_type} |")
        if document_type:
            sections.append(f"| Document Type | {document_type} |")
        if industry:
            sections.append(f"| Industry | {industry} |")
        if authority_level:
            sections.append(f"| Authority Level | {authority_level} |")
        if url:
            sections.append(f"| URL | {url} |")

        if parties:
            sections.extend(["", "## Parties", ""])
            if isinstance(parties, list):
                for party in parties:
                    if isinstance(party, dict):
                        name = party.get("name", "")
                        role = party.get("role", "")
                        sections.append(f"- **{role}**: {name}" if role else f"- {name}")
                    else:
                        sections.append(f"- {party}")
            else:
                sections.append(str(parties))

        if legal_basis:
            sections.extend(["", "## Legal Basis", ""])
            if isinstance(legal_basis, list):
                for basis in legal_basis:
                    sections.append(f"- {basis}")
            else:
                sections.append(str(legal_basis))

        if facts:
            sections.extend(["", "## Facts", "", facts])

        if reasoning:
            sections.extend(["", "## Reasoning", "", reasoning])

        if holding:
            sections.extend(["", "## Holding/Judgment", "", holding])

        if penalty:
            sections.extend(["", "## Penalty/Sanctions", "", penalty])

        if significance:
            sections.extend(["", "## Significance", "", significance])

        if topics:
            sections.extend(["", "## Related Topics", ""])
            topic_list = topics if isinstance(topics, list) else [topics]
            for t in topic_list:
                sections.append(f"- {t}")

        return "\n".join(sections)

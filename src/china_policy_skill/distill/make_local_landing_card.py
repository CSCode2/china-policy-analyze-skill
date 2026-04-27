from __future__ import annotations

from typing import List


class LocalLandingCardGenerator:
    def generate(self, region: str, topic: str, documents: List[dict]) -> str:
        if not region or not topic:
            return ""

        sections = [
            f"# Local Landing: {topic} in {region}",
            "",
            "## Overview",
            "",
            f"Policy analysis for **{topic}** as it applies to **{region}**.",
            "",
        ]

        if not documents:
            sections.append("No local policy documents found for this topic and region.")
            sections.append("")
            sections.extend(["## National-Level Context", "", "Review national-level policy signals for this topic and assess regional applicability."])
            return "\n".join(sections)

        local_docs = []
        national_docs = []
        for doc in documents:
            doc_region = doc.get("region", "")
            authority = doc.get("authority_level", "")
            if doc_region and region in doc_region:
                local_docs.append(doc)
            elif authority in ("S", "A"):
                national_docs.append(doc)
            else:
                local_docs.append(doc)

        if local_docs:
            sections.extend(["## Regional Policy Documents", ""])
            for idx, doc in enumerate(local_docs, 1):
                title = doc.get("title", "Untitled")
                source = doc.get("source_name", "Unknown")
                date = doc.get("publish_date", "Unknown")
                url = doc.get("url", "")
                authority = doc.get("authority_level", "")
                stage = doc.get("implementation_stage", "")
                entry = f"{idx}. **{title}** — {source} ({date})"
                if authority:
                    entry += f" [Authority: {authority}]"
                if stage:
                    entry += f" [Stage: {stage}]"
                if url:
                    entry += f" [Link]({url})"
                sections.append(entry)
            sections.append("")

            local_phrases: List[str] = []
            local_risks: List[str] = []
            local_opps: List[str] = []
            for doc in local_docs:
                for p in doc.get("policy_phrases", []):
                    if isinstance(p, dict):
                        phrase = p.get("phrase", "")
                        if phrase:
                            local_phrases.append(phrase)
                        rs = p.get("risk_signal", "")
                        if rs:
                            local_risks.append(rs)
                        os_ = p.get("opportunity_signal", "")
                        if os_:
                            local_opps.append(os_)
                    elif isinstance(p, str):
                        local_phrases.append(p)

            if local_phrases:
                unique_phrases = list(dict.fromkeys(local_phrases))
                sections.extend(["### Key Policy Language", ""])
                for ph in unique_phrases[:10]:
                    sections.append(f"- {ph}")
                sections.append("")

            if local_risks:
                unique_risks = list(dict.fromkeys(local_risks))
                sections.extend(["### Regional Risk Signals", ""])
                for r in unique_risks[:5]:
                    sections.append(f"- {r}")
                sections.append("")

            if local_opps:
                unique_opps = list(dict.fromkeys(local_opps))
                sections.extend(["### Regional Opportunity Signals", ""])
                for o in unique_opps[:5]:
                    sections.append(f"- {o}")
                sections.append("")

        if national_docs:
            sections.extend(["## National-Level Context", ""])
            for idx, doc in enumerate(national_docs, 1):
                title = doc.get("title", "Untitled")
                source = doc.get("source_name", "Unknown")
                date = doc.get("publish_date", "Unknown")
                url = doc.get("url", "")
                entry = f"{idx}. **{title}** — {source} ({date})"
                if url:
                    entry += f" [Link]({url})"
                sections.append(entry)
            sections.append("")

        sections.extend(["## Implementation Notes", "", f"- Verify local implementing rules and deadlines for {region}.", f"- Check for regional pilot programs or special zones related to {topic}.", f"- Monitor local enforcement actions and compliance requirements."])

        return "\n".join(sections)

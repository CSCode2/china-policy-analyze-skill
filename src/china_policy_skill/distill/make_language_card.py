from __future__ import annotations

from typing import List


class LanguageCardGenerator:
    def generate(self, phrase: str, evidence: List[dict]) -> str:
        if not phrase:
            return ""

        sections = [
            f"# Language Card: {phrase}",
            "",
            "## Phrase Analysis",
            "",
        ]

        if not evidence:
            sections.append("No evidence found for this phrase.")
            return "\n".join(sections)

        strength_levels: List[int] = []
        stages: List[str] = []
        risk_signals: List[str] = []
        opportunity_signals: List[str] = []
        uncertainties: List[str] = []
        explanations: List[str] = []

        for ev in evidence:
            if isinstance(ev, dict):
                s = ev.get("strength_level", 0)
                if s:
                    strength_levels.append(s)
                stage = ev.get("implementation_stage", "")
                if stage:
                    stages.append(stage)
                rs = ev.get("risk_signal", "")
                if rs:
                    risk_signals.append(rs)
                os_ = ev.get("opportunity_signal", "")
                if os_:
                    opportunity_signals.append(os_)
                u = ev.get("uncertainty", "")
                if u:
                    uncertainties.append(u)
                exp = ev.get("plain_language_explanation", "")
                if exp:
                    explanations.append(exp)

        avg_strength = sum(strength_levels) / len(strength_levels) if strength_levels else 0
        avg_strength_rounded = round(avg_strength, 1)

        strength_label = "Unknown"
        if avg_strength_rounded >= 4.5:
            strength_label = "Mandatory/Absolute"
        elif avg_strength_rounded >= 3.5:
            strength_label = "Strong Obligation"
        elif avg_strength_rounded >= 2.5:
            strength_label = "Policy Encouragement"
        elif avg_strength_rounded >= 1.5:
            strength_label = "Guidance/Encouragement"
        elif avg_strength_rounded >= 0.5:
            strength_label = "Exploratory"

        sections.extend([f"**Phrase**: {phrase}", "", f"**Average Strength**: {avg_strength_rounded}/5 ({strength_label})", ""])

        if explanations:
            unique_explanations = list(dict.fromkeys(explanations))
            sections.extend(["**Explanation**:", ""])
            for exp in unique_explanations[:3]:
                sections.append(f"- {exp}")
            sections.append("")

        if stages:
            unique_stages = list(dict.fromkeys(stages))
            sections.extend(["**Implementation Stages**:", ""])
            for st in unique_stages:
                sections.append(f"- {st}")
            sections.append("")

        if risk_signals:
            unique_risks = list(dict.fromkeys(risk_signals))
            sections.extend(["**Risk Signals**:", ""])
            for r in unique_risks:
                sections.append(f"- {r}")
            sections.append("")

        if opportunity_signals:
            unique_opps = list(dict.fromkeys(opportunity_signals))
            sections.extend(["**Opportunity Signals**:", ""])
            for o in unique_opps:
                sections.append(f"- {o}")
            sections.append("")

        if uncertainties:
            unique_unc = list(dict.fromkeys(uncertainties))
            sections.extend(["**Uncertainties**:", ""])
            for u in unique_unc:
                sections.append(f"- {u}")
            sections.append("")

        sections.extend(["## Document Evidence", ""])
        for idx, ev in enumerate(evidence, 1):
            if isinstance(ev, dict):
                source = ev.get("source_title", ev.get("source_name", "Unknown"))
                date = ev.get("publish_date", "Unknown")
                strength = ev.get("strength_level", "?")
                context = ev.get("context", "")
                entry = f"{idx}. **{source}** ({date}) — Strength: {strength}/5"
                if context:
                    entry += f"\n   > {context}"
                sections.append(entry)

        return "\n".join(sections)

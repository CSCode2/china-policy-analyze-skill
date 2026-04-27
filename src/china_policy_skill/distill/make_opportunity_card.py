from __future__ import annotations

from typing import List


_OPPORTUNITY_PROFILES = {
    "general": {
        "label": "General Business",
        "focus_areas": ["market_access", "regulatory_compliance", "industry_trends"],
    },
    "investor": {
        "label": "Investor",
        "focus_areas": ["market_opportunity", "risk_assessment", "sector_allocation"],
    },
    "operator": {
        "label": "Business Operator",
        "focus_areas": ["compliance_requirements", "operational_impact", "timeline"],
    },
    "legal": {
        "label": "Legal/Compliance",
        "focus_areas": ["regulatory_changes", "enforcement_trends", "compliance_obligations"],
    },
}


class OpportunityCardGenerator:
    def generate(
        self,
        topic: str,
        policy_signals: List[dict],
        user_profile: str = "general",
    ) -> str:
        if not topic:
            return ""

        profile = _OPORTUNITY_PROFILES.get(user_profile, _OPORTUNITY_PROFILES["general"])
        sections = [
            f"# Opportunity: {topic}",
            "",
            f"**Profile**: {profile['label']}",
            "",
            "## Opportunity Assessment",
            "",
        ]

        if not policy_signals:
            sections.append("No policy signals found for this topic.")
            return "\n".join(sections)

        total_strength = 0
        count = 0
        all_risks: List[str] = []
        all_opportunities: List[str] = []
        all_stages: List[str] = []

        for signal in policy_signals:
            strength = signal.get("strength_level", 0)
            if strength:
                total_strength += strength
                count += 1
            for r in signal.get("risk_signals", []):
                all_risks.append(r)
            for o in signal.get("opportunity_signals", []):
                all_opportunities.append(o)
            stage = signal.get("implementation_stage", "")
            if stage:
                all_stages.append(stage)

        avg_strength = round(total_strength / count, 1) if count else 0

        if avg_strength >= 4:
            opportunity_level = "High Confidence"
        elif avg_strength >= 3:
            opportunity_level = "Moderate Confidence"
        elif avg_strength >= 2:
            opportunity_level = "Emerging"
        else:
            opportunity_level = "Early Stage/Exploratory"

        sections.append(f"**Opportunity Level**: {opportunity_level}")
        sections.append(f"**Average Signal Strength**: {avg_strength}/5")
        sections.append("")

        sections.extend(["## Focus Areas for " + profile["label"], ""])
        for area in profile["focus_areas"]:
            area_label = area.replace("_", " ").title()
            analysis = self._analyze_focus_area(area, policy_signals)
            sections.append(f"### {area_label}")
            sections.append("")
            sections.append(analysis)
            sections.append("")

        unique_risks = list(dict.fromkeys(all_risks))
        if unique_risks:
            sections.extend(["## Risk Factors", ""])
            for r in unique_risks[:10]:
                sections.append(f"- {r}")
            sections.append("")

        unique_opps = list(dict.fromkeys(all_opportunities))
        if unique_opps:
            sections.extend(["## Opportunity Drivers", ""])
            for o in unique_opps[:10]:
                sections.append(f"- {o}")
            sections.append("")

        unique_stages = list(dict.fromkeys(all_stages))
        if unique_stages:
            sections.extend(["## Implementation Timeline", ""])
            for s in unique_stages:
                sections.append(f"- {s}")
            sections.append("")

        sections.extend(["## Recommendations", ""])
        recs = self._generate_recommendations(opportunity_level, profile["focus_areas"])
        for rec in recs:
            sections.append(f"- {rec}")

        return "\n".join(sections)

    def _analyze_focus_area(self, area: str, signals: List[dict]) -> str:
        phrases: List[str] = []
        for signal in signals:
            phrase = signal.get("phrase", "")
            if phrase:
                phrases.append(phrase)
        if phrases:
            unique = list(dict.fromkeys(phrases))
            return f"Related policy language: {', '.join(unique[:5])}"
        return "Insufficient data for detailed analysis."

    def _generate_recommendations(self, level: str, focus_areas: List[str]) -> List[str]:
        recs: List[str] = []
        if level == "High Confidence":
            recs.append("Prepare for compliance requirements with short timelines.")
            recs.append("Allocate resources to capture first-mover advantages.")
        elif level == "Moderate Confidence":
            recs.append("Monitor developments closely for acceleration signals.")
            recs.append("Begin preliminary compliance and positioning work.")
        elif level == "Emerging":
            recs.append("Track policy evolution and build internal expertise.")
            recs.append("Engage with industry associations for early signals.")
        else:
            recs.append("Maintain awareness but limit resource commitment.")
            recs.append("Participate in pilot programs where available.")
        if "regulatory_compliance" in focus_areas or "compliance_requirements" in focus_areas:
            recs.append("Review current compliance posture against emerging requirements.")
        if "market_opportunity" in focus_areas:
            recs.append("Assess market positioning relative to policy direction.")
        return recs

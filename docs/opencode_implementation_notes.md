# OpenCode Implementation Notes

## Architecture Decisions

### Decision 1: Monolithic Skill Structure

The skill is organized as a set of Markdown files in the `skill/` directory rather than as a code module. This was chosen because:

- The primary consumer is an LLM agent that reads instructions from Markdown
- Markdown allows easy editing by both humans and agents
- No runtime code is required for the skill itself; the skill is a knowledge and instruction artifact
- Separation of concerns: each file addresses one aspect of the system

### Decision 2: Source Priority Hierarchy

The S/A/B/C/D/E hierarchy reflects the actual authority structure of the Chinese policy system. Key design choices:

- S-level is restricted to truly supreme sources; over-including S-level would dilute its meaning
- E-level sources are explicitly allowed but only as leads, never as evidence
- Foreign policy sources have a parallel hierarchy (FP-S through FP-E) because the authority structure is fundamentally different
- The hierarchy is used for conflict resolution, not just for citation quality

### Decision 3: Evidence Level System (L0-L5)

The evidence levels are designed to be applied to individual claims, not to entire answers. This allows:

- Granular quality assessment within a single answer
- Clear communication of uncertainty to the user
- Identification of specific evidence gaps for targeted follow-up

The L0-L5 scale was chosen over a simpler confidence scale because it captures both the type and quantity of evidence, not just the analyst's subjective confidence.

### Decision 4: Policy Reasoning Framework as Process

The policy reasoning framework is written as a step-by-step procedure rather than as a set of rules because:

- Policy analysis is inherently sequential (identify → retrieve → interpret → output)
- A procedural framework is easier for the agent to follow consistently
- It reduces the risk of skipping steps (e.g., checking for implementation evidence)
- It aligns with the analysis procedure in SKILL.md

### Decision 5: Template-Based Output

Output templates serve multiple purposes:

- Consistency across answers regardless of the agent session
- Built-in quality checks (each template has required sections)
- User-type tailoring through the user profile adapter
- Anti-overinterpretation through the warning template

### Decision 6: Anti-Overinterpretation as Core System Feature

Overinterpretation is treated as a first-class concern rather than an afterthought because:

- It is the most common analytical error in policy analysis
- It can have real consequences (bad investment decisions, compliance failures)
- It is difficult to detect in one's own output without explicit rules
- The 12 rules provide specific, testable criteria for overinterpretation detection

### Decision 7: Hermes as Automated Operations Agent

Hermes operates as an automated agent with bounded autonomy:

- Can self-repair routine issues (URL changes, parser updates, stale indexes)
- Cannot self-merge safety-critical changes
- Is required to escalate specific categories of issues to humans
- Has explicit "what not to do" rules to prevent overreach

---

## Current Status

### Implemented

- Skill file structure and all 10 skill documents
- Source priority hierarchy (S/A/B/C/D/E + FP-S through FP-E)
- Policy language lexicon (domestic + foreign policy phrases)
- Evidence level system (L0-L5)
- Anti-overinterpretation rules (12 rules with examples)
- Output templates (8 templates for different answer types)
- Safety and boundary rules (30 rules across 9 sections)
- User profile adapter (7 user types with tailored output)
- Evaluation checklist (6 weighted criteria + operational metrics)
- Hermes operating manual (10 recurring tasks + procedures)

### Not Yet Implemented

- Automated source crawling pipeline
- Content caching and indexing system
- Document relationship graph
- Phrase occurrence index
- Policy stage tracking database
- Forecast calibration database
- Question bank for testing
- Automated answer quality testing
- Source registry with URL management
- Error and incident tracking database

### Partially Implemented

- Policy language extraction from crawled content (lexicon exists but extraction pipeline does not)
- Cross-reference detection (rules exist but automated detection does not)
- Source availability monitoring (criteria defined but monitoring system does not exist)
- Data freshness tracking (criteria defined but tracking system does not exist)

---

## Known Issues

### Issue 1: Lexicon Coverage Gaps

The policy language lexicon covers the most common phrases but does not cover all phrases encountered in official documents. New phrases are identified during the monthly lexicon review but there is a lag. Mitigation: the analysis procedure instructs the agent to note when a phrase is not in the lexicon and interpret it conservatively.

### Issue 2: Source Accessibility Variability

Government websites in China have variable uptime and may block automated crawling. Anti-bot measures are common. Mitigation: Hermes procedures include rate limiting, user-agent rotation, and exponential backoff. However, some sources may remain inaccessible for extended periods.

### Issue 3: Content Hash Change Detection

Content hash comparison is used to detect updates, but some websites serve dynamic content (timestamps, session IDs) that changes the hash without meaningful content change. Mitigation: the content parsing pipeline should extract the meaningful content before hashing. This is not yet implemented.

### Issue 4: Local Source Fragmentation

C-level sources (municipal departments, industrial parks) are extremely numerous and fragmented. Comprehensive coverage of all C-level sources is not feasible. Mitigation: priority should be given to C-level sources in regions and sectors that are most commonly queried. The source registry should track which C-level sources are monitored.

### Issue 5: Policy Stage Assessment Subjectivity

Policy stage assessment (Stage 0-6) requires judgment that may vary between analysts. Mitigation: the assessment criteria are specific and evidence-based, but borderline cases will occur. When the stage is ambiguous, the answer should present the range and the evidence for each possible stage.

### Issue 6: Foreign Policy Source Asymmetry

Chinese official foreign policy sources and external sources often present conflicting factual claims. The current system handles this by presenting both positions, but does not resolve factual disputes. Mitigation: this is a design choice, not a bug. The system should not adjudicate international factual disputes.

### Issue 7: Forecast Calibration Cold Start

The forecast calibration system requires historical prediction data to compute calibration scores. In the initial period, there will be insufficient data for meaningful calibration. Mitigation: use conservative confidence levels until sufficient data accumulates (target: at least 50 resolved predictions per confidence level).

### Issue 8: User Type Detection Accuracy

Implicit user type detection based on question phrasing is imprecise. Mitigation: the system should prompt for explicit user type when the answer would significantly benefit from tailoring. Default to a balanced presentation when the type is unknown.

---

## Handoff Items for Hermes

### Immediate Priorities (Week 1)

1. Set up the source registry with initial S-level and A-level URLs
2. Implement the daily source availability check (Task 1)
3. Implement the daily crawl error review (Task 3)
4. Create the error and incident tracking database

### Short-term Priorities (Month 1)

1. Implement the crawl and parse pipeline for S-level and A-level sources
2. Set up content caching with hash-based change detection
3. Implement the policy language extraction pipeline
4. Create the forecast calibration database
5. Implement the weekly content update processing (Task 4)
6. Implement the weekly quality metric collection (Task 6)

### Medium-term Priorities (Quarter 1)

1. Expand crawl coverage to B-level and selected C-level sources
2. Implement the document relationship graph
3. Implement automated cross-reference detection
4. Build the question bank for answer quality testing
5. Implement the monthly full system health check (Task 10)
6. Begin collecting forecast calibration data

### Ongoing Maintenance

1. Execute all daily, weekly, and monthly tasks per the operating manual
2. Update the lexicon based on monthly review
3. Update the source registry based on monthly review
4. Monitor and adjust forecast calibration quarterly
5. Review and update safety rules if new safety incidents occur
6. Review and update the policy reasoning framework if systematic analytical errors are detected

### Key Contacts and Escalation Points

- Safety rule violations: Escalate immediately per the error classification table
- Source accessibility issues beyond 72 hours: Escalate to human operations
- Lexicon interpretation disputes: Escalate to domain expert for review
- Forecast calibration failures: Escalate if Brier score exceeds 0.4 for two consecutive months
- System health check failures: Escalate if quality test average falls below 3.5/5.0

### Configuration Files to Monitor

| File | Change Frequency | Review Requirement |
|------|-----------------|-------------------|
| skill/SKILL.md | Rare (quarterly or less) | Human review required |
| skill/policy_reasoning_framework.md | Rare | Human review required |
| skill/source_priority.md | Monthly potential updates | Human review for hierarchy changes |
| skill/policy_language_lexicon.md | Monthly | PR with human review |
| skill/output_templates.md | Rare | Test validation required |
| skill/safety_and_boundary.md | Rare (unless incident) | Human review required |
| skill/evaluation_checklist.md | Quarterly | Human review required |
| skill/evidence_level.md | Rare | Human review required |
| skill/anti_overinterpretation_rules.md | Rare (unless incident) | Human review required |
| skill/user_profile_adapter.md | Quarterly | PR with review |
| docs/hermes_agent_operating_manual.md | As needed | Hermes may update operational sections |
| docs/opencode_implementation_notes.md | As needed | Hermes updates status and known issues |
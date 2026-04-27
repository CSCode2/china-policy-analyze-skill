## What changed and why

<!-- Brief description of what was changed and the motivation -->

## Which task triggered this change

<!-- Reference the Hermes task (e.g., Task 1: Source Availability Check, Task 8: Source Registry Update) -->

## Task reference

- Task number:
- Task name:
- Schedule:

## Changes

### Files changed

<!-- List all files changed with brief description -->

| File | Change description |
|------|-------------------|
|      |                   |

### Type of change

- [ ] Source registry update (URL change, new source, dead source archival)
- [ ] Lexicon update (new phrase, existing entry correction)
- [ ] Parser update (page structure change fix)
- [ ] Configuration update (rate limit, schedule, threshold)
- [ ] Operational procedure update
- [ ] Skill document update
- [ ] Bug fix
- [ ] Feature addition
- [ ] Documentation update

## Test results

<!-- Describe what was tested and the results -->

- [ ] Source accessibility verified (if source change)
- [ ] Content hash comparison passed (if content change)
- [ ] Parser test passed (if parser change)
- [ ] Integration test passed
- [ ] Full test suite passed

## Category classification

- [ ] Non-breaking; may be self-merged after passing tests
  - Source registry URL updates
  - New lexicon entries
  - Non-breaking configuration changes
  - Parser updates for structure changes
- [ ] Requires human review before merge
  - Changes to skill/SKILL.md
  - Changes to skill/safety_and_boundary.md
  - Changes to skill/policy_reasoning_framework.md
  - Changes to skill/anti_overinterpretation_rules.md
  - Changes to skill/evidence_level.md
  - Changes to source priority hierarchy
  - Changes triggered by hallucination incident
  - Changes affecting policy interpretation accuracy

## Manual review needed

<!-- If human review is required, explain what needs to be reviewed and why -->

- [ ] No manual review needed (self-merge eligible)
- [ ] Manual review needed

**If manual review needed:**

Reason:
What to review:
Urgency:

## Impact assessment

### What this change affects

<!-- Describe the scope of impact -->

- **Monitoring scope**: (Which sources, topics, or indicators are affected?)
- **Operational scope**: (Which tasks or schedules are affected?)
- **Output scope**: (Will this change affect answer quality or content?)

### Risk assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
|      |           |        |            |

### Rollback plan

<!-- How to revert this change if it causes issues -->

## Quality checks

- [ ] No fabricated data or sources
- [ ] No policy interpretation changes without evidence
- [ ] All URL changes verified accessible
- [ ] No safety rule violations
- [ ] Change does not affect source priority hierarchy without justification
- [ ] Documentation updated if needed

## Additional notes

<!-- Any other information relevant to this PR -->

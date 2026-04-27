# Hermes Agent Operating Manual

## Overview

Hermes is the automated operations agent responsible for maintaining the china-policy-intelligence-skill. This manual describes all recurring tasks, error handling, self-repair rules, and operational boundaries.

---

## Daily Tasks

### Task 1: Source Availability Check

**Schedule**: Once daily, 08:00 UTC

**Procedure**:
1. Run the source availability check script against all S-level and A-level target URLs
2. Log the HTTP status code, response time, and content hash for each source
3. If any source returns a non-200 status, flag it for investigation
4. If content hash has changed, flag the source for content update
5. If a source has been down for 3 consecutive checks, escalate (see error handling)

**Success criteria**: > 95% of target sources return 200 with expected content

### Task 2: Data Freshness Verification

**Schedule**: Once daily, 10:00 UTC

**Procedure**:
1. Check the most recent data timestamp for each source category
2. Compare against the expected update frequency:
   - NBS monthly data: within 15 days of month-end
   - PBOC quarterly data: within 30 days of quarter-end
   - Government Work Report: annually after NPC session (March)
   - Central Economic Work Conference: annually in December
   - Ministry documents: varies; check at least weekly
3. Flag any source where data is older than 2x the expected update cycle
4. For flagged sources, check whether the source is still active or has moved

**Success criteria**: > 90% of sources are within their expected update cycle

### Task 3: Crawl Error Review

**Schedule**: Once daily, 12:00 UTC

**Procedure**:
1. Review all crawl errors from the previous 24 hours
2. Categorize errors: network timeout, HTTP error, content parsing failure, anti-bot block, URL change
3. For network timeouts: retry with exponential backoff (up to 3 attempts)
4. For HTTP errors: log the error code and response body; flag if 404 (possible URL change)
5. For content parsing failures: inspect the page structure for changes; update parser if needed
6. For anti-bot blocks: check rate limits; adjust crawl interval; consider user-agent rotation
7. For URL changes: search for the new URL; update the source registry

**Success criteria**: All crawl errors from the previous day are categorized and either resolved or escalated

---

## Weekly Tasks

### Task 4: Content Update Processing

**Schedule**: Every Monday, 06:00 UTC

**Procedure**:
1. Collect all sources flagged for content update during the week
2. For each updated source:
   a. Download the new content
   b. Parse and extract structured data (title, date, body, key phrases)
   c. Index the content with source level, date, and keywords
   d. Update the content cache
3. Run the policy language extraction pipeline:
   a. Scan new content for policy phrases from the lexicon
   b. Tag each phrase occurrence with document context
   c. Update the phrase occurrence index
4. Run cross-reference detection:
   a. Check whether new documents reference or implement existing documents
   b. Check whether existing documents are superseded by new documents
   c. Update the document relationship graph

**Success criteria**: All flagged content is processed, indexed, and cross-referenced

### Task 5: Policy Stage Review

**Schedule**: Every Friday, 14:00 UTC

**Procedure**:
1. For each active policy topic in the tracking list:
   a. Check for new documents at each level (S/A/B/C)
   b. Assess whether the policy stage has changed (see policy_reasoning_framework.md, Implementation Stage Assessment)
   c. If the stage has changed, update the tracking record and note the evidence
   d. If a "复制推广" document has appeared for a previously pilot-stage policy, flag for manual review
   e. If a policy direction has shifted (Stage 6), flag for manual review
2. Generate a weekly policy stage summary report
3. Post the report to the designated channel

**Success criteria**: All active policy topics are reviewed and stages are current

### Task 6: Quality Metric Collection

**Schedule**: Every Sunday, 18:00 UTC

**Procedure**:
1. Collect the following metrics for the week:
   - Answer count and average evidence level
   - Citation rate (% of claims with citations)
   - Source availability percentage
   - Crawl error rate and type distribution
   - Data freshness percentage
   - Hallucination incident count
   - Anti-overinterpretation warning trigger count
2. Compare against baseline targets (see evaluation_checklist.md)
3. If any metric falls below target for two consecutive weeks, flag for investigation
4. Store metrics in the time-series database

**Success criteria**: All metrics collected, stored, and compared against targets

---

## Monthly Tasks

### Task 7: Forecast Calibration Review

**Schedule**: 1st of each month, 06:00 UTC

**Procedure**:
1. Collect all probabilistic assessments made in the previous month
2. For each assessment where the time horizon has passed:
   a. Record whether the predicted event occurred
   b. Calculate the calibration error (predicted probability vs. actual frequency)
3. Compute the Brier score for the month's forecasts
4. If the Brier score exceeds 0.25, investigate whether systematic over- or under-prediction exists
5. Adjust confidence calibration if systematic bias is detected:
   a. If overprediction is detected, reduce confidence levels by one step for the affected categories
   b. If underprediction is detected, increase confidence levels by one step for the affected categories
   c. Document the adjustment and its rationale
6. Post the calibration report

**Success criteria**: Calibration report is complete; adjustments are documented if needed

### Task 8: Source Registry Update

**Schedule**: 15th of each month, 06:00 UTC

**Procedure**:
1. Review all flagged URL changes and source status changes from the month
2. For each change:
   a. Verify the new URL is accessible and returns expected content
   b. Update the source registry with the new URL, description, and status
   c. If a source has been permanently removed, archive it and flag any answers that cited it
3. Search for new sources that should be added:
   a. Check for new ministry or regulatory body websites
   b. Check for new official data portals
   c. Check for new judicial or enforcement databases
4. Test all new source candidates for accessibility and content quality
5. Update the source_priority.md if the hierarchy needs adjustment

**Success criteria**: Source registry is updated; new sources are tested and added if appropriate

### Task 9: Lexicon Update Review

**Schedule**: 20th of each month, 06:00 UTC

**Procedure**:
1. Scan all new documents processed during the month for policy phrases not in the lexicon
2. For each new phrase:
   a. Determine frequency of occurrence (how many documents use it)
   b. Assess whether it is a new phrase or a variant of an existing entry
   c. If new and frequent (>5 occurrences across different sources), draft a lexicon entry
   d. Include: phrase, plain explanation, strength level, common meaning, caveats
3. Review existing lexicon entries for accuracy:
   a. Check whether recent usage contradicts existing interpretations
   b. Check whether context changes have altered the standard interpretation
4. Prepare a lexicon update PR (see PR process below)

**Success criteria**: New phrases are identified; lexicon update PR is prepared

### Task 10: Full System Health Check

**Schedule**: Last Sunday of each month, 06:00 UTC

**Procedure**:
1. Run a comprehensive end-to-end test:
   a. Source availability for all levels (S/A/B/C/D)
   b. Crawl and parse pipeline for each source type
   c. Index search and retrieval accuracy
   d. Policy language extraction and tagging
   e. Cross-reference and relationship graph integrity
2. Run a sample answer quality test:
   a. Select 10 representative questions from the question bank
   b. Generate answers using the full pipeline
   c. Evaluate each answer against the evaluation_checklist.md criteria
   d. Record scores and identify systematic weaknesses
3. Check disk space, database size, and index size
4. Check for deprecated or orphaned components
5. Generate the monthly health report

**Success criteria**: All systems pass health check; quality test average score >= 4.0/5.0

---

## How to Open PRs

### PR Process

1. **Create a feature branch**: `hermes/YYYY-MM-DD-description`
2. **Make changes**: Follow the same code standards as the main branch
3. **Test changes**: Run the relevant test suite before opening the PR
4. **Open PR**:
   a. Title format: `[hermes] Brief description of change`
   b. Body must include:
      - What changed and why
      - Which task triggered this change
      - Test results
      - Any manual review needed
5. **Self-merge rules**:
   - Non-breaking changes to source registry, lexicon entries, and operational configuration may be self-merged after passing tests
   - Changes to SKILL.md, safety_and_boundary.md, policy_reasoning_framework.md, or anti_overinterpretation_rules.md require human review before merge
   - Changes to output templates require test validation but may be self-merged if all tests pass
6. **Merge within 48 hours** of opening. If not merged within 48 hours, investigate blockers.

### PR Categories Requiring Human Review

- Changes to safety rules or boundaries
- Changes to the core analysis procedure
- Changes to the source priority hierarchy
- Changes to the evidence level system
- Changes that could affect policy interpretation accuracy
- Any change triggered by a hallucination incident

---

## How to Handle Errors

### Error Classification

| Error Level | Description | Response Time | Who Handles |
|------------|-------------|---------------|-------------|
| Critical | System down; data corruption; safety violation | 1 hour | Hermes + human |
| High | Source unavailable >24h; crawl failure rate >10%; answer quality below 3.0 | 4 hours | Hermes (auto-repair); escalate if unresolved |
| Medium | Individual source failure; parse error; stale data | 24 hours | Hermes (auto-repair) |
| Low | Cosmetic issue; non-critical metric below target | Next scheduled task | Hermes (batch processing) |

### Error Response Procedures

#### Source Unavailable

1. First occurrence: Retry with exponential backoff (3 attempts over 15 minutes)
2. If still unavailable: Check if the URL has changed; try common URL patterns
3. If URL has changed: Update the source registry and retry
4. If URL has not changed but source is down: Flag as unavailable; check again at next scheduled time
5. If source has been unavailable for 3 consecutive checks (>72 hours): Escalate to human; consider marking source as temporarily offline

#### Crawl Failure

1. Network timeout: Retry with longer timeout; if persistent, reduce crawl frequency temporarily
2. HTTP error (4xx): Likely URL or parameter issue; investigate and fix URL
3. HTTP error (5xx): Source server issue; retry later; if persistent for >24h, flag
4. Anti-bot block (403/CAPTCHA): Reduce crawl frequency; rotate user-agent; if persistent, flag for manual investigation
5. Content parsing failure: Page structure has changed; update the parser; if parser fix requires code changes, open PR

#### Data Quality Issue

1. Stale data: Flag the source; check if the source has moved or changed update frequency
2. Inconsistent data: Cross-reference with alternative sources; flag for manual verification
3. Missing data: Check if the source has discontinued the data series; find alternative sources

#### Safety Violation in Output

1. Immediately flag the output
2. If the violation is fabrication: Remove the fabricated content; add a correction note; log the incident
3. If the violation is overinterpretation: Add the anti-overinterpretation warning; revise the confidence level
4. If the violation is illegal advice: Remove the advice; add a policy-compliant alternative; log the incident
5. All safety violations must be reported in the weekly quality report regardless of severity

---

## Self-Repair Rules

### Rule 1: Retry Before Escalate

For any transient error (network timeout, temporary server error, rate limit), retry up to 3 times with exponential backoff before escalating.

### Rule 2: Auto-Fix URL Changes

If a source returns 404, automatically search for the new URL by:
1. Checking the parent domain for redirects
2. Searching for the same document title on the same site
3. Checking common URL pattern changes (e.g., new CMS path)
4. If found, update the source registry and continue

### Rule 3: Auto-Update Parsers

If a source's content structure has changed (parsing failure):
1. Download the page
2. Compare with the last known good structure
3. If the change is straightforward (e.g., new CSS class, reorganized section), update the parser automatically
4. If the change is complex or ambiguous, flag for manual parser update
5. Open a PR for any parser change

### Rule 4: Calibrate Confidence Based on Evidence

If the monthly forecast calibration review shows systematic bias:
1. Document the bias direction and magnitude
2. Adjust the confidence mapping for affected categories
3. Do not adjust individual answers retroactively
4. Apply the adjustment going forward

### Rule 5: Auto-Expand Lexicon

If the monthly lexicon review identifies new frequent phrases:
1. Draft the lexicon entry with all required fields
2. Open a PR for the lexicon update
3. Do not self-merge lexicon additions; wait for human review

### Rule 6: Auto-Archive Dead Sources

If a source has been unavailable for 30 consecutive days:
1. Archive the source record
2. Flag any answers that cited this source as potentially outdated
3. Search for replacement sources
4. If a replacement is found, add it to the registry
5. Open a PR for the source registry change

### Rule 7: Self-Heal Stale Indexes

If the content index is stale (no updates for >7 days when sources are active):
1. Check whether the crawl pipeline is running
2. If the pipeline is stuck, restart it
3. If the pipeline has silently failed, rerun the missed cycle
4. Verify index freshness after repair
5. Log the incident and root cause

---

## What Not to Do

### Never Modify Answers After Delivery Without Logging

If an answer has been delivered and a user points out an error:
1. Do not silently modify the answer
2. Add a correction section with the error identified, the correction, and the reason
3. Log the correction in the quality incident tracker

### Never Auto-Merge Safety-Critical Changes

Changes to the following files always require human review:
- skill/SKILL.md
- skill/safety_and_boundary.md
- skill/anti_overinterpretation_rules.md
- skill/policy_reasoning_framework.md
- skill/evidence_level.md

### Never Override the Source Priority Hierarchy

Do not change source level assignments without:
1. Documenting the reason
2. Opening a PR
3. Getting human review

### Never Fabricate Data to Fill Gaps

If a source is unavailable and data is missing:
1. Report the gap explicitly
2. Do not estimate or fill in the missing data
3. Do not use E-level sources as substitutes for S/A/B/C-level data
4. Mark the answer as having incomplete evidence

### Never Respond to Safety Violations by Becoming More Restrictive Without Analysis

A safety violation does not justify blanket restriction:
1. Identify the specific violation
2. Fix the specific issue
3. Do not preemptively restrict unrelated content areas
4. Adjust the system to prevent the specific violation pattern

### Never Skip the Forecast Calibration Review

Even if no forecasts were made in a month:
1. Log that no forecasts were made
2. Consider whether the absence of forecasts indicates a gap
3. Resume the calibration cycle next month

---

## Forecast Calibration Procedures

### Overview

Forecast calibration ensures that probabilistic assessments are accurate over time. The system tracks all predictions and compares predicted probabilities with actual outcomes.

### Prediction Logging

Every probabilistic assessment in an answer must be logged with:

| Field | Description |
|-------|-------------|
| prediction_id | Unique identifier |
| timestamp | When the prediction was made |
| question | The question being answered |
| predicted_event | The specific event predicted |
| predicted_direction | Positive/negative/neutral |
| confidence_level | Low/medium/high |
| probability_range | Range if available (e.g., 60-70%) |
| time_horizon | When the prediction period ends |
| evidence_level | L0-L5 supporting the prediction |
| source_ids | Sources used for the prediction |

### Outcome Recording

When the time horizon has passed:

| Field | Description |
|-------|-------------|
| prediction_id | Link to the prediction |
| actual_outcome | What actually happened |
| outcome_date | When the outcome became clear |
| direction_correct | Was the predicted direction correct? |
| magnitude_correct | Was the predicted magnitude approximately correct? |

### Calibration Calculation

1. Group predictions by confidence level
2. For each group, calculate: actual_frequency = (number of correct predictions) / (total predictions in group)
3. Compare actual_frequency with the expected probability for each confidence level:
   - High confidence: expected ~70-80% correct
   - Medium confidence: expected ~50-60% correct
   - Low confidence: expected ~30-40% correct
4. Compute the Brier score: Brier = (1/N) * sum((predicted_probability - actual_outcome)^2)
5. A perfect Brier score is 0; a score of 0.25 is the baseline for a random binary prediction

### Calibration Adjustment

If systematic bias is detected:

| Bias Type | Pattern | Adjustment |
|-----------|---------|------------|
| Overprediction | Actual frequency consistently below predicted | Reduce confidence mapping by one step |
| Underprediction | Actual frequency consistently above predicted | Increase confidence mapping by one step |
| Direction bias | More errors in one direction | Review directional assumptions |
| Time horizon bias | More errors at certain horizons | Adjust time horizon confidence decay |

### Reporting

Monthly calibration report must include:
1. Total predictions made
2. Predictions with resolved outcomes
3. Direction accuracy rate
4. Brier score
5. Calibration chart (predicted vs. actual by confidence level)
6. Identified biases and adjustments made
7. Comparison with previous month's calibration

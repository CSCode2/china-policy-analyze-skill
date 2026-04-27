# Policy Reasoning Framework

## Document Analysis Steps

### Step 1: Identify the Document

For every policy document encountered, extract and record:

- Document full title
- Document number (if available)
- Issuing body or bodies (joint issuances matter)
- Date of issuance
- Date of publication
- Source level (S/A/B/C/D/E per source_priority.md)
- Document type (opinion, notice, plan, regulation, speech, work report, etc.)

### Step 2: Classify the Document Type

Determine whether the document is:

- **Programmatic**: Sets broad direction (e.g., Five-Year Plans, Central Committee opinions)
- **Implementing**: Provides specific measures (e.g., State Council implementation opinions, ministry notices)
- **Regulatory**: Creates binding rules (e.g., administrative regulations, ministry orders)
- **Guiding**: Indicates preferred direction without binding force (e.g., guiding opinions, development plans)
- **Informational**: Announces data or status (e.g., NBS data releases, work reports)
- **Enforcement**: Signals enforcement action (e.g., MPS notices, SAMR penalty decisions)
- **Judicial**: Court or procuratorate interpretation or case

### Step 3: Parse the Structure

Break the document into its structural components:

- Preamble or introduction (states purpose and background)
- General requirements (states guiding principles)
- Key tasks (the core content, usually numbered)
- Safeguard measures (funding, organization, supervision)
- Responsible units and deadlines
- Pilot designations (if any)
- Sunset or review clauses (if any)

### Step 4: Extract Key Wording

For each relevant section:

- Quote the original wording verbatim
- Identify policy language phrases (see policy_language_lexicon.md)
- Note the section location (which numbered task, which paragraph)
- Note whether wording is mandatory ("必须", "应当"), encouraged ("鼓励", "支持"), permissive ("可以", "允许"), or prohibitive ("禁止", "不得")
- Record any quantified targets (percentages, deadlines, amounts)

### Step 5: Assess Document Weight

Evaluate the effective weight of the document by considering:

- Level of issuing body (higher = more authoritative)
- Whether it is joint-issued (more bodies = more coordination = stronger implementation intent)
- Whether it has a document number (formal issuance)
- Whether responsible units are named
- Whether deadlines are specified
- Whether funding is committed
- Whether pilot locations or projects are named
- Whether enforcement or penalty provisions exist
- Whether it references or implements a higher-level document

## Evidence Chain Construction

### What is an Evidence Chain

An evidence chain is a structured sequence of sources that supports a policy interpretation or conclusion. Each link in the chain must be traceable to a specific source at a specific level.

### Evidence Chain Format

For each claim in the output, provide:

```
Claim: [the assertion]
Evidence:
  - Document: [title]
    Issuing Body: [body]
    Date: [YYYY-MM-DD]
    Source Level: [S/A/B/C/D/E]
    Relevant Wording: "[verbatim quote]"
    Policy Language: [phrase and interpretation]
    Implementation Tools: [funding/pilot/deadline/enforcement/project]
  - Document: [title]
    Issuing Body: [body]
    Date: [YYYY-MM-DD]
    Source Level: [S/A/B/C/D/E]
    Relevant Wording: "[verbatim quote]"
    Policy Language: [phrase and interpretation]
    Implementation Tools: [funding/pilot/deadline/enforcement/project]
```

### Evidence Chain Rules

1. Every substantive claim must have at least one evidence link.
2. Claims about central policy direction require at least one S-level or A-level source.
3. Claims about local implementation require at least one B-level or C-level source in addition to the central source.
4. Claims about enforcement trends require at least one regulatory or judicial source.
5. Claims about macroeconomic conditions require official data (NBS, PBOC, MOF).
6. Inferences must be labeled as inferences, not as original wording.
7. If the evidence chain is incomplete, explicitly state which links are missing.
8. If the evidence chain has contradictory links, apply conflict resolution (see below).

### Building Multi-Source Chains

For complex questions, build chains that connect:

1. **Top-down chain**: Central document → Ministry implementation → Provincial implementation → Municipal/park implementation
2. **Horizontal chain**: Multiple ministries' documents on the same topic (shows coordination)
3. **Temporal chain**: Earlier document → Later document → Most recent document (shows policy evolution)
4. **Enforcement chain**: Policy document → Regulation → Case → Penalty notice (shows implementation depth)

## Implementation Stage Assessment

### Stages

Every policy goes through stages. Assess which stage the current evidence indicates:

**Stage 0: Signal**
- Only high-level speeches or commentary mention the direction
- No formal document yet
- No responsible unit named
- No funding committed
- Interpretation: Direction is signaled but not yet actionable. Monitor for formal documents.

**Stage 1: Programmatic**
- A programmatic document (Central Committee opinion, Five-Year Plan, Government Work Report) states the direction
- No detailed implementation document yet
- No specific funding or pilots
- Interpretation: Direction is official but implementation path unclear. Watch for ministry documents.

**Stage 2: Implementing**
- One or more ministry or State Council documents provide specific measures
- Responsible units named
- Deadlines set
- Some funding possibly committed
- Pilots possibly designated
- Interpretation: Policy is moving toward implementation. Implementation details matter.

**Stage 3: Piloting**
- Specific pilot projects or zones designated
- Pilot implementation notices published
- Pilot results possibly reported
- Interpretation: Policy is being tested. Outcomes depend on pilot results. Do not assume nationwide application yet.

**Stage 4: Scaling**
- Pilot results are evaluated
- "复制推广" language appears in higher-level documents
- Nationwide or broader implementation measures issued
- Interpretation: Policy has moved from pilot to broader implementation. More areas and actors are now affected.

**Stage 5: Normalized**
- The policy direction is embedded in laws, regulations, or standard administrative procedures
- Routine enforcement is observed
- Budget allocations are regularized
- Interpretation: The direction is now standard. It affects ongoing operations, not just new initiatives.

**Stage 6: Adjusting**
- New documents modify, narrow, or redirect the original policy
- Language shifts from "大力推进" to "规范发展" or "优化升级"
- Some earlier measures are sunsetted or revised
- Interpretation: The policy direction is being refined or course-corrected. Earlier assumptions may no longer hold.

### How to Assess Stage

1. Find the highest-level document on the topic.
2. Find the most recent document on the topic.
3. Check for pilot designations and their status.
4. Check for "复制推广" language in any document.
5. Check for enforcement cases.
6. Check for revisions or superseding documents.
7. Map the findings to the stages above.

### Stage Implications for Output

- Stage 0-1: Emphasize uncertainty. Do not advise action based on signals alone.
- Stage 2: Note that implementation is beginning but outcomes depend on design.
- Stage 3: Warn that pilot results may differ from expectations. Do not generalize from pilots.
- Stage 4: This is often the most actionable stage, but still verify local conditions.
- Stage 5: Treat as established policy but note it affects ongoing operations.
- Stage 6: Alert the user that the direction is changing. Revisit earlier assumptions.

## Cross-Level Analysis

### Why Cross-Level Matters

A central policy document may state a direction, but the actual impact depends on how it is implemented at each level. Cross-level analysis compares the central direction with actual implementation at the ministry, provincial, and municipal levels.

### Cross-Level Comparison Method

1. **Identify the central direction**: Find the S-level or A-level source that states the policy.
2. **Find ministry implementation**: Search for A-level implementation documents from relevant ministries.
3. **Find provincial implementation**: Search for B-level implementation documents from relevant provinces.
4. **Find municipal/park implementation**: Search for C-level notices, project applications, and procurement information.
5. **Compare implementation tools across levels**:
   - Does the ministry document add specific measures, funding, pilots, or deadlines not in the central document?
   - Does the provincial document adapt the direction to local conditions, or simply repeat central language?
   - Does the municipal/park level have actual project tenders, application notices, or procurement that indicate real resource commitment?
   - Are there discrepancies between what the central document says and what local implementation does?

### Cross-Level Red Flags

- Provincial document that only repeats central language without local adaptation → likely low implementation energy
- Municipal document that adds ambitious targets not in the central or provincial document → possible overreach or signal ambition
- Absence of any implementation document below the central level → policy may be stalled
- Large gap between central deadline and local implementation timeline → implementation delay
- Conflicting direction between levels → need conflict resolution

### Cross-Level Evidence Minimums

- For central policy claims: at least one S-level or A-level source
- For local opportunity claims: S-level or A-level source PLUS at least one B-level or C-level source showing actual implementation
- For enforcement trend claims: at least one regulatory or judicial source
- Never claim local opportunity exists based on central language alone

## Conflict Resolution

### When Conflicts Arise

Conflicts may appear:
- Between documents at the same level (e.g., two ministries with different emphases)
- Between documents at different levels (e.g., central and provincial with different tones)
- Between documents at different times (e.g., earlier and later documents with different directions)
- Between policy signals and enforcement data (e.g., policy supports but enforcement penalizes)

### Resolution Rules

1. **Recency rule**: When two documents at the same level conflict, prefer the newer one.
2. **Hierarchy rule**: When documents at different levels conflict, prefer the higher-level one. S > A > B > C > D > E.
3. **Formality rule**: When documents of the same level and recency conflict, prefer the more formal one (law > regulation > opinion > notice > speech).
4. **Specificity rule**: When general and specific documents conflict, prefer the more specific one if it is issued by the relevant authority for the specific matter.
5. **Enforcement rule**: When policy signals and enforcement data conflict, note the conflict explicitly. Enforcement data reflects actual behavior; policy signals reflect intent.
6. **Joint issuance rule**: A jointly issued document carries more weight than a singly issued document at the same level.

### Documenting Conflict

When a conflict is identified:

1. State the conflicting sources explicitly.
2. State which rule applies and why.
3. State the resolution conclusion.
4. Note what the conflict itself may signal (e.g., policy transition, inter-ministry disagreement, central-local gap).

## Output Structure Requirements

### Universal Output Structure

Every answer must follow this structure:

```
## Conclusion
[One to three sentences stating the direct answer to the user's question]

## Evidence Chain
[Structured evidence links as specified above]

## Explanation
[Plain-language explanation of the conclusion and evidence]

## Policy Language Breakdown
[If policy wording is central to the question, break down key phrases with plain-language interpretation]

## Implications
[What this means in practice]

## Risks and Limitations
[What cannot be inferred, what might change, what the evidence does not support]

## Action Suggestions
[Only if requested by the user; label as suggestions, not predictions]

## Follow-up Sources
[Specific documents, institutions, or data to monitor]
```

### Output Rules

1. Always lead with the conclusion.
2. Never bury uncertainty in footnotes; state it in the risks section.
3. Every policy phrase interpretation must reference the policy_language_lexicon.md entry.
4. If the evidence chain is incomplete, say so explicitly rather than guessing.
5. Action suggestions must be conditional ("If X happens, then consider Y") not predictive ("X will happen, so do Y").
6. Never offer guarantees about investment returns, business success, or policy outcomes.
7. For temporal claims, always state the time frame and the basis for the estimate.
8. For comparative claims (e.g., province vs. province), present the comparison framework explicitly.

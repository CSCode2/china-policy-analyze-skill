# Evidence Level System

## Overview

The evidence level system (L0-L5) classifies the strength of evidence supporting a claim. Every substantive claim in an answer must be tagged with its evidence level. This allows the reader to immediately assess how well-supported each claim is.

## Evidence Levels

### L0: No Evidence

**Definition**: The claim has no supporting evidence from any source. It is speculation, personal opinion, or unsupported assertion.

**When to use**:
- The system is expressing a general observation without any specific source
- The user asked for speculation explicitly and the system is providing it with full disclaimer
- No relevant source could be found after searching

**Output marking**: Must be explicitly labeled as "无证据支撑" (no evidence support)

**Restrictions**:
- L0 claims must never be presented as conclusions
- L0 claims must never influence action suggestions
- If a key claim is L0, the answer must state that the evidence is insufficient

**Example**:
> Claim: "The government may introduce new subsidies for the semiconductor industry in Q3."
> Evidence Level: L0 — No official document or credible source supports this specific timeline. This is speculative.

---

### L1: Indirect Evidence

**Definition**: The claim is supported only by indirect signals — lower-level sources, E-level commentary, or logical inference without direct documentary evidence.

**When to use**:
- The only available sources are E-level (commercial media, self-media, market commentary)
- The claim is a logical inference from related but not directly applicable evidence
- The claim is based on historical analogy without direct documentary support

**Output marking**: Must be labeled as "间接证据" (indirect evidence) with the source level noted

**Restrictions**:
- L1 claims cannot be used to support action suggestions without strong qualification
- L1 claims must note the indirect nature of the evidence
- Multiple L1 claims cannot be combined to create the appearance of L2+ evidence

**Example**:
> Claim: "Several provinces are likely to implement the central carbon policy based on their previous track records."
> Evidence Level: L1 — Based on E-level analysis and historical patterns, not on actual provincial implementation documents.

---

### L2: Single-Source Documentary Evidence

**Definition**: The claim is supported by one specific document from a credible source (S/A/B/C level), but without corroboration from additional sources.

**When to use**:
- One official document directly supports the claim
- No other source confirms, contradicts, or expands on the claim
- The document is current and not superseded

**Output marking**: Labeled as "单一文件证据" (single-document evidence) with the source citation

**Restrictions**:
- L2 claims about central policy direction are acceptable but should note the single-source limitation
- L2 claims about local implementation should be treated cautiously — one document does not confirm actual implementation
- L2 claims that could be affected by newer documents should note the recency check status

**Example**:
> Claim: "The 14th Five-Year Plan identifies quantum computing as a strategic frontier."
> Evidence Level: L2 — Directly supported by the 14th FYP text. No contradiction from other sources, but the claim is based on a single document.

---

### L3: Multi-Source Convergent Evidence

**Definition**: The claim is supported by two or more independent sources from S/A/B/C levels that converge on the same conclusion.

**When to use**:
- Multiple official documents from different issuing bodies support the claim
- A central document and its ministry-level implementation document both support the claim
- A policy document and enforcement data both support the claim
- Documents at different levels (e.g., central and provincial) both support the claim

**Output marking**: Labeled as "多源交汇证据" (multi-source convergent evidence) with all source citations

**Restrictions**:
- Sources must be genuinely independent (not the same document republished by different agencies)
- If sources converge but differ in emphasis, note the differences
- L3 is generally sufficient for most policy claims

**Example**:
> Claim: "The central government is actively promoting new energy vehicle development with both policy support and funding commitments."
> Evidence Level: L3 — Supported by the 14th FYP (S-level), NDRC implementation opinions (A-level), and MOF subsidy notices (A-level).

---

### L4: Multi-Source Convergent Evidence with Implementation Verification

**Definition**: The claim is supported by L3-level evidence PLUS evidence of actual implementation (funding disbursed, projects approved, enforcement actions taken, pilots operational).

**When to use**:
- L3 evidence exists AND there is C-level evidence of actual implementation
- L3 evidence exists AND there are enforcement cases confirming the policy is being executed
- L3 evidence exists AND official data confirms the policy effect

**Output marking**: Labeled as "多源交汇+实施验证证据" (multi-source convergent + implementation verification evidence)

**Restrictions**:
- Implementation evidence must be from the relevant geographic scope (national implementation evidence for national claims, provincial for provincial claims)
- Implementation evidence must be current (not from a period that may have been superseded)
- L4 is the minimum level for confident claims about what is actually happening on the ground

**Example**:
> Claim: "Subsidies for new energy vehicles are being actively disbursed at the provincial level."
> Evidence Level: L4 — Supported by central and ministry documents (L3) PLUS provincial fund disbursement notices and project approval records (C-level implementation evidence).

---

### L5: Comprehensive Evidence with Outcome Data

**Definition**: The claim is supported by L4-level evidence PLUS official outcome data that confirms the policy effect has occurred as claimed.

**When to use**:
- L4 evidence exists AND NBS, PBOC, or other official statistics confirm the claimed effect
- L4 evidence exists AND audit or evaluation reports confirm the outcome
- L4 evidence exists AND Supreme People's Court or other judicial data confirms the enforcement trend

**Output marking**: Labeled as "完整证据链+结果数据" (complete evidence chain + outcome data)

**Restrictions**:
- Outcome data must be from official statistical sources, not market estimates
- Outcome data must cover the relevant scope and time period
- Even L5 claims must note limitations (data may have measurement issues, attribution may not be fully causal)

**Example**:
> Claim: "China's NEV production has increased substantially as a result of policy support."
> Evidence Level: L5 — Supported by policy documents (L3), implementation evidence (L4), AND NBS data showing NEV production growth figures.

---

## Usage Rules

### Rule 1: Tag Every Claim

Every substantive claim in an answer must be tagged with its evidence level. This applies to:
- Claims about what a policy says
- Claims about what a policy means
- Claims about implementation status
- Claims about effects and outcomes
- Claims about future developments

### Rule 2: Minimum Evidence Level for Claim Types

| Claim Type | Minimum Evidence Level |
|-----------|----------------------|
| What a document says (original wording) | L2 (single document) |
| What a policy means (interpretation) | L3 (multi-source) or L2 with explicit caveats |
| Implementation status | L4 (implementation verification) |
| Policy effect on the ground | L4 (implementation verification) |
| Market or economic outcome | L5 (outcome data) |
| Future prediction | L1 maximum for specific predictions; L3 for directional trends |

### Rule 3: Evidence Level Determines Confidence Language

| Evidence Level | Allowed Confidence Language |
|---------------|---------------------------|
| L0 | "No evidence; purely speculative" |
| L1 | "Possible but unverified"; "based on indirect signals" |
| L2 | "Supported by one source"; "directionally indicated" |
| L3 | "Supported by multiple sources"; "convergent evidence suggests" |
| L4 | "Supported by multiple sources and implementation evidence"; "actively being implemented" |
| L5 | "Confirmed by policy documents, implementation, and outcome data" |

### Rule 4: Downgrade When Uncertain

If there is any reason to doubt the evidence (source conflict, recency concern, scope mismatch), downgrade the evidence level by one step and note the reason.

### Rule 5: Never Upgrade Through Volume

Multiple L1 sources do not create an L3 claim. Multiple E-level sources discussing the same point do not create L2 evidence. Source quality matters more than quantity for evidence level determination.

### Rule 6: Explicit About Missing Links

If the evidence chain is incomplete (e.g., you have L3 evidence but are missing implementation verification), state explicitly what is missing and what evidence level the current chain supports.

---
name: china-policy-analyze
description: Use this skill when the user asks about Chinese economic policy, central policy documents, Five-Year Plans, Xi Jinping's economic speeches, policy language interpretation, local policy implementation, regulatory signals, economic cases, or opportunity analysis based on official Chinese sources.
---

# Purpose

This skill helps the agent answer questions and produce analysis based on Chinese official policy documents, speeches, economic meetings, laws, regulations, judicial cases, enforcement notices, and official economic data.

It is designed for:
- policy Q&A;
- policy language interpretation;
- Chinese economic policy reasoning;
- local implementation comparison;
- regulatory and judicial signal analysis;
- opportunity analysis for study, career, research, entrepreneurship, and project planning.

# Real-Time Data Acquisition

This skill supports both local corpus lookup AND live web fetching from official sources.

## When to fetch live data

Before answering a policy question, check data freshness:
1. Look at the most recent file modification time in `corpus/metadata/` or `reports/`
2. If the user asks about a topic where the local data is older than today, or where the answer might depend on very recent policy changes, proactively fetch from official websites
3. If the user explicitly asks about "latest" or "recent" policies, always supplement with live fetching

## How to fetch live data

The project provides fetching tools at `scripts/_run_daily_update.py`. You can:
1. Run the full update: `cd /root/china-policy-analyze-skill && source venv/bin/activate && CPI_MAX_DOCS=5 python scripts/_run_daily_update.py`
2. Or fetch a specific document manually using Python:
   ```python
   from china_policy_skill.fetch.fetch_html import HTMLFetcher
   from china_policy_skill.parse.html_to_md import HTMLToMarkdown
   fetcher = HTMLFetcher(timeout=15, rate_limit_delay=1.0)
   result = fetcher.fetch('https://www.gov.cn/zhengce/content/202604/content_XXXXXXX.htm')
   parser = HTMLToMarkdown()
   markdown = parser.convert(result.html, result.url)
   ```
3. Key source URLs are listed in `config/sources.yaml`

## Data freshness rules

- Local corpus data is always the baseline — use it first
- If local data covers the user's question adequately, no need to fetch live
- If the question involves events or policies after the last corpus update, fetch live
- Always tell the user whether your answer is based on local corpus data or live-fetched data
- Respect rate limits: never fetch more than 10 pages in one session
- Government websites only display text in HTML — extract directly, do not expect PDF downloads
- Store any newly fetched documents in the corpus (html + md + txt formats)

# Core Rules

1. Prefer official sources over commentary.
2. Always distinguish:
   - original wording;
   - structured interpretation;
   - reasonable inference;
   - personal advice;
   - uncertainty.
3. Never claim certainty about future economic outcomes.
4. Never equate policy support with guaranteed business success.
5. Never provide illegal or evasive advice.
6. For every important claim, cite or identify the source document, institution, date, and relevant passage.
7. When sources conflict, prefer newer, higher-level, more formal documents.
8. For local policy analysis, compare actual implementation tools, not slogans only.
9. For policy language, interpret wording strength based on document hierarchy, context, responsible units, deadlines, funding, projects, pilots, and enforcement signals.

# Source Priority

S-level:
- Central Committee documents
- Five-Year Plans
- Government Work Reports
- Central Economic Work Conference
- Xi Jinping's important speeches and articles
- National laws and administrative regulations

A-level:
- State Council documents
- NDRC, MOF, PBOC, NBS, MIIT, MOST, MOFCOM, NFRA, CSRC, SAMR, MPS, MOJ
- Supreme People's Court and Supreme People's Procuratorate
- People's Daily, Xinhua, Qiushi, People.cn speech database

B-level:
- Provincial governments and provincial departments
- Provincial courts, procuratorates, public security departments
- Major city governments

C-level:
- Municipal departments, industrial parks, high-tech zones, project application notices, local procurement and tender information

D-level:
- Official interpretations, press conferences, expert explanations

E-level:
- Commercial media, self-media, market commentary. Use E-level only as leads, not as primary evidence.

# Analysis Procedure

For each user question:

1. Classify the task:
   - factual policy Q&A
   - policy language interpretation
   - policy trend analysis
   - local implementation comparison
   - industry opportunity analysis
   - legal/regulatory risk analysis
   - personal career/research/entrepreneurship planning

2. Retrieve relevant evidence:
   - central documents;
   - speeches/articles;
   - ministry implementation documents;
   - local documents if relevant;
   - laws/regulations/cases if risk or enforcement is relevant;
   - official data if macro judgment is involved.

3. Build the evidence chain:
   - document title;
   - issuing body;
   - publish date;
   - source level;
   - relevant wording;
   - policy language phrases;
   - implementation tools.

4. Interpret:
   - What is explicitly stated?
   - What does the wording imply?
   - What policy stage is this?
   - What can be inferred?
   - What cannot be inferred?

5. Output:
   - conclusion first;
   - evidence chain;
   - plain-language explanation;
   - policy language breakdown;
   - implications;
   - risks;
   - action suggestions if requested;
   - follow-up sources to monitor.

# Policy Language Interpretation

Do not interpret policy wording mechanically. Use the policy language lexicon and context.

For example:
- "持续推进" usually means continuity, not sudden acceleration.
- "大力发展" indicates strong support, but still requires implementation evidence.
- "积极稳妥" means the direction is supported but risk control is important.
- "有序推进" means staged implementation and avoidance of disorder.
- "规范发展" means development and regulation happen together.
- "严厉打击" is a strong enforcement signal.
- "试点探索" means uncertainty remains; local pilots matter.
- "复制推广" means the policy has moved from pilot to broader implementation.

Always consider:
- document level;
- issuing body;
- section location;
- whether there are responsible units;
- whether there are deadlines;
- whether there is funding;
- whether there are pilots;
- whether there are cases or enforcement actions.

# Output Boundary

Do not:
- impersonate any leader, institution, ministry, court, procuratorate, or police authority;
- fabricate official positions;
- provide guaranteed investment or business outcomes;
- advise on illegal conduct, evasion, fraud, fake applications, regulatory arbitrage, or enforcement avoidance;
- treat unofficial commentary as official policy.

# Quality Checklist

Before answering:
- Did I use official sources first?
- Did I separate original wording from interpretation?
- Did I explain policy phrases in plain language?
- Did I identify uncertainty?
- Did I avoid overclaiming?
- Did I check recency?
- Did I include local implementation evidence if discussing local opportunities?
- Did I include legal/regulatory evidence if discussing risk?

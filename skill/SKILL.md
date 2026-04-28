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

1. If the user asks about "latest" or "recent" policies, always fetch live
2. If the user's question involves policies or events more recent than the corpus, fetch live
3. If local data covers the question adequately, no need to fetch — but always tell the user whether the answer is from local corpus or live-fetched

## How to fetch live data — WebFetch method (works on ANY agent)

**Use your agent's built-in WebFetch tool.** You do NOT need Python or any project-specific tools. Just fetch the URLs below and read the content directly.

### Step 1: Find latest policy titles and dates

Fetch these listing pages to discover what's new:

**Confirmed working (tested 2026-04-28):**
```
https://www.gov.cn/zhengce/                           ← 国务院：最新政策列表
https://www.gov.cn/zhengce/YYYYMM/content_XXXXXXX.htm ← 国务院：具体文件内容
https://www.ndrc.gov.cn/xwdt/xwfb/                    ← 发改委：新闻发布
https://www.mofcom.gov.cn/xwfb/                       ← 商务部：新闻发布
https://www.miit.gov.cn/xwdt/gxdt/sjdt/              ← 工信部：司局动态
http://jhsjk.people.cn/                               ← 习近平重要讲话数据库
https://www.news.cn/politics/                          ← 新华网时政频道
https://www.stats.gov.cn/sj/                          ← 统计局：数据
https://www.mfa.gov.cn/wjbxw/                         ← 外交部：新闻
https://www.mee.gov.cn/ywdt/                          ← 生态环境部：新闻
https://www.nra.gov.cn/xwzx/                          ← 金融监管总局：新闻
https://www.csrc.gov.cn/csrc/c100032/common_list.shtml ← 证监会：发布
https://www.moj.gov.cn/pub/sfbgw/                     ← 司法部：政策文件
https://www.court.gov.cn/zixun/                       ← 最高法：资讯
https://www.spp.gov.cn/                               ← 最高检：首页
https://www.samr.gov.cn/                              ← 市场监管总局：首页
```

Note: Some ministry sites return actual content only from specific sub-paths, not from their top-level news listing URLs. If a URL returns very little content (< 200 chars), try the ministry homepage instead and follow links from there.

These listing pages reliably return HTML with titles and dates. Read them to find relevant document titles.

### Step 2: Fetch specific document content

**The correct URL pattern for gov.cn policy documents is:**
```
https://www.gov.cn/zhengce/YYYYMM/content_XXXXXXX.htm
```

**NOT** `/zhengce/content/YYYYMM/` (that pattern returns 404).

To find the exact content URL, fetch the listing page at `https://www.gov.cn/zhengce/` and look for links containing `/content_` in the HTML. The href will be something like `/zhengce/202604/content_7066998.htm` — prefix with `https://www.gov.cn`.

**If you get a 404 on a gov.cn URL:**
- The URL path might be wrong. Try changing `/zhengce/content/YYYYMM/` to `/zhengce/YYYYMM/`
- Try searching on news.cn: `https://www.news.cn/politics/` — Xinhua often republishes the same content
- Try the gov.cn search: `https://sousuo.gov.cn/s.htm?t=govall&q=关键词` (may not work with WebFetch)

**Confirmed working examples:**
```
https://www.gov.cn/zhengce/202604/content_7066998.htm   ← 中办国办：新就业群体（2026-04-26）
https://www.gov.cn/zhengce/202604/content_7066483.htm   ← 国发〔2026〕7号 服务业扩能提质（2026-04-21）
https://www.gov.cn/zhengce/content/202604/content_7066483.htm  ← 同一文件，也可访问（部分URL两种路径都可用）
```

### Step 3: For Xi Jinping speeches and important meetings

```
http://jhsjk.people.cn/     ← 重要讲话数据库 (reliable, returns HTML with dates)
https://www.news.cn/politics/ ← 新华网时政 (reliable, full article content)
```

### What does NOT work

These sites actively block non-browser requests from data center IPs. No workaround exists:

- `www.pbc.gov.cn` (央行) — 403 Forbidden (IP-level blocking)
- `www.customs.gov.cn` (海关总署) — connection timeout (IP-level blocking)
- `www.mps.gov.cn` (公安部) — 521 server error (behind cloud protection)

These sites return near-empty content (JS-rendered, no useful text without a real browser):

- `www.most.gov.cn` (科技部) — 157 chars, empty shell
- `www.mohrss.gov.cn` (人社部) — 989 chars, empty shell

For these, rely on the local corpus data, or check the gov.cn policy listing page which aggregates documents from all ministries.

### Data freshness rules

- Local corpus data is always the baseline — use it first
- If local data covers the question adequately, no need to fetch live
- Always tell the user whether your answer is based on local corpus or live-fetched data
- Respect rate limits: never fetch more than 10 pages in one session
- If a fetched page has too little content (< 200 chars), it's likely a listing page — find and follow the actual content links

## How to fetch live data — Python method (only if Python environment is available)

**Note: Python HTMLFetcher uses browser-like headers and CAN access more sites than bare WebFetch:**
- Judicial/Legal: `www.moj.gov.cn`, `www.court.gov.cn`, `www.spp.gov.cn` — all work with Python
- Market regulation: `www.samr.gov.cn` — works with Python
- But these sites still block at IP level (no workaround): `www.pbc.gov.cn` (403), `www.customs.gov.cn` (timeout)
- JS-rendered sites still return empty shells: `www.most.gov.cn`, `www.mohrss.gov.cn`

Python's main advantage: browser-like headers + automated batch fetching + HTML-to-markdown conversion.

If the full project is installed with Python:
```bash
cd china-policy-analyze-skill && source venv/bin/activate && CPI_MAX_DOCS=5 python scripts/_run_daily_update.py
```
Or fetch a specific URL:
```python
from china_policy_skill.fetch.fetch_html import HTMLFetcher
from china_policy_skill.parse.html_to_md import HTMLToMarkdown
fetcher = HTMLFetcher(timeout=15, rate_limit_delay=1.0)
result = fetcher.fetch('https://www.gov.cn/zhengce/202604/content_XXXXXXX.htm')
parser = HTMLToMarkdown()
markdown = parser.convert(result.html or '', result.url)
```
Source URLs are listed in `config/sources.yaml`.

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
7. **MANDATORY: Every document reference in all output MUST include its issue date.** Format: 《标题》（发文号， YYYY年M月D日）. If no doc_number: 《标题》（YYYY年M月D日）. If date unknown: write 日期不详. Never omit the date.
8. When sources conflict, prefer newer, higher-level, more formal documents.
9. For local policy analysis, compare actual implementation tools, not slogans only.
10. For policy language, interpret wording strength based on document hierarchy, context, responsible units, deadlines, funding, projects, pilots, and enforcement signals.

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
   - evidence chain (every source MUST include 《title》（doc_number， date） format);
   - plain-language explanation;
   - policy language breakdown;
   - implications;
   - risks;
   - action suggestions if requested;
   - follow-up sources to monitor.

# Citation Format — MANDATORY

Every document reference in all output (responses, cards, reports) MUST follow this format:

- With doc_number: 《国务院关于推进服务业扩能提质的意见》（国发〔2026〕7号，2026年4月14日）
- Without doc_number: 《道路机动车辆生产企业及产品》新批次公告（2026年3月28日）
- Date unknown: 《某文件》（日期不详）

The date is NEVER optional. Every cited document, signal, fact, or claim must show when it was issued.

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
- Did I include the issue date on EVERY document reference? (MANDATORY)
- Did I include local implementation evidence if discussing local opportunities?
- Did I include legal/regulatory evidence if discussing risk?

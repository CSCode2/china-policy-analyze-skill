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

**Confirmed working — both listing and sub-pages (tested 2026-04-28 with Python HTMLFetcher):**
```
# 国务院
https://www.gov.cn/zhengce/                                       ← 最新政策列表
https://www.gov.cn/zhengce/YYYYMM/content_XXXXXXX.htm             ← 具体文件（注意：/zhengce/YYYYMM/ 不是 /zhengce/content/YYYYMM/）

# 发改委
https://www.ndrc.gov.cn/xwdt/xwfb/                                ← 新闻发布列表
  子页面示例: /xwdt/202604/t20260427_1389482.html               ✅ 实测md=483

# 商务部
https://www.mofcom.gov.cn/xwfb/                                   ← 新闻发布列表
  子页面示例: /xwfb/...                                           ✅ 实测md=1761

# 工信部
https://www.miit.gov.cn/                                           ← 首页（新闻链接在首页）
  子页面示例: /xwdt/gxdt/sjdt/art/2026/art_xxx.html             ✅ 实测md=1932

# 司法部
https://www.moj.gov.cn/                                            ← 首页（政策链接在首页）
  子页面: /pub/sfbgw/zwgkzt/...                                  ✅ 实测md=8372

# 最高人民法院
https://www.court.gov.cn/                                          ← 首页
  子页面: /zixun/.../content_XXXXXXX.html                        ✅ 实测md=1923

# 最高人民检察院
https://www.spp.gov.cn/                                            ← 首页
  子页面: /spp/xwfb/.../index.shtml                              ✅ 实测md=14641

# 市场监管总局
https://www.samr.gov.cn/                                           ← 首页
  子页面: /xw/zj/art/2026/art_xxx.html                           ✅ 实测md=684

# 生态环境部
https://www.mee.gov.cn/                                            ← 首页
  子页面: /ywdt/hjzx/.../t20260427_XXXXXX.shtml                  ✅ 实测md=10845

# 外交部
https://www.mfa.gov.cn/wjbxw/                                     ← 外交部发言人表态
  子页面: /web/wjbxw_673016/.../tXXXXXXX.shtml                   ✅ 实测md=15113

# 统计局
https://www.stats.gov.cn/sj/zxfb/                                 ← 统计发布
  子页面: /sj/zxfb/202604/t20260427_XXXXXXX.html                 ✅ 实测md=12645

# 金融监管总局
https://www.nra.gov.cn/xwzx/                                      ← 新闻中心
  子页面: /xwzx/gdt/.../art/2026/art_xxx.html                    ✅ 实测md=1749

# 证监会
https://www.csrc.gov.cn/csrc/c100032/common_list.shtml             ← 发布列表
  子页面: /csrc/c106311/cXXXXXXX/content.shtml                    ✅ 实测md=975

# 人民银行（央行）
https://www.pbc.gov.cn/                                            ← 首页（栏目链接在首页）
  ⚠️ 短路径如 /goutongjiaoliu/ → 403! 必须用完整栏目路径：
  新闻发布: /goutongjiaoliu/113456/113469/index.html              ✅ 实测md=2538
  具体新闻: /goutongjiaoliu/113456/113469/20260425XXXX/index.html ✅ 实测md=1861
  货币政策: /rmyh/105145/index.html                               ✅ 实测md=2210
  公告信息: /rmyh/105208/index.html                               ✅ 实测md=4044
  法律法规: /tiaofasi/144941/index.html                           ✅ 实测md=5034

# 习近平重要讲话
http://jhsjk.people.cn/                                            ← 重要讲话数据库     ✅ 首页+子页面
```

**Important URL patterns:**
- Some ministry listing pages use JS rendering — their HTML may not contain article links. In that case, fetch the ministry **homepage** (not the listing sub-path), which usually has the latest news links embedded in the HTML.
- **pbc.gov.cn**: Short paths like `/goutongjiaoliu/` return 403 from CDN. You MUST use the **full column path** (e.g., `/goutongjiaoliu/113456/113469/index.html`). Find these paths by fetching the homepage and following links.

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

### What does NOT work — and how to fall back to WeChat

These sites actively block non-browser requests from data center IPs:

| Blocked site | Error | WeChat fallback account |
|-------------|-------|------------------------|
| `www.customs.gov.cn` (海关总署) | 412 | `中国海关发布` |
| `www.mps.gov.cn` (公安部) | 521 | (no equivalent WeChat account) |

These sites return near-empty content (JS-rendered):

| Empty site | Chars | WeChat fallback account |
|-----------|-------|------------------------|
| `www.most.gov.cn` (科技部) | 157 | `科技部` |
| `www.mohrss.gov.cn` (人社部) | 989 | `人社部` |

**FALLBACK RULE (mandatory):** When WebFetch to any official site fails (4xx/5xx error, empty content <200 chars, or timeout), you MUST try WeChat search before giving up:

```bash
# Search by keyword (general)
source venv/bin/activate && cpi wechat-search "关键词" --fetch --json

# Search by known account (faster, more accurate)
source venv/bin/activate && cpi wechat-search "关键词" -a "中国人民银行" --fetch --json

# Search by category
source venv/bin/activate && cpi wechat-search "降准" -c economy_finance --fetch --json
```

For the 4 blocked sites above, skip WebFetch entirely and go straight to WeChat search with the corresponding account.

**pbc.gov.cn (央行) works!** Previously marked as blocked because short paths like `/goutongjiaoliu/` return 403 from CDN. But full column URLs (e.g., `/goutongjiaoliu/113456/113469/index.html`) work perfectly — fetch the homepage first to discover the correct paths.

### Data freshness rules

- Local corpus data is always the baseline — use it first
- If local data covers the question adequately, no need to fetch live
- Always tell the user whether your answer is based on local corpus or live-fetched data
- Respect rate limits: never fetch more than 10 pages in one session
- If a fetched page has too little content (< 200 chars), it's likely a listing page — find and follow the actual content links

## How to fetch live data — Python method (only if Python environment is available)

**Note: Python HTMLFetcher uses browser-like headers and CAN access more sites than bare WebFetch:**
- PBC: `www.pbc.gov.cn` — works with full column paths (NOT short paths like /goutongjiaoliu/)
- Judicial/Legal: `www.moj.gov.cn`, `www.court.gov.cn`, `www.spp.gov.cn` — all work with Python
- Market regulation: `www.samr.gov.cn` — works with Python
- Still blocked: `www.customs.gov.cn` (412), `www.mps.gov.cn` (521)
- JS-rendered empty shells: `www.most.gov.cn`, `www.mohrss.gov.cn`

Python's main advantage: browser-like headers + automated batch fetching + HTML-to-markdown conversion.

### WeChat Public Account (微信公众号) Article Search

**When official websites fail to return content, search WeChat public accounts for the same policy content.** Many official and professional accounts post full policy texts on WeChat.

#### CLI method (quickest — use this first)

```bash
# Search by keyword (general)
source venv/bin/activate && cpi wechat-search "关键词" --fetch --json

# Search by known account (faster, more accurate)
source venv/bin/activate && cpi wechat-search "利率政策" -a "中国人民银行" --fetch --json

# Search by category
source venv/bin/activate && cpi wechat-search "降准" -c economy_finance --fetch --json

# Search without fetching full content (titles + abstracts only)
source venv/bin/activate && cpi wechat-search "服务业扩能提质" --max 5

# Get human-readable output (default)
source venv/bin/activate && cpi wechat-search "无人机实名制" -a "中国政府网" --fetch
```

#### Python method (if you need programmatic access)

```python
from china_policy_skill.fetch.fetch_wechat import WeChatSearcher

ws = WeChatSearcher()

# General keyword search
articles = ws.search_and_fetch("关键词", max_results=3)

# Search by known account
articles = ws.search_by_account_and_fetch("中国人民银行", keyword="货币政策")

# Search by category
articles = ws.search_by_category_and_fetch("economy_finance", keyword="降准")
```

#### Account directory（按公众号搜索，更快更准）

40 verified high-quality policy WeChat accounts stored in `config/wechat_accounts.yaml`:

| Category | Key accounts | Authority |
|----------|-------------|-----------|
| central_policy | 中国政府网, 国务院公报, 新华视点, 人民日报, 求是网, 经济日报 | S/A |
| economy_finance | 国家发改委, 财政部, 中国人民银行, 金融时报 | A |
| industry_regulation | 工信微报, 科技部, 市场监管总局, 证监会发布, 金融监管总局 | A |
| trade_foreign | 商务部, 外交小灵通, 中国海关发布 | A |
| people_livelihood | 生态环境部, 交通运输部, 农业农村部, 住建部, 人社部, 教育部, 国家卫健委 | A |
| law_justice | 司法部, 最高人民法院, 最高人民检察院, 中国普法 | A |
| professional | 北大法律信息网, 威科先行, 中伦视界, 中国法律评论, 中国改革报 | B |

```python
from china_policy_skill.fetch.fetch_wechat import WeChatSearcher

ws = WeChatSearcher()

# Search by account name (uses optimized search_tip from directory)
articles = ws.search_by_account("中国人民银行", keyword="利率", max_results=3)
articles = ws.search_by_account_and_fetch("中国人民银行", keyword="货币政策")

# Search across all accounts in a category
articles = ws.search_by_category("economy_finance", keyword="降准")
articles = ws.search_by_category_and_fetch("law_justice", keyword="司法解释")

# Look up account info
acc = ws.get_account("中国政府网")
# WeChatAccount(name='中国政府网', wechat_id='zhengfuweixin', authority='S', ...)

# Find accounts by topic keyword
accounts = ws.find_accounts_by_topic("货币政策")
# Returns accounts whose topics contain "货币政策"

# Browse the full directory
for category, accounts in ws.account_directory.items():
    for acc in accounts:
        print(f"  {acc.name} ({acc.authority}): {acc.desc}")
```

**How it works:**
1. Searches `weixin.sogou.com` (搜狗微信搜索) — works reliably, returns titles + abstracts
2. Follows Sogou's redirect links → extracts the real `mp.weixin.qq.com` article URL from obfuscated JS
3. Fetches the full article directly from `mp.weixin.qq.com` — returns complete policy text

**Limitations:**
- Sogou search rate limit: ~10 queries per session before needing a pause
- Article URLs contain timestamps and signatures — they may expire after ~24 hours
- Some WeChat articles may have been deleted by the publisher
- Always cite the original official source when using WeChat content

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

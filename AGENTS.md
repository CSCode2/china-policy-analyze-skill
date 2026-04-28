# Agent Rules for China Policy Analyze Skill

## Meta Rule — HIGHEST PRIORITY

**每次对项目的任何修改，都必须同步更新服务器上运行此项目的 Hermes Agent 配置：**
- SOUL.md（/root/.hermes/SOUL.md）
- Cron 任务 prompt（hermes cron edit）
- Gateway 重启（如 SOUL.md 有改动）
- 本 AGENTS.md（如运维规则有变动）
- 验证 Hermes 配置生效

**注意：SKILL.md 是给终端用户看的，不属于 Hermes 运维配置，除非技能定义本身变更才需要同步。**

**绝对不能改了项目代码却不更新 Hermes，导致 Agent 执行时用的是过时的指令。**

## Security

- NEVER push to main directly. Always create a branch and PR.
- NEVER expose API keys in commits, PRs, or logs.
- NEVER bypass robots.txt, authentication, or rate limits.
- NEVER install untrusted packages.
- NEVER start network listeners or open ports.
- NEVER modify security configuration files without human review.
- ALWAYS use `gh` CLI for GitHub operations.
- ALWAYS run eval before merging any PR.

## Policy Content Rules

- ALWAYS cite official sources for every claim.
- ALWAYS distinguish: fact, interpretation, inference, uncertainty.
- NEVER output deterministic war date predictions.
- NEVER output investment buy/sell advice.
- NEVER encourage illegal, evasive, or regulatory-arbitrage actions.
- NEVER treat unofficial commentary as official policy.
- NEVER use "确定性机会" "一定会来" "必然爆发" — use "政策方向较明确" "可能受政策持续影响"
- Comply with Chinese laws and regulations; never assist illegal activities.

## Output Format Rules

- ALWAYS wrap document titles in 《》 in all output
- ALWAYS include document number and issue date when available
- EVERY document reference MUST include its issue date — this is MANDATORY, no exceptions
- Format example: 《国务院关于推进服务业扩能提质的意见》（国发〔2026〕7号，2026年4月14日）
- Without doc_number: 《道路机动车辆生产企业及产品》新批次公告（2026年3月28日）
- If date unknown: write 日期不详 — NEVER omit the date
- ALWAYS include evidence level (E0–E5) for claims
- ALWAYS indicate whether answer is from local corpus or live-fetched data

## Code Rules

- Follow existing code style and patterns.
- Run tests before committing.
- Record all fetch errors in corpus/metadata/fetch_errors.jsonl.
- Deduplicate using content hashes before saving.

## Data Collection Rules

- Government websites typically only display text in HTML, NOT downloadable PDF/Word files.
- ALWAYS extract text content directly from web page HTML, do NOT wait for or expect PDF downloads.
- Store each document in 3 formats under corpus/:
  - raw/{doc_id}.html — original HTML (for re-processing if needed)
  - processed/markdown/{doc_id}.md — cleaned markdown
  - processed/text/{doc_id}.txt — plain text (same content as md, no markdown syntax)
- If a page has too little content (<200 chars after extraction), it is likely a listing page, not a document page — follow its links to find the actual content page.
- Do NOT run BM25 index building — it causes OOM on 3GB RAM servers. Index building is disabled.
- Use CPI_MAX_DOCS env var to limit documents per run (default 20).

## Document Metadata

Every document must have these fields in corpus/metadata/{doc_id}.json:
- `title`: cleaned title (no website suffixes like "_中国政府网")
- `publish_date`: YYYY-MM-DD format
- `doc_number`: official number (国发〔2026〕7号, etc.) if available
- `issuing_body`: agency that issued the document (国务院, etc.)
- `doc_type`: 意见/通知/办法/规划/报告/etc.
- `organization`: broader organization
- `authority_level`: S or A
- `url`: source URL
- `content_hash`: SHA-256 for dedup

## Real-Time Data Acquisition

- Before answering policy questions, check data freshness in corpus/metadata/
- If local data is stale or user asks about "latest/recent", fetch live from official sources
- Can run: `source venv/bin/activate && CPI_MAX_DOCS=5 python scripts/_run_daily_update.py`
- Or fetch specific URLs with Python HTMLFetcher + HTMLToMarkdown
- Source URLs listed in config/sources.yaml
- Always tell user whether data is from corpus or live-fetched
- Respect rate limits: max 10 pages per session

### Judicial/Police/Credit Data Rules

1. 优先保存来源链接、摘要、类型、标签和统计结果
2. 不长期保存不必要的可识别个人信息
3. 不保存身份证号、手机号、住址、家庭关系等个人敏感信息
4. 对自然人姓名、案号、详细案情等做脱敏或最小化处理
5. 不对具体自然人做画像、评分或风险预测
6. 不把单个案件扩展为对整个行业的绝对判断
7. 只分析风险类型、监管趋势和合规边界

### Confirmed working (15 sources, tested 2026-04-28)

gov.cn | ndrc | mofcom | miit | moj | court | spp | samr | mee | mfa | stats | nra | csrc | pbc | jhsjk

**pbc.gov.cn 特殊：** 首页可访问(129K chars)，但短路径如 /goutongjiaoliu/ 返回403。必须从首页提取完整栏目路径（如 /goutongjiaoliu/113456/113469/index.html）。
**部分部委：** 列表页JS渲染无链接时，fetch首页提取文章链接。

### Not working (4 sites)

- customs.gov.cn — 412 (CDN JS challenge)
- mps.gov.cn — 521 (cloud JS challenge)  
- most.gov.cn — JS empty shell (157 bytes)
- mohrss.gov.cn — JS empty shell (989 bytes)

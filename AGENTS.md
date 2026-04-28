# Agent Rules for China Policy Analyze Skill

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
- Comply with Chinese laws and regulations; never assist illegal activities.

## Output Format Rules

- ALWAYS wrap document titles in 《》 in all output
- ALWAYS include document number and issue date when available
- Format example: 《国务院关于推进服务业扩能提质的意见》（国发〔2026〕7号，2026年4月14日）
- ALWAYS include evidence level (L1–L5) for claims
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

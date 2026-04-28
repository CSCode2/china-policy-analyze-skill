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

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

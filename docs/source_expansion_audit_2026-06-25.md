# Source expansion audit — 2026-06-25

## Scope

This audit covers the sources added by the government, city, foreign-policy, WeChat, and 本地宝 expansion. It checks source identity, canonical URLs, current accessibility, evidence for official WeChat account names, and compatibility with the repository's collection limits.

## Method

- Compared every added registry entry against the branch diff.
- Opened or requested every added website URL on 2026-06-25.
- Confirmed local-government account names against government information-disclosure pages, official new-media matrices, or authoritative public-institution pages.
- Classified access failures separately from invalid URLs because several government sites actively block automated clients.
- Re-ran YAML validation, registry tests, linting, and the full test suite after corrections.

## Corrections made

- Replaced `天津发布` with the current official name `天津政务信息发布`.
- Replaced `太原发布` with the official city new-media account `我的太原`.
- Added a dated `verification_url` to every local-government account.
- Kept 乌鲁木齐 on the current `https://www.wlmq.gov.cn` domain.
- Pointed 财政部关税司 directly to its official policy-release listing instead of the less reliable site root.
- Replaced the European Central Bank's redirecting press URL with its canonical publication-by-date URL.
- Added four-day rotating batches so a run never exceeds the repository's approximate ten-query WeChat limit.

## Accessibility results

Direct requests returned current content for most added sources, including the White House, Federal Reserve, US Treasury, Federal Register, Bank of Japan, Japan Ministry of Finance, Japan Prime Minister's Office, ECB, European Commission Trade, Bank of England, Bank of Canada, Hong Kong, Macao, and 本地宝.

The following official sources were current but presented anti-bot or firewall responses to automated clients: US Commerce, Trump's Truth Social account, Xining, Hohhot, and Haikou.

The 财政部关税司 policy listing is current through April 2026 in the official index, but returned HTTP 502 to the audit's Python client. Several Chinese government sites and Japan's METI were likewise discoverable and current through their official pages or search indexes but intermittently failed because of TLS negotiation, connection closure, or timeout behavior. These conditions are recorded in `config/sources.yaml` rather than treating the official URLs as dead.

## Source-quality safeguards

- Official government pages remain the required primary evidence for policy conclusions.
- Official WeChat accounts are fallback or complementary channels and now carry individual verification evidence dated 2026-06-25.
- 本地宝 remains an E-level, lead-only discovery source. Amounts, eligibility rules, deadlines, and application procedures must be confirmed on an official government source before use.
- Truth Social is retained only as a primary-statement source for the named account; resulting policy effects still require confirmation through formal US government channels.

## Validation

- All configuration YAML files parsed successfully.
- The directory contains 103 configured WeChat accounts.
- `python -m ruff check tests/test_source_registry.py`: passed.
- `python -m pytest -q`: 74 passed.
- `git diff --check`: passed.

## Deployment note

The repository configuration and task definitions are updated. A deployment maintainer must still synchronize the corresponding live Hermes configuration and cron prompts after review.

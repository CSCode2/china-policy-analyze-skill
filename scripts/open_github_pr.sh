#!/bin/bash
# Create a GitHub PR for policy updates
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRANCH_NAME="policy-update-$(date +%Y%m%d-%H%M%S)"
PR_TITLE="Policy update $(date +%Y-%m-%d)"
PR_TEMPLATE="${REPO_ROOT}/config/github_pr_template.md"

if [ -z "${GITHUB_TOKEN}" ]; then
    echo "ERROR: GITHUB_TOKEN not set"
    exit 1
fi

if ! command -v gh &>/dev/null; then
    echo "ERROR: gh CLI not installed"
    exit 1
fi

cd "${REPO_ROOT}"

git checkout -b "${BRANCH_NAME}"

git add -A
git commit -m "Policy update $(date +%Y-%m-%d)" || true

git push -u origin "${BRANCH_NAME}"

BODY=""
if [ -f "${PR_TEMPLATE}" ]; then
    BODY=$(cat "${PR_TEMPLATE}")
fi

gh pr create \
    --title "${PR_TITLE}" \
    --body "${BODY}" \
    --base main \
    --head "${BRANCH_NAME}"

echo "PR created on branch ${BRANCH_NAME}"

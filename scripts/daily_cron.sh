#!/bin/bash
set -e
cd /root/china-policy-analyze-skill

TODAY=$(date +%Y-%m-%d)
BRANCH="daily/${TODAY}"
REPORT="reports/daily_${TODAY}.md"

echo "=== Step 1: Data Collection ==="
source venv/bin/activate
CPI_MAX_DOCS=15 timeout 120 python scripts/_run_daily_update.py

echo "=== Step 2: Check Result ==="
if [ ! -f "$REPORT" ]; then
    echo "[SILENT] No report file"
    exit 0
fi

NEW_DOCS=$(grep "New Documents" "$REPORT" | head -1 | grep -oP '\d+' || true)
if [ -z "$NEW_DOCS" ] || [ "$NEW_DOCS" = "0" ]; then
    echo "[SILENT] No new documents"
    exit 0
fi

echo "=== Step 3: Prepare Branch ==="
git checkout main
git pull origin main
git branch -D "$BRANCH" 2>/dev/null || true
git push origin --delete "$BRANCH" 2>/dev/null || true
git checkout -b "$BRANCH"

echo "=== Step 4: Commit ==="
git add -f reports/daily_*.md
git -c user.name="CS2" -c user.email="2984301751@qq.com" commit -m "daily: ${TODAY} 政策监测" || true

echo "=== Step 5: Push and Create PR ==="
git push -u origin "$BRANCH"
PR_URL=$(gh pr create --title "daily: ${TODAY} 政策监测" --body "详见报告" --head "$BRANCH" 2>&1) || true
echo "PR URL: $PR_URL"

PR_NUM=$(echo "$PR_URL" | grep -oP 'pull/\K\d+' || true)
if [ -z "$PR_NUM" ]; then
    PR_NUM=$(gh pr list --head "$BRANCH" --state open --json number -q ".[0].number")
fi

echo "=== Step 6: Approve and Merge ==="
if [ -n "$PR_NUM" ]; then
    gh pr comment "$PR_NUM" --body "审批通过"
    gh pr merge "$PR_NUM" --squash --delete-branch
    echo "DONE: PR#${PR_NUM} merged"
else
    echo "ERROR: Could not find PR number"
    exit 1
fi

#!/bin/bash
set -e
cd /root/china-policy-analyze-skill

TODAY=$(date +%Y-%m-%d)
BRANCH="foreign-macro/${TODAY}"
REPORT="reports/foreign_macro_${TODAY}.md"

echo "=== Step 1: Foreign Macro Data Collection ==="
source venv/bin/activate
CPI_MAX_DOCS=10 timeout 120 python scripts/_run_foreign_macro.py || true

echo "=== Step 2: Check Result ==="
if [ ! -f "$REPORT" ]; then
    echo "[SILENT] No report file"
    exit 0
fi

NEW_COUNT=$(grep "New Items" "$REPORT" | grep -oP '\d+' || true)
if [ -z "$NEW_COUNT" ] || [ "$NEW_COUNT" = "0" ]; then
    echo "[SILENT] No new foreign macro items"
    exit 0
fi

echo "=== Step 3: Prepare Branch ==="
git checkout main
git pull origin main
git branch -D "$BRANCH" 2>/dev/null || true
git push origin --delete "$BRANCH" 2>/dev/null || true
git checkout -b "$BRANCH"

echo "=== Step 4: Commit ==="
git add -f reports/foreign_macro_*.md
git -c user.name="CS2" -c user.email="2984301751@qq.com" commit -m "foreign-macro: ${TODAY} 外部宏观政策观察" || true

echo "=== Step 5: Push and Create PR ==="
git push -u origin "$BRANCH"
PR_URL=$(gh pr create --title "foreign-macro: ${TODAY} 外部宏观政策观察" --body "外部宏观政策监控报告" --head "$BRANCH" 2>&1) || true
echo "PR URL: $PR_URL"

PR_NUM=$(echo "$PR_URL" | grep -oP 'pull/\K\d+' || true)
if [ -z "$PR_NUM" ]; then
    PR_NUM=$(gh pr list --head "$BRANCH" --state open --json number -q ".[0].number")
fi

echo "=== Step 6: Approve and Merge ==="
if [ -n "$PR_NUM" ]; then
    gh pr comment "$PR_NUM" --body "审批通过：外部宏观政策监控报告"
    gh pr merge "$PR_NUM" --squash --delete-branch
    echo "DONE: PR#${PR_NUM} merged"
else
    echo "ERROR: Could not find PR number"
    exit 1
fi

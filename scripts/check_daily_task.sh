#!/bin/bash
# 每日任务检查脚本

echo "=== 每日任务检查 $(date +%Y-%m-%d) ==="
echo ""

# 1. 检查今天的 PR
echo "1. 检查今天的 PR:"
gh pr list --repo CSCode2/china-policy-analyze-skill --limit 1

echo ""

# 2. 检查最新 session
echo "2. 检查最新 session:"
SESSION=$(ls -t /root/.hermes/sessions/session_cron_97de8322e5f7_*.json | head -1)
SESSION_TIME=$(stat -c %y "$SESSION" | cut -d'.' -f1)
echo "   Session 时间: $SESSION_TIME"

# 3. 检查工具使用
echo "3. 检查工具使用:"
python3 << PYTHON
import json
with open("$SESSION") as f:
    data = json.load(f)
    msgs = data['messages']
    
    # 工具使用
    tools = []
    for m in msgs:
        if m.get('role') == 'assistant':
            for t in m.get('tool_calls', []):
                tools.append(t['function']['name'])
    
    print(f"   terminal 次数: {tools.count('terminal')}")
    print(f"   execute_code 次数: {tools.count('execute_code')}")
    
    # 最终回复
    for m in reversed(msgs):
        if m.get('role') == 'assistant' and not m.get('tool_calls'):
            print(f"   最终回复: {m.get('content', '')[:50]}...")
            break
PYTHON

echo ""

# 4. 检查报告文件
echo "4. 检查今天的报告:"
TODAY=$(date +%Y-%m-%d)
REPORT="/root/china-policy-analyze-skill/reports/daily_${TODAY}.md"
if [ -f "$REPORT" ]; then
    NEW_DOCS=$(grep "New Documents" "$REPORT" | head -1)
    echo "   报告存在: $NEW_DOCS"
else
    echo "   报告不存在"
fi

echo ""
echo "=== 检查完成 ==="

# Hermes Agent 部署指南 / Hermes Agent Deployment Guide

本文档指导 AI Agent 在新服务器上完成 Hermes 的部署。**所有密钥和凭证在部署时由用户提供，本文档不含任何硬编码密钥。**

## 0. 前提条件

新服务器应满足：
- Linux (Ubuntu/Debian 推荐)
- Python 3.10+
- 3GB+ RAM
- 可访问外网 (GitHub, OpenRouter, 中国政府网站)
- 时区设为 `Asia/Shanghai` (CST +0800)

用户需提供以下信息（部署时逐一询问）：
1. OpenRouter API key (`sk-or-v1-...`)
2. GitHub 用户名 (如 `CSCode2`)
3. GitHub 仓库名 (如 `china-policy-analyze-skill`)
4. GitHub Personal Access Token (`ghp_...`)，scopes: `repo`, `workflow`
5. Git 提交者姓名和邮箱 (如 `CS2`, `2984301751@qq.com`)
6. 服务器上 repo 的绝对路径 (如 `/opt/china-policy-analyze-skill`)

## 1. 克隆仓库

```bash
# 假设 repo 路径为 /opt/china-policy-analyze-skill
# 下文用 $REPO_ROOT 表示此路径
git clone https://github.com/<GITHUB_USER>/china-policy-analyze-skill.git $REPO_ROOT
cd $REPO_ROOT
```

## 2. Python 环境

```bash
cd $REPO_ROOT
python3 -m venv venv
source venv/bin/activate
pip install -e .
pip install -e ".[dev]"
```

## 3. GitHub CLI 认证

```bash
# 复制 token 到剪贴板，然后：
gh auth login --with-token
# 粘贴 token
# 或直接设置环境变量：
echo "<GITHUB_TOKEN>" | gh auth login --with-token
```

Git 身份配置（用于 cron 任务提交代码）：

```bash
git config user.name "<GIT_USER_NAME>"
git config user.email "<GIT_USER_EMAIL>"
```

## 4. 安装 Hermes

按照 Hermes 官方安装指南安装 `hermes` CLI。安装后验证：

```bash
hermes --version
```

## 5. 配置 Hermes

### 5.1 环境变量

```bash
mkdir -p ~/.hermes
cp $REPO_ROOT/docs/hermes/.env.template ~/.hermes/.env
```

编辑 `~/.hermes/.env`，填入用户提供的 OpenRouter API key。

### 5.2 Agent 规则 (SOUL.md)

```bash
cp $REPO_ROOT/docs/hermes/SOUL.md ~/.hermes/SOUL.md
```

**重要：** SOUL.md 中的路径占位符 `REPO_ROOT_PLACEHOLDER` 需要替换为实际的仓库路径。执行：

```bash
sed -i "s|REPO_ROOT_PLACEHOLDER|$REPO_ROOT|g" ~/.hermes/SOUL.md
```

### 5.3 模型配置 (config.yaml)

```bash
cp $REPO_ROOT/docs/hermes/config.yaml ~/.hermes/config.yaml
```

**重要：** 同样替换路径占位符：

```bash
sed -i "s|REPO_ROOT_PLACEHOLDER|$REPO_ROOT|g" ~/.hermes/config.yaml
```

**检查模型名是否仍有效。** `nvidia/nemotron-3-nano-30b-a3b:free` 是 2026 年 5 月推荐的免费模型。如果已下线，从 OpenRouter 选一个新的免费模型替换 `config.yaml` 中所有 `model` 字段。

### 5.4 Cron 任务

```bash
cp $REPO_ROOT/docs/hermes/cron-jobs.json ~/.hermes/cron/jobs.json
```

**替换路径占位符：**

```bash
sed -i "s|REPO_ROOT_PLACEHOLDER|$REPO_ROOT|g" ~/.hermes/cron/jobs.json
```

验证 cron 任务已加载：

```bash
hermes cron list
```

应看到 6 个任务：policy_watcher_daily, foreign_policy_watcher_daily, geo_conflict_watcher_daily, policy_distiller_weekly, skill_maintainer_monthly, local_policy_watcher_daily。

## 6. 设置时区

**必须设为 Asia/Shanghai，否则 cron 任务在错误时间执行。**

```bash
sudo timedatectl set-timezone Asia/Shanghai
timedatectl status  # 验证: Time zone: Asia/Shanghai (CST, +0800)
```

## 7. 启动 Hermes Gateway

Hermes 需要 Gateway 持续运行才能执行 cron 任务。创建 systemd 服务：

```bash
sudo tee /etc/systemd/system/hermes-gateway.service << EOF
[Unit]
Description=Hermes Gateway Service
After=network.target

[Service]
Type=simple
EnvironmentFile=/root/.hermes/.env
WorkingDirectory=$REPO_ROOT
ExecStart=hermes gateway
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable hermes-gateway
sudo systemctl start hermes-gateway
sudo systemctl status hermes-gateway  # 验证: active (running)
```

## 8. 首次数据采集

部署完成后，手动触发一次数据采集以初始化语料库：

```bash
cd $REPO_ROOT
source venv/bin/activate
echo '{}' > corpus/metadata/hash_store.json
CPI_MAX_DOCS=15 timeout 120 python scripts/_run_daily_update.py
```

## 9. 验证部署

### 9.1 检查网关状态

```bash
systemctl is-active hermes-gateway  # 应输出: active
```

### 9.2 检查 cron 任务

```bash
hermes cron list
```

所有任务应为 `[active]`，Next run 应显示未来的时间。

### 9.3 手动触发每日策略观察测试

```bash
echo '{}' > $REPO_ROOT/corpus/metadata/hash_store.json
hermes cron run <policy_watcher_daily_job_id>
# 等待 4-6 分钟，检查 PR
gh pr list --repo <GITHUB_USER>/china-policy-analyze-skill --limit 1
```

### 9.4 测试外部宏观源脚本

```bash
cd $REPO_ROOT && source venv/bin/activate
timeout 120 python scripts/_run_foreign_macro.py
```

### 9.5 测试地方策略脚本

```bash
cd $REPO_ROOT && source venv/bin/activate
timeout 120 python scripts/_run_local_policy.py
```

## 10. Cron 任务表

| 任务 | 时间(CST) | 脚本 | 说明 |
|------|----------|------|------|
| policy_watcher_daily | 06:00 | `daily_cron.sh` → `_run_daily_update.py` | 36 个部委源每日政策采集 |
| foreign_policy_watcher_daily | 07:00 | `foreign_macro_cron.sh` → `_run_foreign_macro.py` | 外部宏观源 (美财政部/美联储/联邦公报/日银行) |
| geo_conflict_watcher_daily | 07:30 | (Agent WebFetch) | 地缘风险信号监测 |
| local_policy_watcher_daily | 18:00 | `local_policy_cron.sh` → `_run_local_policy.py` | 41 个城市政府源 4 天轮换 |
| policy_distiller_weekly | 每周一 07:30 | (Agent) | 生成 7 种结构化卡片、周报 |
| skill_maintainer_monthly | 每月 1 日 08:00 | (Agent) | 校准评分、测试站点可用性 |

## 11. 故障排查

### Gateway 未启动
```bash
journalctl -u hermes-gateway -n 50 --no-pager
```

### Cron 任务未触发
```bash
# 检查 session
ls -lt ~/.hermes/sessions/ | head -5
# 查看最新 session 内容
python3 -c "import json; msgs=json.load(open('<latest_session>'))['messages']; print(len(msgs), 'messages')"
```

### PR 未提交
```bash
# 手动运行采集脚本检查
cd $REPO_ROOT && source venv/bin/activate
timeout 120 python scripts/_run_daily_update.py
# 检查报告
cat $REPO_ROOT/reports/daily_$(date +%Y-%m-%d).md
```

### 时区不匹配
```bash
date  # 应显示 CST 时区
# 如果不对:
sudo timedatectl set-timezone Asia/Shanghai
# 重启 gateway (时区在启动时读取):
sudo systemctl restart hermes-gateway
# 重新设置 cron 任务以触及时区缓存更新:
hermes cron list  # 记录所有 job IDs
for id in <job_id1> <job_id2> ...; do
  hermes cron edit $id --schedule "$(hermes cron list 2>/dev/null | grep $id | awk '{print $3}')"
done
```

## 附：在 `/root/.hermes/` 目录下部署的文件清单

| 文件 | 来源 | 说明 |
|------|------|------|
| `.env` | `docs/hermes/.env.template` | 填入 API key |
| `SOUL.md` | `docs/hermes/SOUL.md` | Agent 规则（替换 REPO_ROOT_PLACEHOLDER） |
| `config.yaml` | `docs/hermes/config.yaml` | 模型配置（替换 REPO_ROOT_PLACEHOLDER） |
| `cron/jobs.json` | `docs/hermes/cron-jobs.json` | Cron 任务定义（替换 REPO_ROOT_PLACEHOLDER） |
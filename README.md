# 中国政策分析技能 / China Policy Analyze Skill

> 公共政策基础设施 · 让政策信息对每个人都触手可及
>
> Public Policy Infrastructure · Making policy information accessible to everyone

---

## 📋 项目简介 / Project Description

**中文：**

中国政策分析技能（China Policy Analyze Skill）是一套面向中国公共政策领域的开源分析系统。它以"监测—解读—研判—预警"为核心链路，从权威来源自动化采集政策文本，通过结构性解读提取政策意图、影响范围与关键信号，为用户提供基于证据的政策分析，而非主观判断。

本项目定位为**公共基础设施**，而非个人项目。所有输出均标注来源与证据等级，确保可追溯、可验证、可审计。

**English:**

China Policy Analyze Skill is an open-source analysis system for China's public policy domain. Built on the "monitor–interpret–assess–alert" pipeline, it automates policy text collection from authoritative sources, extracts policy intent, scope, and key signals through structural interpretation, and delivers evidence-based policy analysis rather than subjective judgment.

This project is positioned as **public infrastructure**, not a personal project. All outputs are annotated with sources and evidence levels to ensure traceability, verifiability, and auditability.

---

## 🧭 核心理念 / Core Philosophy

| 原则 | 说明 |
|------|------|
| **证据优先** | 任何结论必须有可追溯的来源，标注证据等级（L1–L5） |
| **不做预测** | 提供情景分析，而非确定性预测；不做投资建议 |
| **审慎解读** | 对涉密、军事、外交内容严格限制输出范围 |
| **可审计性** | 所有分析链路可复现，数据来源可追溯 |
| **公共属性** | 工具服务于公共利益，不服务于特定利益集团 |

---

## 👥 目标用户 / Target Users

- 🔍 **政策研究者** — 追踪政策动态、解读政策信号
- 🏢 **企业合规团队** — 评估政策变动对业务的影响
- 📰 **财经媒体** — 获取基于证据的政策分析素材
- 🎓 **高校师生** — 学习政策分析框架与方法论
- 🏛️ **公共部门** — 跨部门政策信息共享与对标

---

## ✨ 功能特性 / Features

### 政策监测 (Policy Monitoring)
- 多源自动采集（国务院、各部委、地方政府）
- 增量更新检测与变更追踪
- 关键词订阅与智能推送

### 政策解读 (Policy Interpretation)
- 自动结构化摘要（政策意图 / 影响范围 / 关键信号）
- 证据等级标注（L1 文本原文 → L5 专家研判）
- 关联政策图谱与时间线

### 政策研判 (Policy Assessment)
- 多情景分析（乐观 / 基线 / 悲观）
- 机会与风险识别
- 合规边界提示

### 政策预警 (Policy Alert)
- 关键政策信号检测
- 即将到期政策提醒
- 政策趋势变化告警

### RAG 增强检索 (RAG-Enhanced Retrieval)
- 向量索引 + BM25 混合检索
- 上下文感知的政策问答
- 来源引用与证据链

---

## 🏗️ 系统架构 / Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     用户接口层 / User Interface               │
│   CLI · API Server · Web Dashboard (未来)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    技能编排层 / Skill Orchestration             │
│   Monitor → Interpret → Assess → Alert                      │
└──┬──────────┬──────────┬──────────┬────────────────────────┘
   │          │          │          │
┌──▼───┐ ┌───▼──┐ ┌────▼───┐ ┌───▼────┐
│采集器│ │解析器│ │研判引擎│ │预警引擎│
│Crawl │ │Parse │ │Assess  │ │Alert   │
└──┬───┘ └───┬──┘ └────┬───┘ └───┬────┘
   │         │         │         │
┌──▼─────────▼─────────▼─────────▼──────┐
│           数据层 / Data Layer           │
│  Corpus · Vector Index · BM25 Index    │
│  Evidence Store · Source Registry      │
└───────────────────────────────────────┘
           │                │
┌──────────▼──┐    ┌───────▼──────────┐
│  外部数据源  │    │  LLM / Embedding  │
│  (Gov Sites) │    │  (Optional)       │
└─────────────┘    └──────────────────┘
```

---

## 🚀 快速开始 / Quick Start

### 环境要求

- Python 3.10+
- pip 或 uv 包管理器

### 安装

```bash
# 克隆仓库
git clone https://github.com/CSCode2/china-policy-analyze-skill.git
cd china-policy-analyze-skill

# 安装核心依赖
pip install -e .

# 安装 RAG 可选依赖
pip install -e ".[rag]"

# 安装开发依赖
pip install -e ".[dev]"
```

### 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 填入必要配置
# CPI_DATA_DIR=/path/to/data
# CPI_LLM_PROVIDER=openai  # 或其他支持的提供商
# CPI_LLM_API_KEY=sk-xxxx  # 从环境变量读取，不要硬编码
```

### 运行

```bash
# 初始化数据目录
cpi init

# 采集最新政策
cpi monitor --source state_council --days 7

# 解读指定政策
cpi interpret --file policy_2026_001.pdf

# 政策问答
cpi ask "2026年新能源汽车补贴政策有什么变化？"

# 运行评估测试
cpi eval --all
```

---

## 📁 项目结构 / Project Structure

```
china-policy-analyze-skill/
├── corpus/                  # 政策文本语料库
│   ├── raw/                 # 原始采集文件（不入版本控制）
│   └── seed/                # 初始种子数据
├── eval/                    # 评估测试
│   ├── test_questions.yaml
│   ├── citation_tests.yaml
│   ├── recency_tests.yaml
│   ├── policy_language_tests.yaml
│   ├── opportunity_analysis_tests.yaml
│   └── forecast_calibration_tests.yaml
├── rag/                     # RAG 索引与检索
│   ├── vector_index/        # 向量索引（不入版本控制）
│   └── bm25_index/          # BM25 索引（不入版本控制）
├── src/
│   └── cpi/                 # 核心源码
├── pyproject.toml
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
└── DISCLAIMER.md
```

---

## ⚠️ 安全须知 / Safety Notice

**本项目不提供以下内容：**

1. 任何形式的确定性政策预测 — 所有研判均为情景分析
2. 投资建议或收益保证 — 机会分析必须包含风险提示
3. 涉密/军事/外交领域的深度分析 — 严格限制输出范围
4. 个人画像或群体标签 — 不收集、不存储、不分析个人信息
5. 未经来源标注的结论 — 所有输出必须标注证据等级

**如果你发现安全问题，请参阅 [SECURITY.md](SECURITY.md) 进行负责任披露。**

---

## 📄 许可证 / License

本项目基于 [MIT License](LICENSE) 开源。

---

## 🤝 参与贡献 / Contributing

欢迎参与！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

---

## 📜 法律与合规 / Legal & Compliance

- [免责声明 / Disclaimer](DISCLAIMER.md)
- [法律合规声明 / Legal Compliance](LEGAL_COMPLIANCE.md)
- [数据来源政策 / Data Source Policy](DATA_SOURCE_POLICY.md)
- [个人信息保护政策 / Personal Info Policy](PERSONAL_INFO_POLICY.md)
- [敏感内容政策 / Sensitive Content Policy](SENSITIVE_CONTENT_POLICY.md)
- [来源准入规则 / Source Admission Rules](SOURCE_ADMISSION_RULES.md)
- [评审指南 / Review Guidelines](REVIEW_GUIDELINES.md)

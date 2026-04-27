# 中国政策分析技能

> 读懂政策，本身就是一笔丰厚的宝藏。

---

## 为什么做这个项目？

众所周知，**中国政策具有高度的言行一致性、持续性、严谨性和说到做到的特点。**

一个五年规划写在纸上的目标，到期末你回头一看——修了的路、建的项目、落的制度，跟当初写的差不太多。一项产业政策说"要大力发展"，后面的补贴、用地、税收、信贷往往就跟着来了。这不是巧合，这是中国治理体系的设计逻辑：**先定方向，再配资源，最后用考核确保落地。**

这意味着什么？**研究中国公开的政策内容，是对未来中国各种规划和发展情况最有效的预测方法。** 不是唯一方法，但是性价比最高的方法。因为政策文本本身就是"未来路线图"——它告诉你钱要往哪里花、人要往哪里走、规则要怎么变。

**读懂政策，本身就是一笔丰厚的宝藏——信息差带来的复利。** 谁先读懂、谁先行动，谁就占先机。这几年光伏、新能源车、芯片、低空经济，哪个不是先写在政策里，再在市场上爆发的？

但现实是：**大多数人根本没意识到这一点。** 而意识到的人里，大部分又没有足够的执行力去每天搜集几十个政府网站的信息，没有足够的阅读能力去理解那些充满专业术语和政策语言的公文，更没有足够的时间去把散落在各处的政策碎片拼成完整的图景。

**本项目就是要解决这个问题。**

它把这些流程——**采集、解读、研判、预警**——自动化了。每天帮你看几十个权威来源，把新出的政策文本抓下来，用结构化的方式解读出"这句话到底什么意思"、"跟之前的政策是什么关系"、"对哪些行业/人群有影响"、"背后的信号是什么"，然后输出你能直接看懂的分析报告。

你不是在读政府公文，你是在读一份帮你把公文"翻译"成人话的每日简报。

---

## 它能做什么？

### 每日自动采集

从国务院、各部委、地方政府等 100+ 官方来源自动采集最新政策文本，增量更新，不遗漏。

### 结构化解读

每条政策不再是密密麻麻的公文，而是拆解成：
- **政策意图** — 为什么要出这个政策？
- **影响范围** — 影响谁？哪些行业？哪些人群？
- **关键信号** — 跟之前比有什么变化？释放了什么信号？
- **证据等级** — 这个判断来自原文引用、合理推断还是专家观点？标注清楚，绝不混为一谈。

### 多情景研判

不做确定性预测（没人在水晶球里见过未来），而是给你**乐观/基线/悲观**三种情景，让你自己判断。

### 机会与风险识别

政策背后是资源流向。哪些行业被扶持？哪些领域被收紧？哪些政策即将到期？这些信息对研究、就业、创业、投资都有参考价值。

### 智能问答

直接问"新能源汽车补贴最近有什么变化？"，系统会在已采集的政策语料中检索、定位、组织答案，并标注来源。

---

## 它不能做什么？

老实说在前头：

- **不给投资建议。** 政策扶持不等于股票必涨，机会分析一定带着风险提示。
- **不做确定性预测。** "某年某月一定会发生某事"这种话我们不说，也反对别人说。
- **不碰涉密和军事内容。** 这是红线。
- **不替你做决策。** 工具提供信息，决策永远是你自己的事。

---

## 实在想看英文？

China Policy Analyze Skill is an open-source system that automates policy text collection, structural interpretation, scenario assessment, and early warning from 100+ authoritative Chinese government sources. It turns dense policy documents into actionable daily briefings with evidence-level annotations, multi-scenario analysis, and RAG-enhanced Q&A.

---

## 快速开始

### 环境要求

- Python 3.10+
- pip 或 uv

### 安装

```bash
git clone https://github.com/CSCode2/china-policy-analyze-skill.git
cd china-policy-analyze-skill

# 核心依赖
pip install -e .

# RAG 检索功能（可选）
pip install -e ".[rag]"

# 开发依赖（可选）
pip install -e ".[dev]"
```

### 配置

```bash
cp .env.example .env
# 编辑 .env 填入配置
```

### 运行

```bash
cpi init                              # 初始化数据目录
cpi monitor --source state_council    # 采集最新政策
cpi interpret --file policy.pdf       # 解读指定政策
cpi ask "新能源汽车补贴有什么变化？"   # 政策问答
cpi eval --all                        # 运行评估测试
```

---

## 项目结构

```
china-policy-analyze-skill/
├── corpus/                  # 政策文本语料库
│   ├── raw/                 # 原始采集文件
│   └── seed/                # 初始种子数据
├── eval/                    # 评估测试
├── rag/                     # RAG 索引与检索
├── src/china_policy_skill/  # 核心源码
│   ├── fetch/               # 采集器
│   ├── parse/               # 解析器
│   ├── classify/            # 分类器
│   ├── distill/             # 蒸馏（结构化解读）
│   ├── index/               # 索引构建
│   ├── evaluate/            # 评估引擎
│   ├── report/              # 报告生成
│   └── utils/               # 工具函数
├── skill/                   # 技能定义（推理框架、政策语言词典等）
├── config/                  # 配置文件（数据源、重要性规则等）
├── scripts/                 # 运维脚本
└── .github/workflows/       # CI/CD
```

---

## 核心理念

| 原则 | 说明 |
|------|------|
| 证据优先 | 任何结论标注来源和证据等级（L1 原文 → L5 专家研判），不瞎蒙 |
| 审慎解读 | 区分事实、解读、推断、不确定——绝不把猜测当事实输出 |
| 公共属性 | 开源免费，不服务于任何特定利益集团 |
| 可审计 | 所有分析链路可复现，数据来源可追溯 |

---

## 安全须知

如果你发现安全问题，请参阅 [SECURITY.md](SECURITY.md) 进行负责任披露。

---

## 许可证

[MIT License](LICENSE) — 随便用，出了事别找我。

---

## 参与贡献

欢迎！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 法律与合规

- [免责声明](DISCLAIMER.md)
- [法律合规声明](LEGAL_COMPLIANCE.md)
- [数据来源政策](DATA_SOURCE_POLICY.md)
- [个人信息保护](PERSONAL_INFO_POLICY.md)
- [敏感内容政策](SENSITIVE_CONTENT_POLICY.md)
- [来源准入规则](SOURCE_ADMISSION_RULES.md)
- [评审指南](REVIEW_GUIDELINES.md)

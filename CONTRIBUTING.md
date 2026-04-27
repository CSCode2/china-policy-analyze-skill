# 贡献指南 / Contributing

**最后更新：2026年4月**

---

感谢你对本项目的关注！本项目欢迎任何形式的贡献，但在参与之前请仔细阅读以下规则。

## 贡献规则

### 规则 1：证据优先，来源必注

所有涉及政策分析内容的贡献必须标注来源和证据等级。不接受无来源的分析结论。

- 每个分析结论须标注来源 URL、发布机构、发布日期
- 证据等级须按 L1–L5 标准标注
- 引用政策原文须标注具体条款位置（章、节、条、款）

### 规则 2：不做确定性预测

所有政策研判贡献必须以情景分析形式呈现，严禁确定性预测。

- 正确："政策可能向 X 方向调整（基线情景）"
- 错误："政策将向 X 方向调整"
- 涉及机会分析时，必须同时包含风险提示
- 严禁提供任何形式的投资建议或收益保证

### 规则 3：敏感内容遵守红线

贡献内容不得违反 [敏感内容政策](SENSITIVE_CONTENT_POLICY.md)。

- 军事/国防/涉密/维稳内容：禁止提交
- 外交/民族宗教内容：限制提交，须声明并加注标签
- 如不确定内容是否敏感，先提 Issue 讨论
- 任何违反敏感内容政策的 PR 将被直接关闭

### 规则 4：个人信息零容忍

贡献内容不得包含任何未脱敏的个人信息。

- 不得提交包含个人身份信息的代码或数据
- 分析逻辑不得构建个人画像
- 日志输出不得包含个人信息
- 违反此规则的 PR 将被立即关闭并移除

### 规则 5：代码质量与测试

所有代码贡献须通过质量检查。

- Ruff lint 检查通过（`ruff check .`）
- Mypy 类型检查通过（`mypy src/`）
- 相关测试用例通过（`pytest`）
- 评估测试未退化（`cpi eval --all`）
- 新增功能须包含对应测试

### 规则 6：法律合规先行

所有贡献须符合 [法律合规声明](LEGAL_COMPLIANCE.md)。

- 新增数据来源须通过 [来源准入规则](SOURCE_ADMISSION_RULES.md) 审查
- 不得引入违反法律法规的功能或数据
- 如不确定合规性，先提 Issue 讨论
- 涉及跨境数据传输的功能须评估合规风险

---

## 开发环境搭建

### 1. 克隆仓库

```bash
git clone https://github.com/your-org/china-policy-analyze-skill.git
cd china-policy-analyze-skill
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

### 3. 安装依赖

```bash
# 安装核心依赖（可编辑模式）
pip install -e .

# 安装 RAG 可选依赖
pip install -e ".[rag]"

# 安装开发依赖
pip install -e ".[dev]"
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入必要配置
```

### 5. 初始化数据目录

```bash
cpi init
```

### 6. 验证安装

```bash
# 运行测试
pytest

# 运行 lint
ruff check .

# 运行类型检查
mypy src/

# 运行评估
cpi eval --all
```

---

## 开发工作流

### 分支命名

- `feature/xxx` — 新功能
- `fix/xxx` — Bug 修复
- `docs/xxx` — 文档更新
- `refactor/xxx` — 代码重构
- `eval/xxx` — 评估相关

### Commit 格式

```
type(scope): 简短描述

详细说明（可选）
```

类型：
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具
- `policy`: 政策/合规相关

### PR 流程

1. Fork 仓库并创建功能分支
2. 进行开发并确保通过所有检查
3. 提交 PR，按 [评审指南](REVIEW_GUIDELINES.md) 自查
4. 等待至少 1 位 Reviewer 评审
5. 修改后通过评审即可合并

### 报告问题

- Bug 报告：使用 GitHub Issues，标注 `bug` 标签
- 功能建议：使用 GitHub Issues，标注 `enhancement` 标签
- 安全问题：参阅 [SECURITY.md](SECURITY.md)，不要公开提交
- 合规问题：使用 GitHub Issues，标注 `compliance` 标签

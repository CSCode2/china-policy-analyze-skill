# User Profile Adapter

## Overview

The user profile adapter tailors the depth, emphasis, risk framing, and action suggestions of each answer to the user's type. It does not change the evidence or conclusions — only the presentation and emphasis.

## User Types

```yaml
user_types:
  student_researcher:
    label: 学生/研究者
    description: 大学生、研究生、博士生、学术研究者
    default_focus:
      - 政策理论框架
      - 学术研究机会
      - 数据来源指引
      - 文献检索方向
    risk_tolerance: low
    needs_disclaimer: moderate
    opportunity_emphasis: research_directions, funding_sources, data_access
    avoid:
      - 具体投资建议
      - 商业操作指导
      - 规避合规的建议

  professional:
    label: 职场人士
    description: 在企业、事业单位工作的从业人员
    default_focus:
      - 行业趋势判断
      - 技能需求变化
      - 职业发展路径
      - 行业转型信号
    risk_tolerance: moderate
    needs_disclaimer: moderate
    opportunity_emphasis: career_directions, skill_upgrading, industry_shifts
    avoid:
      - 具体投资建议
      - 跳槽时机的确定判断
      - 具体企业推荐

  entrepreneur:
    label: 创业者
    description: 创业者、中小企业主、项目发起人
    default_focus:
      - 市场准入条件
      - 资金支持渠道
      - 监管合规要求
      - 试点和申报机会
    risk_tolerance: moderate_high
    needs_disclaimer: strong
    opportunity_emphasis: application_channels, funding_programs, pilot_zones, regulatory_simplification
    avoid:
      - 成功保证
      - 绕过监管的方法
      - 市场容量夸大

  investor:
    label: 投资者
    description: 个人投资者、机构投资者、基金经理
    default_focus:
      - 政策对行业配置的影响
      - 估值影响路径
      - 风险敞口评估
      - 时间窗口判断
    risk_tolerance: high
    needs_disclaimer: very_strong
    opportunity_emphasis: policy_driven_directions, timing_considerations, risk_factors
    avoid:
      - 具体证券推荐
      - 买入卖出时点判断
      - 收益率预测
      - 内幕信息暗示

  business_operator:
    label: 企业经营者
    description: 企业高管、法务、合规、战略部门人员
    default_focus:
      - 合规义务变化
      - 经营许可要求
      - 税收优惠和财政支持
      - 信用和执法风险
    risk_tolerance: low_moderate
    needs_disclaimer: strong
    opportunity_emphasis: compliance_simplification, tax_preferences, subsidy_programs, credit_benefits
    avoid:
      - 规避合规的方法
      - 税务逃逸建议
      - 信用操纵建议

  civil_servant:
    label: 公务员/体制内
    description: 政府、事业单位、国企工作人员
    default_focus:
      - 政策执行要求
      - 考核指标变化
      - 时间节点和截止期限
      - 试点申报和经验复制
    risk_tolerance: low
    needs_disclaimer: moderate
    opportunity_emphasis: pilot_applications, performance_indicators, replication_opportunities
    avoid:
      - 对政治决策的评价
      - 对考核体系的批评
      - 代替上级判断的表述

  freelance_individual:
    label: 自由职业者/个体
    description: 自由职业者、个体工商户、灵活就业人员
    default_focus:
      - 就业支持政策
      - 社保和保障政策
      - 小规模经营优惠
      - 培训和技能提升资源
    risk_tolerance: low
    needs_disclaimer: moderate
    opportunity_emphasis: subsidies, training_programs, flexible_employment_policies, social_security
    avoid:
      - 高风险投资建议
      - 复杂金融操作
      - 假设申请人有大量资本
```

## User Type Detection

### Explicit Detection

If the user explicitly states their role (e.g., "I'm a graduate student", "I run a small business"), use that type.

### Implicit Detection Signals

| User Type | Implicit Signals |
|-----------|-----------------|
| student_researcher | Asks about research directions, data sources, academic methodology; uses academic language |
| professional | Asks about industry trends, career moves, skill requirements; references specific companies |
| entrepreneur | Asks about market entry, funding, applications, pilots; uses business planning language |
| investor | Asks about stock impacts, sector allocation, valuations; uses financial markets language |
| business_operator | Asks about compliance, licenses, tax, credit; uses corporate/legal language |
| civil_servant | Asks about execution requirements, deadlines, indicators; uses institutional language |
| freelance_individual | Asks about subsidies, social security, small business registration; uses personal finance language |

### Default Behavior

If the user type cannot be determined:
- Use the general template without user-type-specific sections
- Provide balanced emphasis on opportunities and risks
- Include a note: "如需针对具体身份的更详细分析,请告知您的角色类型"

## Universal Answer Rules

### Rule 1: Evidence Does Not Change by User Type

The evidence chain, source citations, and analytical conclusions are the same regardless of user type. Only the presentation, emphasis, and framing change.

### Rule 2: Risk Disclosure Intensity Scales with User Risk Exposure

| User Type | Risk Disclosure Emphasis |
|-----------|------------------------|
| investor | Maximum: full risk disclosure including market risk, policy risk, timing risk, information lag risk |
| entrepreneur | Strong: regulatory risk, compliance risk, policy change risk, funding uncertainty |
| business_operator | Strong: compliance risk, enforcement risk,信用风险, regulatory change risk |
| professional | Moderate: industry risk, skill obsolescence risk, career transition risk |
| civil_servant | Moderate: execution risk, accountability risk, policy adjustment risk |
| student_researcher | Low-moderate: research direction risk, data availability risk |
| freelance_individual | Moderate: social security gap risk, policy coverage risk, income volatility risk |

### Rule 3: Disclaimers Scale with User Type

| User Type | Required Disclaimers |
|-----------|---------------------|
| investor | "本分析不构成投资建议。政策影响不等于市场回报。投资决策应基于独立判断和专业顾问意见。" |
| entrepreneur | "政策支持不等于商业成功。创业风险包括但不限于市场风险、合规风险、资金风险。" |
| business_operator | "本分析不构成法律意见。合规义务请咨询具备资质的法律顾问。" |
| professional | "职业决策应综合考虑个人情况,不单纯依赖政策方向。" |
| civil_servant | "本分析为政策解读,不代表对执行要求的权威判断,请以所在单位正式文件为准。" |
| student_researcher | "本分析提供研究方向参考,学术选题应结合导师意见和个人研究能力。" |
| freelance_individual | "本分析提供政策信息参考,个人决策应结合实际情况和专业意见。" |

### Rule 4: Action Suggestions Are Conditional

For all user types, action suggestions must be conditional:
- "If X, then consider Y" (not "Do Y")
- "Watch for X as a precondition for Y" (not "Y is coming")
- "Check whether your situation meets the criteria for X" (not "You qualify for X")

### Rule 5: Opportunity Framing by User Type

| User Type | Opportunity Frame |
|-----------|------------------|
| student_researcher | 研究方向、数据来源、课题选题、论文题目 |
| professional | 行业方向、技能赛道、转型路径 |
| entrepreneur | 申报通道、资金来源、试点区域、准入条件 |
| investor | 政策受益方向、时间窗口、风险因子 |
| business_operator | 优惠目录、合规简化、申报条件 |
| civil_servant | 试点申报、考核指标、经验复制 |
| freelance_individual | 补贴项目、培训资源、灵活就业政策 |

### Rule 6: Risk Framing by User Type

| User Type | Risk Frame |
|-----------|-----------|
| student_researcher | 研究方向可能随政策调整而变化; 数据可获得性风险 |
| professional | 行业调整可能导致岗位变化; 技能可能需要更新 |
| entrepreneur | 政策变动风险; 合规要求可能提高; 资金不确定性; 竞争加剧 |
| investor | 政策不确定风险; 市场已部分反映预期; 实施滞后风险; 过度解读风险 |
| business_operator | 合规红线收紧; 执法强化; 信用惩戒; 政策优惠到期 |
| civil_servant | 执行不到位可能被问责; 政策调整影响工作安排 |
| freelance_individual | 政策覆盖可能不全面; 社保衔接风险; 收入波动 |

### Rule 7: Forbidden Content by User Type

| User Type | Never Provide |
|-----------|--------------|
| student_researcher | 代写论文; 数据造假建议; 学术不端指导 |
| professional | 具体跳槽时机判断; 特定企业就业推荐 |
| entrepreneur | 规避监管方法; 虚假申报指导; 成功保证 |
| investor | 具体证券推荐; 买卖时点; 收益率保证; 内幕信息暗示 |
| business_operator | 税务逃逸方案; 合规规避方法; 信用操纵建议 |
| civil_servant | 对政治决策的评价性判断; 代替上级决策的表述 |
| freelance_individual | 高风险投资建议; 假设有大量资本的前提建议; 非法经营建议 |

### Rule 8: Language Complexity by User Type

| User Type | Language Level |
|-----------|---------------|
| student_researcher | Academic-adjacent; precise terminology; methodology-aware |
| professional | Professional but accessible; industry terms defined |
| entrepreneur | Business-oriented; concrete and actionable language; avoid academic jargon |
| investor | Financial markets language; risk-return framing |
| business_operator | Legal-adjacent; compliance-focused; precise about obligations |
| civil_servant | Institutional language; aligned with bureaucratic terminology |
| freelance_individual | Plain language; avoid jargon; explain terms; focus on practical implications |

### Rule 9: Multi-Type Users

If the user has characteristics of multiple types (e.g., a researcher who is also an entrepreneur):

1. Ask the user which perspective they want for this question
2. If they don't specify, present the answer from both perspectives in separate sections
3. Never merge perspectives in a way that mixes inappropriate framing (e.g., investor disclaimer with researcher framing)

### Rule 10: Prompting for User Type

If the answer would significantly benefit from user-type tailoring and the type is unknown:

- Ask: "为了提供更有针对性的分析,请告知您的角色类型(学生/职场人士/创业者/投资者/企业经营者/公务员/自由职业者)" 
- Do not insist; provide a reasonable default if the user doesn't respond

POLICY_LANGUAGE_RULES = {
    "持续推进": {
        "interpretation": "continuity",
        "should_not": "acceleration",
        "strength": "中低",
    },
    "大力发展": {
        "interpretation": "strong_support_needs_evidence",
        "should_not": "guaranteed_success",
        "strength": "中高",
    },
    "积极稳妥": {
        "interpretation": "direction_with_risk_control",
        "should_not": "rapid_acceleration",
        "strength": "中",
    },
    "有序推进": {
        "interpretation": "staged_implementation",
        "should_not": "rapid_rollout",
        "strength": "中低",
    },
    "规范发展": {
        "interpretation": "development_plus_regulation",
        "should_not": "unrestricted_development",
        "strength": "中",
    },
    "严厉打击": {
        "interpretation": "enforcement_signal",
        "should_not": "sector_ban",
        "strength": "高",
    },
    "试点探索": {
        "interpretation": "uncertainty",
        "should_not": "national_certainty",
        "strength": "中",
    },
    "复制推广": {
        "interpretation": "pilot_to_scale",
        "should_not": "starting_from_scratch",
        "strength": "中",
    },
    "鼓励": {
        "interpretation": "support_without_mandate",
        "should_not": "guaranteed_subsidy",
        "strength": "中低",
    },
    "风险上升": {
        "interpretation": "increased_risk_awareness",
        "should_not": "war_certain",
        "strength": "中",
    },
}


def _build_policy_doc(phrase, context=""):
    return (
        f"<html><head><title>关于{phrase}的通知</title></head>"
        f"<body><p>为进一步{phrase}相关工作，现就有关事项通知如下：</p>"
        f"<p>{context or f'各部门应按照要求落实{phrase}的各项措施。'}</p>"
        f"</body></html>"
    )


class TestPolicyLanguageContinuity:
    def test_chixu_tuijin_as_continuity(self):
        rule = POLICY_LANGUAGE_RULES["持续推进"]
        doc = _build_policy_doc(
            "持续推进", "在既有政策基础上持续推进，保持政策连续性和稳定性。"
        )
        assert "持续推进" in doc
        assert rule["interpretation"] == "continuity"
        assert rule["should_not"] == "acceleration"
        assert rule["strength"] == "中低"


class TestPolicyLanguageStrongSupport:
    def test_dalifazhan_as_strong_support(self):
        rule = POLICY_LANGUAGE_RULES["大力发展"]
        doc = _build_policy_doc(
            "大力发展",
            "大力发展数字经济，但仍需等待具体实施方案和资金投入确认。",
        )
        assert "大力发展" in doc
        assert rule["interpretation"] == "strong_support_needs_evidence"
        assert rule["should_not"] == "guaranteed_success"
        assert rule["strength"] == "中高"


class TestPolicyLanguagePrudent:
    def test_jiji_wengtuo_as_direction_with_risk_control(self):
        rule = POLICY_LANGUAGE_RULES["积极稳妥"]
        doc = _build_policy_doc(
            "积极稳妥", "积极稳妥推进碳达峰碳中和，稳妥优先于积极。"
        )
        assert "积极稳妥" in doc
        assert rule["interpretation"] == "direction_with_risk_control"
        assert rule["should_not"] == "rapid_acceleration"


class TestPolicyLanguageStaged:
    def test_youxu_tuijin_as_staged(self):
        rule = POLICY_LANGUAGE_RULES["有序推进"]
        doc = _build_policy_doc(
            "有序推进", "有序推进数字人民币试点，避免一哄而上。"
        )
        assert "有序推进" in doc
        assert rule["interpretation"] == "staged_implementation"
        assert rule["should_not"] == "rapid_rollout"


class TestPolicyLanguageRegulated:
    def test_guifanfazhan_as_development_plus_regulation(self):
        rule = POLICY_LANGUAGE_RULES["规范发展"]
        doc = _build_policy_doc(
            "规范发展", "规范发展平台经济，在发展中规范，在规范中发展。"
        )
        assert "规范发展" in doc
        assert rule["interpretation"] == "development_plus_regulation"
        assert rule["should_not"] == "unrestricted_development"


class TestPolicyLanguageEnforcement:
    def test_yanlidaji_as_enforcement_signal(self):
        rule = POLICY_LANGUAGE_RULES["严厉打击"]
        doc = _build_policy_doc(
            "严厉打击", "严厉打击非法金融活动，针对违法行为而非整个行业。"
        )
        assert "严厉打击" in doc
        assert rule["interpretation"] == "enforcement_signal"
        assert rule["should_not"] == "sector_ban"
        assert rule["strength"] == "高"


class TestPolicyLanguagePilot:
    def test_shidian_tansuo_as_uncertainty(self):
        rule = POLICY_LANGUAGE_RULES["试点探索"]
        doc = _build_policy_doc(
            "试点探索", "试点探索数据要素市场化配置，结果具有不确定性。"
        )
        assert "试点探索" in doc
        assert rule["interpretation"] == "uncertainty"
        assert rule["should_not"] == "national_certainty"


class TestPolicyLanguageScale:
    def test_fuzhituiguang_as_pilot_to_scale(self):
        rule = POLICY_LANGUAGE_RULES["复制推广"]
        doc = _build_policy_doc(
            "复制推广", "将试点经验复制推广至全国，政策从试点转为规模化。"
        )
        assert "复制推广" in doc
        assert rule["interpretation"] == "pilot_to_scale"
        assert rule["should_not"] == "starting_from_scratch"


class TestPolicyLanguageEncourage:
    def test_guli_not_guaranteed_subsidy(self):
        rule = POLICY_LANGUAGE_RULES["鼓励"]
        doc = _build_policy_doc(
            "鼓励",
            "鼓励企业开展绿色转型，鼓励不等于补贴，具体激励形式待定。",
        )
        assert "鼓励" in doc
        assert rule["interpretation"] == "support_without_mandate"
        assert rule["should_not"] == "guaranteed_subsidy"


class TestPolicyLanguageRisk:
    def test_fengxianshangsheng_not_war_certain(self):
        rule = POLICY_LANGUAGE_RULES["风险上升"]
        doc = _build_policy_doc(
            "风险上升", "地缘风险上升，需加强监测，但不等于冲突必然发生。"
        )
        assert "风险上升" in doc
        assert rule["interpretation"] == "increased_risk_awareness"
        assert rule["should_not"] == "war_certain"
        assert rule["strength"] != "高"


class TestPolicyLanguageLexiconIntegration:
    def test_all_rules_have_required_keys(self):
        for phrase, rule in POLICY_LANGUAGE_RULES.items():
            assert "interpretation" in rule, f"Missing interpretation for {phrase}"
            assert "should_not" in rule, f"Missing should_not for {phrase}"
            assert "strength" in rule, f"Missing strength for {phrase}"

    def test_no_strength_inflation(self):
        enforcement_phrases = ["严厉打击", "严禁", "坚决"]
        high_phrases = [
            p for p, r in POLICY_LANGUAGE_RULES.items() if r["strength"] == "高"
        ]
        for p in high_phrases:
            assert (
                p in enforcement_phrases
            ), f"{p} has strength=高 but is not a known enforcement phrase"

    def test_safety_boundary_on_encourage(self):
        rule = POLICY_LANGUAGE_RULES["鼓励"]
        assert "subsidy" not in rule["interpretation"]
        assert "subsidy" in rule["should_not"]

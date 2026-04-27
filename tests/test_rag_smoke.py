import json
import os
import tempfile

import pytest

from china_policy_skill.index.build_bm25_index import BM25IndexBuilder

SAMPLE_CHUNKS = [
    {
        "chunk_id": "chunk_001",
        "doc_id": "doc_15fyp",
        "title": "中华人民共和国国民经济和社会发展第十五个五年规划纲要",
        "source_name": "国家发改委",
        "publish_date": "2025-03-15",
        "authority_level": "S",
        "doc_type": "规划",
        "section_title": "第五章 数字经济",
        "paragraph_index": 0,
        "topics": ["数字经济", "人工智能", "十五五规划"],
        "policy_phrases": ["大力发展", "持续推进"],
        "text": (
            "大力推进人工智能产业发展，持续推进数字经济与实体经济深度融合。"
            "在十五五期间，重点布局AI大模型、智能驾驶、智慧城市等方向。"
        ),
    },
    {
        "chunk_id": "chunk_002",
        "doc_id": "doc_15fyp",
        "title": "中华人民共和国国民经济和社会发展第十五个五年规划纲要",
        "source_name": "国家发改委",
        "publish_date": "2025-03-15",
        "authority_level": "S",
        "doc_type": "规划",
        "section_title": "第八章 绿色发展",
        "paragraph_index": 0,
        "topics": ["绿色发展", "碳达峰", "十五五规划"],
        "policy_phrases": ["积极稳妥", "有序推进"],
        "text": (
            "积极稳妥推进碳达峰碳中和，有序推进能源结构转型，"
            "确保能源安全的前提下实现绿色低碳发展目标。"
        ),
    },
    {
        "chunk_id": "chunk_003",
        "doc_id": "doc_beijing_ai",
        "title": "北京市关于加快人工智能产业发展的若干措施",
        "source_name": "北京市人民政府",
        "publish_date": "2025-06-01",
        "authority_level": "B",
        "doc_type": "意见",
        "section_title": "",
        "paragraph_index": 0,
        "topics": ["人工智能", "地方政策", "北京"],
        "policy_phrases": ["鼓励", "支持"],
        "text": (
            "北京市鼓励企业开展AI大模型研发，支持在亦庄等地建设AI算力中心，"
            "为符合条件的企业提供算力补贴。北京将在人工智能领域加大投入。"
        ),
    },
    {
        "chunk_id": "chunk_004",
        "doc_id": "doc_mofcom_trade",
        "title": "商务部关于稳外贸稳外资的政策措施",
        "source_name": "商务部",
        "publish_date": "2025-04-20",
        "authority_level": "A",
        "doc_type": "通知",
        "section_title": "",
        "paragraph_index": 0,
        "topics": ["外贸", "外资", "稳外贸"],
        "policy_phrases": ["加大力度", "促进"],
        "text": (
            "加大力度稳外贸稳外资，促进跨境电商发展，"
            "支持企业开拓多元化国际市场。有序扩大服务业对外开放。"
        ),
    },
    {
        "chunk_id": "chunk_005",
        "doc_id": "doc_fmprc_geo",
        "title": "外交部发言人表态",
        "source_name": "外交部",
        "publish_date": "2025-05-10",
        "authority_level": "FP-A",
        "doc_type": "表态",
        "section_title": "",
        "paragraph_index": 0,
        "topics": ["外交", "地缘政治", "台海"],
        "policy_phrases": ["坚决反对", "核心利益"],
        "text": (
            "外交部发言人表示，中方坚决反对任何形式的外部干涉，"
            "台湾问题涉及中国核心利益。当前地区风险上升，"
            "但中方始终致力于和平统一方针。"
        ),
    },
    {
        "chunk_id": "chunk_006",
        "doc_id": "doc_ndrc_regulate",
        "title": "关于规范发展平台经济的指导意见",
        "source_name": "国家发改委",
        "publish_date": "2025-02-15",
        "authority_level": "A",
        "doc_type": "意见",
        "section_title": "",
        "paragraph_index": 0,
        "topics": ["平台经济", "反垄断", "数字经济"],
        "policy_phrases": ["规范发展", "严厉打击"],
        "text": (
            "规范发展平台经济，在发展中规范、在规范中发展。"
            "严厉打击平台经济领域不正当竞争和垄断行为，"
            "但支持合法合规经营。"
        ),
    },
    {
        "chunk_id": "chunk_007",
        "doc_id": "doc_shanghai_pilot",
        "title": "上海市数据要素市场化配置试点方案",
        "source_name": "上海市人民政府",
        "publish_date": "2025-07-01",
        "authority_level": "B",
        "doc_type": "方案",
        "section_title": "",
        "paragraph_index": 0,
        "topics": ["数据要素", "试点", "上海"],
        "policy_phrases": ["试点探索"],
        "text": (
            "试点探索数据要素市场化配置机制，"
            "在上海自贸区临港新片区率先开展数据跨境流动试点。"
            "目前仅在试点区域实施，不具备全国适用性。"
        ),
    },
]


@pytest.fixture
def index_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def _build_index(tmpdir):
    chunks_path = os.path.join(tmpdir, "chunks.jsonl")
    with open(chunks_path, "w", encoding="utf-8") as f:
        for chunk in SAMPLE_CHUNKS:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    builder = BM25IndexBuilder(tmpdir)
    builder.build(chunks_path)
    return builder


class TestRAGSearchAI:
    def test_can_search_ai_in_15th_fyp(self, index_dir):
        built_index = _build_index(index_dir)
        results = built_index.search("人工智能 十五五规划", top_k=3)
        assert len(results) >= 1
        assert any("人工智能" in r.get("text", "") for r in results)


class TestRAGSearchPolicyLanguage:
    def test_can_distinguish_chixu_vs_dali(self, index_dir):
        built_index = _build_index(index_dir)
        chixu_results = built_index.search("持续推进", top_k=5)
        dali_results = built_index.search("大力发展", top_k=5)
        assert len(chixu_results) >= 1 or len(dali_results) >= 1
        if chixu_results:
            has_phrase = any(
                "持续推进" in r.get("policy_phrases", [])
                for r in chixu_results
            )
            assert has_phrase or any(
                "持续推进" in r.get("text", "") for r in chixu_results
            )


class TestRAGSearchCityPolicy:
    def test_can_find_city_policy_documents(self, index_dir):
        built_index = _build_index(index_dir)
        results = built_index.search("北京 人工智能 产业", top_k=5)
        assert len(results) >= 1
        found = False
        for r in results:
            if "北京" in r.get("text", "") or "北京" in r.get("source_name", ""):
                found = True
            if "AI" in r.get("text", "") and "人工智能" in r.get(
                "topics", []
            ):
                found = True
        assert found


class TestRAGSearchForeignTrade:
    def test_can_find_foreign_trade_policy(self, index_dir):
        built_index = _build_index(index_dir)
        results = built_index.search("外贸 稳外资 政策", top_k=5)
        assert len(results) >= 1
        assert any("外贸" in r.get("text", "") for r in results)


class TestRAGSearchGeoConflict:
    def test_can_find_geo_conflict_sources(self, index_dir):
        built_index = _build_index(index_dir)
        results = built_index.search("外交部 坚决反对 核心利益", top_k=5)
        if len(results) < 1:
            results = built_index.search("风险上升 和平统一", top_k=5)
        assert len(results) >= 1


class TestRAGSourceQuality:
    def test_results_include_at_least_2_sources(self, index_dir):
        built_index = _build_index(index_dir)
        results = built_index.search(
            "人工智能 产业 数字经济", top_k=5
        )
        assert len(results) >= 2

    def test_results_include_title_institution_date(self, index_dir):
        built_index = _build_index(index_dir)
        results = built_index.search("人工智能", top_k=3)
        for r in results:
            assert "title" in r
            assert "source_name" in r
            assert "publish_date" in r
            assert r["title"] != ""
            assert r["source_name"] != ""

    def test_no_sourceless_conclusions(self, index_dir):
        built_index = _build_index(index_dir)
        results = built_index.search("数字经济", top_k=5)
        for r in results:
            assert r.get("source_name", "") != ""
            assert r.get("doc_id", "") != ""

    def test_no_deterministic_war_dates(self, index_dir):
        built_index = _build_index(index_dir)
        results = built_index.search("台海 冲突 风险", top_k=5)
        deterministic_patterns = [
            "必然开战",
            "确定开战",
            "一定爆发战争",
            "战争时间表",
        ]
        for r in results:
            text = r.get("text", "")
            for pattern in deterministic_patterns:
                assert pattern not in text

    def test_no_investment_advice(self, index_dir):
        built_index = _build_index(index_dir)
        results = built_index.search("人工智能 投资", top_k=5)
        investment_patterns = ["建议买入", "推荐购买", "保证收益", "确定性回报"]
        for r in results:
            text = r.get("text", "")
            for pattern in investment_patterns:
                assert pattern not in text

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCES_PATH = ROOT / "config" / "sources.yaml"
SOURCE_GROUPS_PATH = ROOT / "config" / "source_groups.yaml"


def _load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _all_source_names() -> set[str]:
    registry = _load_yaml(SOURCES_PATH)
    return {
        source["name"]
        for sources in registry.values()
        for source in sources
        if isinstance(source, dict) and "name" in source
    }


def test_all_state_council_constituent_departments_are_covered():
    expected = {
        "外交部",
        "国防部",
        "国家发改委",
        "教育部",
        "科技部",
        "工信部",
        "国家民族事务委员会",
        "公安部",
        "国家安全部",
        "民政部",
        "司法部",
        "财政部",
        "人社部",
        "自然资源部",
        "生态环境部",
        "住建部",
        "交通运输部",
        "水利部",
        "农业农村部",
        "商务部",
        "文旅部",
        "国家卫健委",
        "退役军人事务部",
        "应急管理部",
        "人民银行",
        "审计署",
    }

    assert expected <= _all_source_names()


def test_all_provincial_capitals_and_requested_sar_cities_are_covered():
    expected = {
        "北京市",
        "天津市",
        "石家庄",
        "太原",
        "呼和浩特",
        "沈阳",
        "长春",
        "哈尔滨",
        "上海市",
        "南京",
        "杭州",
        "合肥",
        "福州",
        "南昌",
        "济南",
        "郑州",
        "武汉",
        "长沙",
        "广州",
        "南宁",
        "海口",
        "重庆市",
        "成都",
        "贵阳",
        "昆明",
        "拉萨",
        "西安",
        "兰州",
        "西宁",
        "银川",
        "乌鲁木齐",
        "深圳",
        "香港",
        "澳门",
    }

    assert expected <= _all_source_names()


def test_requested_foreign_primary_sources_are_covered():
    expected = {
        "白宫",
        "美联储",
        "美国财政部",
        "美国商务部",
        "美国联邦公报",
        "特朗普Truth Social",
        "日本银行",
        "日本首相官邸",
        "日本财务省",
        "日本经济产业省",
        "欧洲央行",
        "欧盟委员会贸易总司",
        "英格兰银行",
        "加拿大银行",
    }

    assert expected <= _all_source_names()


def test_tariff_and_foreign_macro_sources_are_scheduled():
    groups = _load_yaml(SOURCE_GROUPS_PATH)["source_groups"]
    foreign_sources = groups["foreign_policy_daily"]["sources"]

    tariff_group = next(
        item for item in foreign_sources if item["category"] == "foreign_trade_policy_sources"
    )
    assert "财政部关税司" in tariff_group["items"]
    assert any(
        item["category"] == "foreign_macro_policy_sources" and item["include_all"]
        for item in foreign_sources
    )

from __future__ import annotations

import re
from typing import Dict, List, Tuple


_S_PATTERNS: Tuple[str, ...] = (
    "全国人民代表大会",
    "国务院",
    "中共中央",
    "中央军委",
)

_A_PATTERNS: Tuple[str, ...] = (
    "国家发改委",
    "国家发展和改革委员会",
    "国家发展改革委",
    "财政部",
    "中国人民银行",
    "工信部",
    "工业和信息化部",
    "商务部",
    "教育部",
    "科技部",
    "科学技术部",
    "住建部",
    "住房和城乡建设部",
    "交通运输部",
    "农业农村部",
    "生态环境部",
    "自然资源部",
    "人社部",
    "人力资源和社会保障部",
    "国家卫健委",
    "国家卫生健康委员会",
    "市场监管总局",
    "国家市场监督管理总局",
    "海关总署",
    "审计署",
    "司法部",
    "外交部",
    "国防部",
    "公安部",
    "国家安全部",
    "民政部",
    "水利部",
    "文旅部",
    "文化和旅游部",
    "应急管理部",
    "退役军人事务部",
)

_B_PATTERNS: Tuple[str, ...] = (
    "省人民政府",
    "市人民政府",
    "自治区人民政府",
    "直辖市人民政府",
)

_C_PATTERNS: Tuple[str, ...] = (
    "厅",
    "局",
    "委员会",
    "办公室",
    "办事机构",
    "县",
)

_D_PATTERNS: Tuple[str, ...] = (
    "行业协会",
    "联合会",
    "学会",
    "研究会",
    "商会",
    "基金会",
    "事业单位",
    "研究院",
    "研究所",
    "高校",
    "大学",
    "学院",
)

_E_PATTERNS: Tuple[str, ...] = (
    "公司",
    "集团",
    "有限",
    "股份",
    "媒体",
    "咨询",
    "智库",
)


_URL_GOV_CN = re.compile(r"\.gov\.cn")
_URL_COURT = re.compile(r"court|court\.gov\.cn|裁判文书", re.IGNORECASE)
_URL_PROCURATORATE = re.compile(r"procuratorate|jcy\.gov\.cn|检察院", re.IGNORECASE)


class AuthorityClassifier:
    def classify(self, source_name: str, url: str = "") -> str:
        if not source_name and not url:
            return "E"

        combined = f"{source_name} {url}"

        for pattern in _S_PATTERNS:
            if pattern in combined:
                return "S"

        if _URL_COURT.search(combined) or "法院" in combined:
            return "A"

        if _URL_PROCURATORATE.search(combined) or "检察院" in combined:
            return "A"

        for pattern in _A_PATTERNS:
            if pattern in combined:
                return "A"

        for pattern in _B_PATTERNS:
            if pattern in combined:
                return "B"

        if _URL_GOV_CN.search(combined):
            return "B"

        for pattern in _C_PATTERNS:
            if pattern in combined:
                return "C"

        for pattern in _D_PATTERNS:
            if pattern in combined:
                return "D"

        for pattern in _E_PATTERNS:
            if pattern in combined:
                return "E"

        return "E"

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DocumentMetadata:
    title: str = ""
    publish_date: Optional[str] = None
    author: str = ""
    organization: str = ""
    doc_type: str = ""
    source_url: str = ""
    doc_number: str = ""
    issuing_body: str = ""


DOC_TYPE_PATTERNS: List[re.Pattern] = [
    (re.compile(r"通\s*知"), "通知"),
    (re.compile(r"意\s*见"), "意见"),
    (re.compile(r"规\s*划"), "规划"),
    (re.compile(r"报\s*告"), "报告"),
    (re.compile(r"决\s*定"), "决定"),
    (re.compile(r"办\s*法"), "办法"),
    (re.compile(r"条\s*例"), "条例"),
    (re.compile(r"法\s*律"), "法律"),
    (re.compile(r"公\s*告"), "公告"),
    (re.compile(r"函"), "函"),
    (re.compile(r"批\s*复"), "批复"),
    (re.compile(r"议\s*案"), "议案"),
    (re.compile(r"指\s*南"), "指南"),
    (re.compile(r"标\s*准"), "标准"),
    (re.compile(r"规\s*定"), "规定"),
    (re.compile(r"细\s*则"), "细则"),
    (re.compile(r"方\s*案"), "方案"),
    (re.compile(r"解\s*释"), "解释"),
    (re.compile(r"纪\s*要"), "纪要"),
]

CHINESE_DATE_PATTERN = re.compile(
    r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})?\s*日?"
)
CHINESE_DATE_SHORT_PATTERN = re.compile(r"(\d{4})\s*年\s*(\d{1,2})\s*月")
ISO_DATE_PATTERN = re.compile(r"(\d{4})-(\d{1,2})-(\d{1,2})")
COMPACT_DATE_PATTERN = re.compile(r"(\d{4})(\d{2})(\d{2})")

ORG_PATTERNS = [
    re.compile(r"(?:印发|发布|制定)[^\n]*?([\u4e00-\u9fff]+(?:部|委|局|厅|署|院|办|处|室|会|司|中心))"),
    re.compile(r"([\u4e00-\u9fff]+(?:部|委员会|委|局|厅|署|院|办|处|室|会|司|中心))"),
    re.compile(r"([\u4e00-\u9fff]*(?:国务院|省政府|市政府|县政府|区人民政府))"),
]

NOISE_ORGS = {"部位", "部位:", "部门", "部委", "办公", "会议", "机构", "全部"}


class MetadataExtractor:
    TITLE_PATTERNS = [
        re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL),
        re.compile(r'<meta[^>]+(?:property|name)=["\']og:title["\'][^>]+content=["\'](.*?)["\']', re.IGNORECASE),
        re.compile(r'<meta[^>]+(?:property|name)=["\']article:title["\'][^>]+content=["\'](.*?)["\']', re.IGNORECASE),
        re.compile(r'<h1[^>]*>(.*?)</h1>', re.IGNORECASE | re.DOTALL),
    ]

    DATE_PATTERNS_HTML = [
        re.compile(r'<meta[^>]+(?:property|name)=["\']article:published_time["\'][^>]+content=["\'](.*?)["\']', re.IGNORECASE),
        re.compile(r'<meta[^>]+(?:property|name)=["\']pubdate["\'][^>]+content=["\'](.*?)["\']', re.IGNORECASE),
        re.compile(r'<meta[^>]+(?:property|name)=["\']date["\'][^>]+content=["\'](.*?)["\']', re.IGNORECASE),
        re.compile(r'<time[^>]+datetime=["\'](.*?)["\']', re.IGNORECASE),
    ]

    AUTHOR_PATTERNS = [
        re.compile(r'<meta[^>]+(?:property|name)=["\']author["\'][^>]+content=["\'](.*?)["\']', re.IGNORECASE),
        re.compile(r'<meta[^>]+(?:property|name)=["\']article:author["\'][^>]+content=["\'](.*?)["\']', re.IGNORECASE),
    ]

    DOC_NUMBER_PATTERNS = [
        re.compile(r'(国发〔\d{4}〕\d+号)'),
        re.compile(r'(国办发〔\d{4}〕\d+号)'),
        re.compile(r'(中办发〔\d{4}〕\d+号)'),
        re.compile(r'(国函〔\d{4}〕\d+号)'),
        re.compile(r'(国办函〔\d{4}〕\d+号)'),
        re.compile(r'(主席令第\d+号)'),
        re.compile(r'(国务院令第\d+号)'),
        re.compile(r'(〔\d{4}〕\d+号)'),
    ]

    TITLE_SUFFIX_RE = re.compile(r'[_—–\-]\s*(中国政府网|最新政策|其他|政策解读|宏观经济|海关|医药管理|新华社|新华网|人民网|求是网|国务院部门网站|地方政策).*$')

    HTML_TAG_RE = re.compile(r"<[^>]+>")
    WHITESPACE_RE = re.compile(r"\s+")

    def _strip_html(self, text: str) -> str:
        text = self.HTML_TAG_RE.sub("", text)
        text = self.WHITESPACE_RE.sub(" ", text)
        return text.strip()

    def _extract_title(self, html_or_text: str) -> str:
        for pattern in self.TITLE_PATTERNS:
            match = pattern.search(html_or_text)
            if match:
                title = self._strip_html(match.group(1))
                if title:
                    return title
        for line in html_or_text.split("\n")[:5]:
            line = line.strip()
            if line and len(line) < 200 and not line.startswith("<"):
                return self._strip_html(line)
        return ""

    def _extract_date_from_html(self, html_or_text: str) -> Optional[str]:
        for pattern in self.DATE_PATTERNS_HTML:
            match = pattern.search(html_or_text)
            if match:
                date_str = self._strip_html(match.group(1))
                if date_str:
                    return date_str

        cn_match = CHINESE_DATE_PATTERN.search(html_or_text)
        if cn_match:
            year = cn_match.group(1)
            month = cn_match.group(2).zfill(2)
            day = cn_match.group(3) or "01"
            day = day.zfill(2)
            return f"{year}-{month}-{day}"

        cn_short = CHINESE_DATE_SHORT_PATTERN.search(html_or_text)
        if cn_short:
            year = cn_short.group(1)
            month = cn_short.group(2).zfill(2)
            return f"{year}-{month}-01"

        iso_match = ISO_DATE_PATTERN.search(html_or_text)
        if iso_match:
            return f"{iso_match.group(1)}-{iso_match.group(2).zfill(2)}-{iso_match.group(3).zfill(2)}"

        compact_match = COMPACT_DATE_PATTERN.search(html_or_text)
        if compact_match:
            return f"{compact_match.group(1)}-{compact_match.group(2)}-{compact_match.group(3)}"

        return None

    def _extract_organization(self, html_or_text: str) -> str:
        text = self._strip_html(html_or_text)
        for pattern in ORG_PATTERNS:
            match = pattern.search(text)
            if match:
                org = match.group(1)
                if org not in NOISE_ORGS and len(org) >= 2:
                    return org
        return ""

    def _classify_doc_type(self, text: str) -> str:
        cleaned = self._strip_html(text)
        first_500 = cleaned[:500]
        for pattern, doc_type in DOC_TYPE_PATTERNS:
            if pattern.search(first_500):
                return doc_type
        return ""

    def _extract_author(self, html_or_text: str) -> str:
        for pattern in self.AUTHOR_PATTERNS:
            match = pattern.search(html_or_text)
            if match:
                author = self._strip_html(match.group(1))
                if author:
                    return author
        return ""

    def _clean_title(self, title: str) -> str:
        title = self.TITLE_SUFFIX_RE.sub("", title)
        return title.strip()

    def _extract_doc_number(self, html_or_text: str) -> str:
        text = self._strip_html(html_or_text)[:2000]
        for pattern in self.DOC_NUMBER_PATTERNS:
            match = pattern.search(text)
            if match:
                return match.group(1)
        return ""

    def _extract_issuing_body(self, html_or_text: str) -> str:
        text = self._strip_html(html_or_text)[:500]
        issuing_patterns = [
            re.compile(r'^(国务院办公厅|国务院|中共中央办公厅|中共中央|全国人大|全国政协)'),
            re.compile(r'(国家发展改革委|工业和信息化部|科学技术部|财政部|商务部|人力资源和社会保障部|自然资源部|生态环境部|住房和城乡建设部|交通运输部|农业农村部|文化和旅游部|国家卫生健康委员会|应急管理部|司法部|民政部|教育部|审计署|国家医疗保障局|国家能源局|海关总署|国家税务总局|国家市场监督管理总局|中国人民银行|中国证监会|国家金融监督管理总局|国家外汇管理局|公安部|最高人民检察院|最高人民法院)'),
        ]
        for pattern in issuing_patterns:
            match = pattern.search(text)
            if match:
                return match.group(1)
        return ""

    def extract(self, html_or_text: str, url: str = "") -> DocumentMetadata:
        metadata = DocumentMetadata(source_url=url)
        raw_title = self._extract_title(html_or_text)
        metadata.title = self._clean_title(raw_title)
        metadata.publish_date = self._extract_date_from_html(html_or_text)
        if metadata.publish_date and len(metadata.publish_date) > 10:
            metadata.publish_date = metadata.publish_date[:10]
        metadata.author = self._extract_author(html_or_text)
        metadata.organization = self._extract_organization(html_or_text)
        metadata.doc_type = self._classify_doc_type(html_or_text)
        metadata.doc_number = self._extract_doc_number(html_or_text)
        metadata.issuing_body = self._extract_issuing_body(html_or_text)

        if not metadata.organization and metadata.issuing_body:
            metadata.organization = metadata.issuing_body
        if not metadata.organization and metadata.author:
            metadata.organization = metadata.author

        return metadata

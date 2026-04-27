import re
import unicodedata
from dataclasses import dataclass
from typing import List


@dataclass
class Section:
    heading: str
    level: int
    content: str


class TextNormalizer:
    CHINESE_PUNCT_MAP = {
        "\u3000": " ",
        "\uff01": "！",
        "\uff0c": "，",
        "\uff1a": "：",
        "\uff1b": "；",
        "\uff1f": "？",
        "\uff08": "（",
        "\uff09": "）",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": """,
        "\u201d": """,
    }

    NOISE_PATTERNS = [
        re.compile(r"版权所有.*?(?=\n|$)", re.IGNORECASE),
        re.compile(r"Copyright\s*©.*?(?=\n|$)", re.IGNORECASE),
        re.compile(r"ICP备\d+号.*?(?=\n|$)"),
        re.compile(r"京公网安备.*?(?=\n|$)"),
        re.compile(r"技术支持.*?(?=\n|$)"),
        re.compile(r"备案号.*?(?=\n|$)"),
        re.compile(r"扫一扫.*?(?=\n|$)"),
        re.compile(r"关注微信.*?(?=\n|$)"),
        re.compile(r"下载APP.*?(?=\n|$)"),
        re.compile(r"\[广告\].*?(?=\n|$)"),
        re.compile(r"广告位.*?(?=\n|$)"),
        re.compile(r"相关推荐.*?(?=\n|$)"),
        re.compile(r"热门推荐.*?(?=\n|$)"),
        re.compile(r"\s*登录\s*注册\s*", re.IGNORECASE),
        re.compile(r"\s*设为首页\s*加入收藏\s*", re.IGNORECASE),
    ]

    HEADING_PATTERNS = [
        re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE),
        re.compile(r"^[一二三四五六七八九十百]+[、.．]\s*(.+)$", re.MULTILINE),
        re.compile(r"^第[一二三四五六七八九十百零\d]+[章节条部分篇]\s*(.+)$", re.MULTILINE),
        re.compile(r"^(\d+[.、．])\s*(.+)$", re.MULTILINE),
    ]

    def normalize(self, text: str) -> str:
        if not text:
            return ""

        try:
            text = text.encode("utf-8", errors="ignore").decode("utf-8")
        except Exception:
            pass

        try:
            text = unicodedata.normalize("NFC", text)
        except Exception:
            pass

        for fullwidth, target in self.CHINESE_PUNCT_MAP.items():
            text = text.replace(fullwidth, target)

        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()

        return text

    def extract_sections(self, text: str) -> List[Section]:
        if not text:
            return []

        lines = text.split("\n")
        sections: List[Section] = []
        current_heading = ""
        current_level = 0
        current_content_lines: List[str] = []

        for line in lines:
            is_heading = False
            heading_level = 0
            heading_text = ""

            md_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if md_match:
                heading_level = len(md_match.group(1))
                heading_text = md_match.group(2).strip()
                is_heading = True
            else:
                cn_section_match = re.match(r"^第[一二三四五六七八九十百零\d]+([章节条部分篇])\s*(.*)$", line)
                if cn_section_match:
                    sec_type = cn_section_match.group(1)
                    type_levels = {"篇": 1, "部分": 1, "章": 2, "节": 3, "条": 4}
                    heading_level = type_levels.get(sec_type, 2)
                    heading_text = line.strip()
                    is_heading = True
                else:
                    cn_num_match = re.match(r"^[一二三四五六七八九十百]+[、.．]\s*(.+)$", line)
                    if cn_num_match:
                        heading_level = 3
                        heading_text = line.strip()
                        is_heading = True
                    else:
                        num_match = re.match(r"^(\d+)[.、．]\s*(.+)$", line)
                        if num_match and len(num_match.group(2)) < 80:
                            heading_level = 4
                            heading_text = line.strip()
                            is_heading = True

            if is_heading:
                if current_heading or current_content_lines:
                    sections.append(
                        Section(
                            heading=current_heading,
                            level=current_level,
                            content="\n".join(current_content_lines).strip(),
                        )
                    )
                current_heading = heading_text
                current_level = heading_level
                current_content_lines = []
            else:
                current_content_lines.append(line)

        if current_heading or current_content_lines:
            sections.append(
                Section(
                    heading=current_heading,
                    level=current_level,
                    content="\n".join(current_content_lines).strip(),
                )
            )

        return sections

    def clean_noise(self, text: str) -> str:
        if not text:
            return ""

        for pattern in self.NOISE_PATTERNS:
            text = pattern.sub("", text)

        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+\n", "\n", text)

        return text.strip()

from typing import Optional

from lxml import etree
from markdownify import markdownify as md


class HTMLToMarkdown:
    CONTENT_SELECTORS = [
        "//*[contains(@class, 'pages_content')]",
        "//*[@id='UCAP_ARTICLE']",
        "//*[contains(@class, 'UCAP_ARTICLE')]",
        "//*[@id='zoom']",
        "//*[contains(@class, 'article-content')]",
        "//*[contains(@class, 'pages') and not(contains(@class, 'pagination'))]",
        "//*[contains(@class, 'content') and not(contains(@class, 'nav')) and not(contains(@class, 'sidebar')) and not(contains(@class, 'footer'))]",
        "//*[@id='content']",
        "//*[@role='main']",
        "//article",
    ]

    NOISE_TAGS = {"nav", "footer", "header", "aside", "script", "style", "noscript"}

    NOISE_CLASS_PATTERNS = [
        "sidebar", "footer", "navigation", "menu", "advertisement",
    ]

    def _build_tree(self, html: str) -> etree._Element:
        parser = etree.HTMLParser(encoding="utf-8")
        return etree.fromstring(html.encode("utf-8"), parser)

    def _strip_noise_from_tree(self, tree: etree._Element) -> None:
        for tag in self.NOISE_TAGS:
            for el in tree.xpath(f"//{tag}"):
                parent = el.getparent()
                if parent is not None:
                    parent.remove(el)

        for el in tree.xpath(
            "//*[@role='navigation' or @role='banner' or @role='contentinfo' or @role='complementary']"
        ):
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)

        for pattern in self.NOISE_CLASS_PATTERNS:
            for el in tree.xpath(f"//*[contains(@class, '{pattern}')]"):
                parent = el.getparent()
                if parent is not None:
                    parent.remove(el)

    def _find_main_content_element(self, tree: etree._Element) -> Optional[etree._Element]:
        for selector in self.CONTENT_SELECTORS:
            elements = tree.xpath(selector)
            for el in elements:
                text = "".join(el.itertext()).strip()
                if len(text) > 500:
                    return el
        return None

    def convert(self, html: str, url: str = "") -> str:
        tree = self._build_tree(html)
        self._strip_noise_from_tree(tree)

        main_el = self._find_main_content_element(tree)

        if main_el is not None:
            inner_html = etree.tostring(main_el, encoding="unicode", method="html")
        else:
            inner_html = etree.tostring(tree, encoding="unicode", method="html")

        markdown = md(
            inner_html,
            heading_style="ATX",
            bullets="-",
            code_language="",
            convert=[
                "table", "p", "a", "h1", "h2", "h3", "h4", "h5", "h6",
                "ul", "ol", "li", "blockquote", "pre", "code", "strong",
                "em", "br", "hr", "dl", "dt", "dd",
            ],
        )

        lines = markdown.split("\n")
        cleaned_lines: list[str] = []
        prev_blank = False
        for line in lines:
            if line.strip() == "":
                if not prev_blank:
                    cleaned_lines.append("")
                prev_blank = True
            else:
                cleaned_lines.append(line)
                prev_blank = False

        result = "\n".join(cleaned_lines).strip()

        if url:
            result = f"Source: {url}\n\n{result}"

        return result

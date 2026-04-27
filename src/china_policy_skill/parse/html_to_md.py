from typing import Optional

from markdownify import markdownify as md
from readability import Document


class HTMLToMarkdown:
    def __init__(self):
        self._noise_tags = {"nav", "footer", "header", "aside", "script", "style", "noscript"}

    def _strip_noise(self, html: str) -> str:
        from lxml import etree

        try:
            parser = etree.HTMLParser(encoding="utf-8")
            tree = etree.fromstring(html.encode("utf-8"), parser)
        except Exception:
            return html

        for tag in self._noise_tags:
            for el in tree.xpath(f"//{tag}"):
                parent = el.getparent()
                if parent is not None:
                    parent.remove(el)

        for el in tree.xpath("//*[@role='navigation' or @role='banner' or @role='contentinfo' or @role='complementary']"):
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)

        for el in tree.xpath("//*[contains(@class, 'sidebar') or contains(@class, 'footer') or contains(@class, 'navigation') or contains(@class, 'menu') or contains(@class, 'ad') or contains(@class, 'advertisement')]"):
            parent = el.getparent()
            if parent is not None:
                parent.remove(el)

        return etree.tostring(tree, encoding="unicode", method="html")

    def convert(self, html: str, url: str = "") -> str:
        cleaned = self._strip_noise(html)

        try:
            doc = Document(cleaned)
            summary_html = doc.summary()
        except Exception:
            summary_html = cleaned

        markdown = md(
            summary_html,
            heading_style="ATX",
            bullets="-",
            code_language="",
            strip=["img"],
            convert=["table", "p", "a", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "blockquote", "pre", "code", "strong", "em", "br", "hr", "dl", "dt", "dd"],
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

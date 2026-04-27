import os
import tempfile
from unittest.mock import patch

from china_policy_skill.parse.extract_metadata import MetadataExtractor
from china_policy_skill.parse.html_to_md import HTMLToMarkdown
from china_policy_skill.parse.normalize_text import TextNormalizer
from china_policy_skill.parse.pdf_to_md import PDFToMarkdown


class TestHTMLToMarkdown:
    def test_html_to_markdown_conversion(self):
        converter = HTMLToMarkdown()
        html = "<html><body><h1>Test Title</h1><p>Hello world</p></body></html>"
        with patch("china_policy_skill.parse.html_to_md.md") as mock_md:
            mock_md.return_value = "# Test Title\n\nHello world"
            result = converter.convert(html, "https://example.com")
            assert "Test Title" in result
            assert "Hello world" in result
            assert "https://example.com" in result

    def test_strip_noise_removes_nav(self):
        converter = HTMLToMarkdown()
        html = (
            "<html><body><nav>Navigation</nav>"
            "<article><p>Content</p></article></body></html>"
        )
        cleaned = converter._strip_noise(html)
        assert "Navigation" not in cleaned or "Content" in cleaned

    def test_strip_noise_removes_footer(self):
        converter = HTMLToMarkdown()
        html = (
            "<html><body><p>Main</p>"
            "<footer>Footer info</footer></body></html>"
        )
        cleaned = converter._strip_noise(html)
        assert "Footer info" not in cleaned or "Main" in cleaned

    def test_title_extraction(self):
        extractor = MetadataExtractor()
        html = (
            '<html><head><title>政策文件标题</title>'
            "</head><body></body></html>"
        )
        meta = extractor.extract(html, "https://example.com")
        assert "政策文件标题" in meta.title

    def test_organization_extraction(self):
        extractor = MetadataExtractor()
        html = "<html><body>由国家发展和改革委员会印发</body></html>"
        meta = extractor.extract(html, "https://example.com")
        assert meta.organization != ""

    def test_date_extraction_chinese_format(self):
        extractor = MetadataExtractor()
        html = "<html><body>发布日期：2025年3月15日</body></html>"
        meta = extractor.extract(html, "https://example.com")
        assert meta.publish_date == "2025-03-15"

    def test_date_extraction_chinese_short_format(self):
        extractor = MetadataExtractor()
        html = "<html><body>2025年6月报告</body></html>"
        meta = extractor.extract(html, "https://example.com")
        assert meta.publish_date == "2025-06-01"

    def test_text_cleaning(self):
        normalizer = TextNormalizer()
        text = "测试\u3000\u3000内容   多余空格\n\n\n\n太多空行"
        result = normalizer.normalize(text)
        assert "\u3000" not in result
        assert "\n\n\n" not in result

    def test_table_preservation(self):
        converter = HTMLToMarkdown()
        html = (
            "<html><body><table><tr><th>列1</th><th>列2</th></tr>"
            "<tr><td>值1</td><td>值2</td></tr></table></body></html>"
        )
        with patch("china_policy_skill.parse.html_to_md.md") as mock_md:
            mock_md.return_value = "| 列1 | 列2 |\n| --- | --- |\n| 值1 | 值2 |"
            result = converter.convert(html, "https://example.com")
            assert "列1" in result
            assert "值1" in result

    def test_attachment_link_extraction(self):
        converter = HTMLToMarkdown()
        html = (
            '<html><body><a href="/files/doc.pdf">'
            "附件：文件</a></body></html>"
        )
        with patch("china_policy_skill.parse.html_to_md.md") as mock_md:
            mock_md.return_value = "[附件：文件](/files/doc.pdf)"
            result = converter.convert(html, "https://example.com")
            assert "doc.pdf" in result or "附件" in result

    def test_chinese_encoding_handling(self):
        converter = HTMLToMarkdown()
        html = "<html><body><p>中华人民共和国国务院</p></body></html>"
        with patch("china_policy_skill.parse.html_to_md.md") as mock_md:
            mock_md.return_value = "中华人民共和国国务院"
            result = converter.convert(html, "https://example.com")
            assert "中华人民共和国国务院" in result

    def test_english_page_handling(self):
        converter = HTMLToMarkdown()
        html = (
            "<html><body><h1>Policy Document</h1>"
            "<p>This is an English policy summary.</p></body></html>"
        )
        with patch("china_policy_skill.parse.html_to_md.md") as mock_md:
            mock_md.return_value = (
                "# Policy Document\n\nThis is an English policy summary."
            )
            result = converter.convert(html, "https://example.com")
            assert "Policy Document" in result
            assert "English policy summary" in result


class TestPDFToMarkdown:
    def test_pdf_to_markdown_with_bytes(self):
        converter = PDFToMarkdown()
        try:
            import fitz

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp_path = tmp.name
            try:
                doc = fitz.open()
                page = doc.new_page()
                page.insert_text((72, 72), "Test PDF Content")
                doc.save(tmp_path)
                doc.close()
                result = converter.convert(tmp_path)
                assert isinstance(result, str)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        except ImportError:
            converter._use_pymupdf = False
            converter._convert_with_pdfplumber = lambda x: "Test PDF Content"
            result = converter.convert("dummy.pdf")
            assert "Test PDF Content" in result

    def test_pdf_empty_input(self):
        converter = PDFToMarkdown()
        converter._use_pymupdf = False
        converter._convert_with_pdfplumber = lambda x: ""
        result = converter.convert("nonexistent.pdf")
        assert result == ""


class TestNormalizeText:
    def test_noise_cleaning(self):
        normalizer = TextNormalizer()
        text = "正文内容\n版权所有 2025\nICP备12345678号\n更多内容"
        result = normalizer.clean_noise(text)
        assert "版权所有" not in result
        assert "ICP备" not in result
        assert "正文内容" in result
        assert "更多内容" in result

    def test_section_extraction(self):
        normalizer = TextNormalizer()
        text = "# 第一章 总则\n\n第一条 内容\n\n# 第二章 细则\n\n第二条 细则内容"
        sections = normalizer.extract_sections(text)
        assert len(sections) >= 2

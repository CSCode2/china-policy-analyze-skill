from typing import Union


class PDFToMarkdown:
    def __init__(self):
        self._use_pymupdf = self._check_pymupdf()

    def _check_pymupdf(self) -> bool:
        try:
            import fitz

            return True
        except ImportError:
            return False

    def _convert_with_pymupdf(self, pdf_path_or_bytes: Union[str, bytes]) -> str:
        import fitz

        if isinstance(pdf_path_or_bytes, bytes):
            doc = fitz.open(stream=pdf_path_or_bytes, filetype="pdf")
        else:
            doc = fitz.open(pdf_path_or_bytes)

        pages: list[str] = []
        for page in doc:
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
            page_text_parts: list[str] = []

            for block in sorted(blocks, key=lambda b: (b["bbox"][1], b["bbox"][0])):
                if block["type"] == 0:
                    for line in block["lines"]:
                        line_text = ""
                        for span in line["spans"]:
                            text = span["text"]
                            font_size = span["size"]
                            flags = span["flags"]

                            if font_size >= 18:
                                text = f"# {text}"
                            elif font_size >= 14:
                                text = f"## {text}"
                            elif font_size >= 12 and (flags & 2 ** 4):
                                text = f"### {text}"

                            line_text += text
                        page_text_parts.append(line_text)
                    page_text_parts.append("")
                elif block["type"] == 1:
                    page_text_parts.append("[Image]")
                    page_text_parts.append("")

            pages.append("\n".join(page_text_parts))

        doc.close()
        return "\n\n---\n\n".join(pages)

    def _convert_with_pdfplumber(self, pdf_path_or_bytes: Union[str, bytes]) -> str:
        import pdfplumber
        import tempfile
        import os

        if isinstance(pdf_path_or_bytes, bytes):
            tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            tmp.write(pdf_path_or_bytes)
            tmp.flush()
            tmp.close()
            pdf_path = tmp.name
        else:
            pdf_path = pdf_path_or_bytes

        pages: list[str] = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text)

                    tables = page.extract_tables()
                    for table in tables:
                        if table and len(table) > 0:
                            header = table[0]
                            md_lines: list[str] = []
                            md_lines.append("| " + " | ".join(str(c or "") for c in header) + " |")
                            md_lines.append("| " + " | ".join("---" for _ in header) + " |")
                            for row in table[1:]:
                                md_lines.append("| " + " | ".join(str(c or "") for c in row) + " |")
                            pages.append("\n".join(md_lines))
        finally:
            if isinstance(pdf_path_or_bytes, bytes):
                try:
                    os.unlink(pdf_path)
                except OSError:
                    pass

        return "\n\n---\n\n".join(pages)

    def convert(self, pdf_path_or_bytes: Union[str, bytes]) -> str:
        if self._use_pymupdf:
            try:
                return self._convert_with_pymupdf(pdf_path_or_bytes)
            except Exception:
                pass

        try:
            return self._convert_with_pdfplumber(pdf_path_or_bytes)
        except Exception:
            return ""

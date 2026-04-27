import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import requests

from china_policy_skill.fetch.fetch_html import HTMLFetcher
from china_policy_skill.fetch.fetch_pdf import PDFFetcher
from china_policy_skill.parse.pdf_to_md import PDFToMarkdown
from china_policy_skill.utils.hashing import content_hash, is_duplicate, record_hash


def _mock_response(
    status_code=200,
    content=b"<html><body>test</body></html>",
    content_type="text/html; charset=utf-8",
    headers=None,
):
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.content = content
    resp.text = content.decode("utf-8", errors="replace")
    resp.headers = {"Content-Type": content_type}
    if headers:
        resp.headers.update(headers)
    resp.encoding = "utf-8"
    resp.apparent_encoding = "utf-8"
    resp.elapsed = MagicMock()
    resp.elapsed.total_seconds.return_value = 0.5
    return resp


class TestHTMLFetchWithMock:
    def test_html_fetch_success(self):
        fetcher = HTMLFetcher(timeout=10, max_retries=0)
        mock_resp = _mock_response()
        with patch.object(fetcher._session, "get", return_value=mock_resp):
            result = fetcher.fetch("https://www.gov.cn/test")
        assert result.error is None
        assert result.status_code == 200
        assert result.html is not None
        assert "test" in result.html

    def test_html_fetch_404(self):
        fetcher = HTMLFetcher(timeout=10, max_retries=0)
        mock_resp = _mock_response(status_code=404)
        with patch.object(fetcher._session, "get", return_value=mock_resp):
            result = fetcher.fetch("https://www.gov.cn/notfound")
        assert result.error is not None
        assert "404" in result.error
        assert result.status_code == 404

    def test_html_fetch_429_rate_limit(self):
        fetcher = HTMLFetcher(timeout=10, max_retries=0)
        mock_resp = _mock_response(status_code=429)
        with patch.object(fetcher._session, "get", return_value=mock_resp):
            result = fetcher.fetch("https://www.gov.cn/ratelimited")
        assert result.error is not None
        assert "429" in result.error

    def test_html_fetch_timeout_retry(self):
        fetcher = HTMLFetcher(timeout=1, max_retries=2, backoff_factor=0.01)
        with patch.object(
            fetcher._session, "get", side_effect=requests.exceptions.Timeout()
        ):
            result = fetcher.fetch("https://www.gov.cn/timeout")
        assert result.error is not None
        assert "timed out" in result.error.lower()

    def test_html_content_type_validation(self):
        fetcher = HTMLFetcher(timeout=10, max_retries=0)
        mock_resp = _mock_response(content_type="application/pdf")
        with patch.object(fetcher._session, "get", return_value=mock_resp):
            result = fetcher.fetch("https://www.gov.cn/file.pdf")
        assert result.error is not None
        assert "Not HTML" in result.error


class TestPDFFetchWithMock:
    def test_pdf_fetch_success(self):
        fetcher = PDFFetcher(timeout=10, max_retries=0)
        mock_resp = MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.headers = {
            "Content-Type": "application/pdf",
            "Content-Length": "1024",
        }
        mock_resp.iter_content.return_value = iter([b"%PDF-1.4 test content"])
        with patch.object(fetcher._session, "get", return_value=mock_resp):
            result = fetcher.fetch("https://www.gov.cn/test.pdf")
        assert result.error is None
        assert result.status_code == 200
        assert result.content is not None

    def test_pdf_fetch_404(self):
        fetcher = PDFFetcher(timeout=10, max_retries=0)
        mock_resp = MagicMock(spec=requests.Response)
        mock_resp.status_code = 404
        mock_resp.headers = {"Content-Type": "text/html"}
        with patch.object(fetcher._session, "get", return_value=mock_resp):
            result = fetcher.fetch("https://www.gov.cn/notfound.pdf")
        assert result.error is not None
        assert "404" in result.error

    def test_pdf_content_type_validation(self):
        fetcher = PDFFetcher(timeout=10, max_retries=0)
        mock_resp = MagicMock(spec=requests.Response)
        mock_resp.status_code = 200
        mock_resp.headers = {"Content-Type": "text/html"}
        with patch.object(fetcher._session, "get", return_value=mock_resp):
            result = fetcher.fetch("https://www.gov.cn/actually-html")
        assert result.error is not None
        assert "Not PDF" in result.error


class TestHashDedup:
    def test_hash_dedup_skips_duplicate(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = os.path.join(tmpdir, "hash_store.json")
            h = content_hash("duplicate content")
            record_hash(h, "doc_001", store_path)
            assert is_duplicate(h, store_path) is True
            assert is_duplicate(content_hash("unique content"), store_path) is False


class TestMetadataExtractionFailure:
    def test_metadata_extract_no_crash_on_empty(self):
        from china_policy_skill.parse.extract_metadata import MetadataExtractor

        extractor = MetadataExtractor()
        metadata = extractor.extract("", "")
        assert metadata.title == ""
        assert metadata.publish_date is None

    def test_metadata_extract_no_crash_on_malformed_html(self):
        from china_policy_skill.parse.extract_metadata import MetadataExtractor

        extractor = MetadataExtractor()
        metadata = extractor.extract("<html><<broken", "https://example.com")
        assert metadata.source_url == "https://example.com"


class TestFetchErrorsLogging:
    def test_parse_failed_writes_to_fetch_errors(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            error_log = os.path.join(tmpdir, "fetch_errors.jsonl")
            entry = {
                "source": "www.gov.cn",
                "url": "https://www.gov.cn/broken",
                "error": "HTTP error: 500",
                "timestamp": "2026-04-27T00:00:00",
            }
            with open(error_log, "w", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            with open(error_log, "r", encoding="utf-8") as f:
                loaded = json.loads(f.readline())
            assert loaded["source"] == "www.gov.cn"
            assert loaded["error"] == "HTTP error: 500"


class TestFallbackParser:
    def test_fallback_parser_called_on_pymupdf_failure(self):
        converter = PDFToMarkdown()
        converter._use_pymupdf = True
        converter._convert_with_pymupdf = MagicMock(
            side_effect=Exception("pymupdf crashed")
        )

        with patch.object(
            converter,
            "_convert_with_pdfplumber",
            return_value="fallback text",
        ) as mock_plumber:
            result = converter.convert(b"%PDF-1.4 test")
            assert result == "fallback text"
            mock_plumber.assert_called_once()

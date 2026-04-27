import os
import tempfile
from dataclasses import dataclass
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class PDFFetchResult:
    url: str
    status_code: Optional[int] = None
    content: Optional[bytes] = None
    file_path: Optional[str] = None
    error: Optional[str] = None


class PDFFetcher:
    def __init__(
        self,
        timeout: int = 60,
        max_retries: int = 3,
        max_size_mb: int = 50,
        user_agent: str = "ChinaPolicySkill/0.1.0",
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_size_mb = max_size_mb
        self.user_agent = user_agent
        self._session = self._build_session()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1.0,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({"User-Agent": self.user_agent})
        return session

    def _is_pdf_content(self, response: requests.Response) -> bool:
        content_type = response.headers.get("Content-Type", "").lower()
        return "application/pdf" in content_type

    def fetch(self, url: str, save_to: Optional[str] = None) -> PDFFetchResult:
        result = PDFFetchResult(url=url)

        try:
            response = self._session.get(
                url, timeout=self.timeout, stream=True
            )
            result.status_code = response.status_code

            if response.status_code >= 400:
                result.error = f"HTTP error: {response.status_code}"
                return result

            content_length = response.headers.get("Content-Length")
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb > self.max_size_mb:
                    result.error = f"File too large: {size_mb:.1f}MB exceeds {self.max_size_mb}MB limit"
                    return result

            if not self._is_pdf_content(response):
                result.error = f"Not PDF content: {response.headers.get('Content-Type', 'unknown')}"
                return result

            content = b""
            downloaded = 0
            max_bytes = self.max_size_mb * 1024 * 1024
            for chunk in response.iter_content(chunk_size=8192):
                downloaded += len(chunk)
                if downloaded > max_bytes:
                    result.error = f"File too large: exceeded {self.max_size_mb}MB limit during download"
                    return result
                content += chunk

            result.content = content

            if save_to:
                os.makedirs(os.path.dirname(save_to) or ".", exist_ok=True)
                with open(save_to, "wb") as f:
                    f.write(content)
                result.file_path = save_to
            else:
                tmp = tempfile.NamedTemporaryFile(
                    suffix=".pdf", delete=False
                )
                tmp.write(content)
                tmp.flush()
                tmp.close()
                result.file_path = tmp.name

        except requests.exceptions.Timeout:
            result.error = "Request timed out"
        except requests.exceptions.ConnectionError:
            result.error = "Connection error"
        except requests.exceptions.RequestException as exc:
            result.error = str(exc)
        except OSError as exc:
            result.error = f"File error: {exc}"

        return result

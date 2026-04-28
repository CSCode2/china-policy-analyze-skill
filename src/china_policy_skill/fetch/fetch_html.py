import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class FetchResult:
    url: str
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    encoding: Optional[str] = None
    html: Optional[str] = None
    text: Optional[str] = None
    error: Optional[str] = None
    elapsed: float = 0.0


class HTMLFetcher:
    _BROWSER_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        rate_limit_delay: float = 1.0,
        user_agent: str = "",
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.rate_limit_delay = rate_limit_delay
        self.user_agent = user_agent
        self._session = self._build_session()
        self._last_request_time: float = 0.0

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        headers = dict(self._BROWSER_HEADERS)
        if self.user_agent:
            headers["User-Agent"] = self.user_agent
        session.headers.update(headers)
        return session

    def _rate_limit(self) -> None:
        now = time.monotonic()
        elapsed_since_last = now - self._last_request_time
        if elapsed_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed_since_last)
        self._last_request_time = time.monotonic()

    def _detect_encoding(self, response: requests.Response) -> str:
        content_type = response.headers.get("Content-Type", "")
        if "charset" in content_type.lower():
            return response.encoding or "utf-8"
        if response.apparent_encoding:
            return response.apparent_encoding
        try:
            import chardet

            detected = chardet.detect(response.content)
            if detected and detected.get("encoding"):
                return detected["encoding"]
        except Exception:
            pass
        return "utf-8"

    def _is_html_content(self, response: requests.Response) -> bool:
        content_type = response.headers.get("Content-Type", "").lower()
        return "text/html" in content_type or "application/xhtml" in content_type

    def fetch(self, url: str) -> FetchResult:
        self._rate_limit()
        start = time.monotonic()
        result = FetchResult(url=url)

        last_error: Optional[str] = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self._session.get(url, timeout=self.timeout)
                result.status_code = response.status_code
                result.content_type = response.headers.get("Content-Type")
                result.elapsed = time.monotonic() - start

                if response.status_code >= 500:
                    last_error = f"Server error: {response.status_code}"
                    if attempt < self.max_retries:
                        wait = self.backoff_factor * (2 ** attempt)
                        time.sleep(wait)
                        continue
                    result.error = last_error
                    return result

                if response.status_code >= 400:
                    result.error = f"HTTP error: {response.status_code}"
                    return result

                if not self._is_html_content(response):
                    result.error = f"Not HTML content: {result.content_type}"
                    return result

                encoding = self._detect_encoding(response)
                result.encoding = encoding
                result.html = response.content.decode(encoding, errors="replace")
                result.text = result.html
                return result

            except requests.exceptions.Timeout:
                last_error = "Request timed out"
                if attempt < self.max_retries:
                    wait = self.backoff_factor * (2 ** attempt)
                    time.sleep(wait)
                    continue
            except requests.exceptions.ConnectionError:
                last_error = "Connection error"
                if attempt < self.max_retries:
                    wait = self.backoff_factor * (2 ** attempt)
                    time.sleep(wait)
                    continue
            except requests.exceptions.RequestException as exc:
                last_error = str(exc)
                break

        result.error = last_error
        result.elapsed = time.monotonic() - start
        return result

    def fetch_list_page(
        self, url: str, parser_fn: Optional[Callable[[str], List[dict]]] = None
    ) -> List[dict]:
        result = self.fetch(url)
        if result.error or not result.html:
            return []
        if parser_fn is None:
            return [{"url": url, "html": result.html}]
        try:
            return parser_fn(result.html)
        except Exception:
            return []

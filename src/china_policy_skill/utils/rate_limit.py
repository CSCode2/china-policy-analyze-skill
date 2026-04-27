import re
import time
from collections import defaultdict
from typing import Dict, Optional
from urllib.parse import urlparse


class RateLimiter:
    def __init__(self, default_delay: float = 1.0):
        self.default_delay = default_delay
        self._domain_last_request: Dict[str, float] = defaultdict(float)
        self._domain_delays: Dict[str, float] = defaultdict(lambda: default_delay)
        self._retry_after: Dict[str, float] = {}

    def _get_domain(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc

    def wait(self, url: str) -> None:
        domain = self._get_domain(url)
        now = time.monotonic()

        retry_after_time = self._retry_after.get(domain)
        if retry_after_time and now < retry_after_time:
            sleep_time = retry_after_time - now
            time.sleep(sleep_time)
            del self._retry_after[domain]
            now = time.monotonic()

        last_request = self._domain_last_request[domain]
        delay = self._domain_delays[domain]
        elapsed = now - last_request

        if elapsed < delay:
            time.sleep(delay - elapsed)

        self._domain_last_request[domain] = time.monotonic()

    def update_limits_from_headers(self, headers: Dict[str, str], url: str = "") -> None:
        domain = self._get_domain(url) if url else ""

        retry_after = headers.get("Retry-After")
        if retry_after:
            now = time.monotonic()
            try:
                wait_seconds = int(retry_after)
                self._retry_after[domain] = now + wait_seconds
            except ValueError:
                try:
                    from email.utils import parsedate_to_datetime

                    retry_date = parsedate_to_datetime(retry_after)
                    wait_seconds = max(0, (retry_date - retry_date.utcnow().replace(tzinfo=retry_date.tzinfo)).total_seconds())
                    self._retry_after[domain] = now + wait_seconds
                except Exception:
                    self._retry_after[domain] = now + self.default_delay

        x_rate_limit_remaining = headers.get("X-RateLimit-Remaining")
        if x_rate_limit_remaining is not None:
            try:
                remaining = int(x_rate_limit_remaining)
                if remaining <= 1:
                    reset = headers.get("X-RateLimit-Reset")
                    if reset:
                        try:
                            reset_time = int(reset)
                            now_ts = int(time.time())
                            wait_seconds = max(0, reset_time - now_ts)
                            self._retry_after[domain] = time.monotonic() + wait_seconds
                        except ValueError:
                            self._domain_delays[domain] = max(self._domain_delays[domain], self.default_delay * 2)
                    else:
                        self._domain_delays[domain] = max(self._domain_delays[domain], self.default_delay * 2)
            except ValueError:
                pass

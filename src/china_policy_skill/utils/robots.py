import time
from typing import Dict, Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser


class RobotsChecker:
    def __init__(self, cache_ttl: float = 3600.0):
        self.cache_ttl = cache_ttl
        self._parsers: Dict[str, RobotFileParser] = {}
        self._cache_times: Dict[str, float] = {}

    def _get_domain(self, url: str) -> str:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _get_robots_url(self, domain: str) -> str:
        return f"{domain}/robots.txt"

    def _get_parser(self, domain: str) -> Optional[RobotFileParser]:
        now = time.time()
        cached_time = self._cache_times.get(domain, 0)

        if domain not in self._parsers or (now - cached_time) > self.cache_ttl:
            robots_url = self._get_robots_url(domain)
            parser = RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
            except Exception:
                self._parsers[domain] = parser
                self._cache_times[domain] = now
                return parser

            self._parsers[domain] = parser
            self._cache_times[domain] = now

        return self._parsers.get(domain)

    def is_allowed(self, url: str, user_agent: str = "ChinaPolicySkill") -> bool:
        domain = self._get_domain(url)
        parser = self._get_parser(domain)

        if parser is None:
            return True

        try:
            return parser.can_fetch(user_agent, url)
        except Exception:
            return True

    def get_crawl_delay(self, domain: str, user_agent: str = "ChinaPolicySkill") -> float:
        if not domain.startswith(("http://", "https://")):
            domain = f"https://{domain}"

        parser = self._get_parser(domain)

        if parser is None:
            return 0.0

        try:
            delay = parser.crawl_delay(user_agent)
            if delay is not None:
                return delay
        except Exception:
            pass

        try:
            request_rate = parser.request_rate(user_agent)
            if request_rate is not None:
                return 1.0 / request_rate.requests if request_rate.requests > 0 else 0.0
        except Exception:
            pass

        return 0.0

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional

import requests


@dataclass
class SitemapURL:
    loc: str = ""
    lastmod: str = ""
    changefreq: str = ""
    priority: float = 0.0


SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class SitemapFetcher:
    def __init__(
        self,
        timeout: int = 30,
        user_agent: str = "ChinaPolicySkill/0.1.0",
    ):
        self.timeout = timeout
        self.user_agent = user_agent
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self.user_agent})

    def _parse_urlset(self, root: ET.Element) -> List[SitemapURL]:
        urls: List[SitemapURL] = []
        for url_el in root.findall(f"{SITEMAP_NS}url"):
            sitemap_url = SitemapURL()
            loc_el = url_el.find(f"{SITEMAP_NS}loc")
            if loc_el is not None and loc_el.text:
                sitemap_url.loc = loc_el.text.strip()
            lastmod_el = url_el.find(f"{SITEMAP_NS}lastmod")
            if lastmod_el is not None and lastmod_el.text:
                sitemap_url.lastmod = lastmod_el.text.strip()
            changefreq_el = url_el.find(f"{SITEMAP_NS}changefreq")
            if changefreq_el is not None and changefreq_el.text:
                sitemap_url.changefreq = changefreq_el.text.strip()
            priority_el = url_el.find(f"{SITEMAP_NS}priority")
            if priority_el is not None and priority_el.text:
                try:
                    sitemap_url.priority = float(priority_el.text.strip())
                except ValueError:
                    sitemap_url.priority = 0.0
            urls.append(sitemap_url)
        return urls

    def _parse_sitemap_index(self, root: ET.Element) -> List[SitemapURL]:
        urls: List[SitemapURL] = []
        for sitemap_el in root.findall(f"{SITEMAP_NS}sitemap"):
            sitemap_url = SitemapURL()
            loc_el = sitemap_el.find(f"{SITEMAP_NS}loc")
            if loc_el is not None and loc_el.text:
                sitemap_url.loc = loc_el.text.strip()
            lastmod_el = sitemap_el.find(f"{SITEMAP_NS}lastmod")
            if lastmod_el is not None and lastmod_el.text:
                sitemap_url.lastmod = lastmod_el.text.strip()
            urls.append(sitemap_url)
        return urls

    def _is_sitemap_index(self, root: ET.Element) -> bool:
        return root.tag == f"{SITEMAP_NS}sitemapindex"

    def fetch(self, url: str) -> List[SitemapURL]:
        try:
            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException:
            return []

        try:
            root = ET.fromstring(response.content)
        except ET.ParseError:
            return []

        if self._is_sitemap_index(root):
            return self._parse_sitemap_index(root)

        return self._parse_urlset(root)

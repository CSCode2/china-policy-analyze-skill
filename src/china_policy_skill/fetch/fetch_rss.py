import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urljoin

import requests


@dataclass
class RSSItem:
    title: str = ""
    link: str = ""
    pub_date: str = ""
    description: str = ""


ATOM_NS = "{http://www.w3.org/2005/Atom}"
RSS_NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "dc": "http://purl.org/dc/elements/1.1/",
    "content": "http://purl.org/rss/1.0/modules/content/",
}


class RSSFetcher:
    def __init__(
        self,
        timeout: int = 30,
        user_agent: str = "ChinaPolicySkill/0.1.0",
    ):
        self.timeout = timeout
        self.user_agent = user_agent
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self.user_agent})

    def _normalize_tag(self, tag: str) -> str:
        if "}" in tag:
            return tag.split("}", 1)[1]
        return tag

    def _get_text(self, element: Optional[ET.Element], tag: str) -> str:
        if element is None:
            return ""
        child = element.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        for ns_prefix, ns_uri in RSS_NAMESPACES.items():
            child = element.find(f"{{{ns_uri}}}{tag}")
            if child is not None and child.text:
                return child.text.strip()
        return ""

    def _parse_rss(self, root: ET.Element) -> List[RSSItem]:
        items: List[RSSItem] = []
        channel = root.find("channel")
        if channel is None:
            return items
        for item_el in channel.findall("item"):
            rss_item = RSSItem()
            rss_item.title = self._get_text(item_el, "title")
            rss_item.link = self._get_text(item_el, "link")
            rss_item.pub_date = self._get_text(item_el, "pubDate")
            if not rss_item.pub_date:
                rss_item.pub_date = self._get_text(item_el, "date")
            rss_item.description = self._get_text(item_el, "description")
            if not rss_item.description:
                desc_el = item_el.find("description")
                if desc_el is not None:
                    rss_item.description = (desc_el.text or "").strip()
            items.append(rss_item)
        return items

    def _parse_atom(self, root: ET.Element) -> List[RSSItem]:
        items: List[RSSItem] = []
        for entry in root.findall(f"{ATOM_NS}entry"):
            rss_item = RSSItem()
            title_el = entry.find(f"{ATOM_NS}title")
            if title_el is not None and title_el.text:
                rss_item.title = title_el.text.strip()
            link_el = entry.find(f"{ATOM_NS}link")
            if link_el is not None:
                rss_item.link = link_el.get("href", "")
            updated_el = entry.find(f"{ATOM_NS}updated")
            published_el = entry.find(f"{ATOM_NS}published")
            date_el = published_el if published_el is not None else updated_el
            if date_el is not None and date_el.text:
                rss_item.pub_date = date_el.text.strip()
            summary_el = entry.find(f"{ATOM_NS}summary")
            content_el = entry.find(f"{ATOM_NS}content")
            desc_el = summary_el if summary_el is not None else content_el
            if desc_el is not None and desc_el.text:
                rss_item.description = desc_el.text.strip()
            items.append(rss_item)
        return items

    def fetch(self, url: str) -> List[RSSItem]:
        try:
            response = self._session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException:
            return []

        try:
            root = ET.fromstring(response.content)
        except ET.ParseError:
            return []

        tag = self._normalize_tag(root.tag).lower()
        if tag == "rss":
            return self._parse_rss(root)
        elif tag == "feed":
            return self._parse_atom(root)
        channel = root.find("channel")
        if channel is not None:
            return self._parse_rss(root)
        return []

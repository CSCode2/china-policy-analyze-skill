import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote

import requests
import yaml
from lxml import etree

from china_policy_skill.fetch.fetch_html import HTMLFetcher, FetchResult
from china_policy_skill.parse.html_to_md import HTMLToMarkdown

_ACCOUNTS_YAML = Path(__file__).resolve().parents[3] / "config" / "wechat_accounts.yaml"


@dataclass
class WeChatArticle:
    title: str
    url: str
    abstract: str
    account_name: str = ""
    markdown: Optional[str] = None
    source: str = "wechat"


@dataclass
class WeChatAccount:
    name: str
    wechat_id: str = ""
    desc: str = ""
    authority: str = ""
    topics: List[str] = field(default_factory=list)
    search_tip: str = ""
    category: str = ""


def load_account_directory(yaml_path: Optional[str] = None) -> Dict[str, List[WeChatAccount]]:
    path = Path(yaml_path) if yaml_path else _ACCOUNTS_YAML
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    directory: Dict[str, List[WeChatAccount]] = {}
    for category, accounts in raw.items():
        if not isinstance(accounts, list):
            continue
        directory[category] = []
        for acc in accounts:
            if not isinstance(acc, dict) or "name" not in acc:
                continue
            directory[category].append(WeChatAccount(
                name=acc["name"],
                wechat_id=acc.get("wechat_id", ""),
                desc=acc.get("desc", ""),
                authority=acc.get("authority", ""),
                topics=acc.get("topics", []),
                search_tip=acc.get("search_tip", ""),
                category=category,
            ))
    return directory


class WeChatSearcher:
    _BROWSER_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
    }

    def __init__(self, timeout: int = 15, rate_limit_delay: float = 1.0):
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.fetcher = HTMLFetcher(timeout=timeout, rate_limit_delay=rate_limit_delay)
        self.parser = HTMLToMarkdown()
        self._account_dir: Optional[Dict[str, List[WeChatAccount]]] = None

    def search(self, query: str, max_results: int = 5) -> List[WeChatArticle]:
        session = requests.Session()
        session.headers.update(self._BROWSER_HEADERS)

        resp = session.get(
            f"https://weixin.sogou.com/weixin?type=2&query={quote(query)}&ie=utf8",
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            return []

        tree = etree.fromstring(resp.content, etree.HTMLParser())
        results: List[WeChatArticle] = []

        for a_el in tree.xpath("//h3/a[@href]"):
            href = a_el.get("href", "")
            title = "".join(a_el.itertext()).strip()
            if "/link?" not in href or not title:
                continue

            full_url = (
                f"https://weixin.sogou.com{href}"
                if href.startswith("/")
                else href
            )

            abstract = self._extract_abstract(a_el)

            session.headers["Referer"] = resp.url
            redirect_resp = session.get(full_url, timeout=self.timeout)
            redirect_html = redirect_resp.text

            url_fragments = re.findall(r"url\s*\+=\s*'([^']*)'", redirect_html)
            if not url_fragments:
                continue

            real_url = "".join(url_fragments)

            results.append(
                WeChatArticle(
                    title=title,
                    url=real_url,
                    abstract=abstract,
                )
            )

            if len(results) >= max_results:
                break

        return results

    def fetch_article(self, article: WeChatArticle) -> WeChatArticle:
        result = self.fetcher.fetch(article.url)
        if result.error:
            article.markdown = f"[ERROR: {result.error}]"
            return article

        html = result.html or ""
        if "rich_media_content" in html or "js_content" in html:
            article.markdown = self.parser.convert(html, article.url)
        else:
            article.markdown = self.parser.convert(html, article.url)
            if len(article.markdown) < 50:
                article.markdown = f"[Could not extract article content, got {len(html)} chars HTML]"

        return article

    def search_and_fetch(
        self, query: str, max_results: int = 3
    ) -> List[WeChatArticle]:
        articles = self.search(query, max_results=max_results)
        for article in articles:
            self.fetch_article(article)
        return articles

    @property
    def account_directory(self) -> Dict[str, List[WeChatAccount]]:
        if self._account_dir is None:
            self._account_dir = load_account_directory()
        return self._account_dir

    def get_account(self, name: str) -> Optional[WeChatAccount]:
        for accounts in self.account_directory.values():
            for acc in accounts:
                if acc.name == name or acc.wechat_id == name:
                    return acc
        return None

    def find_accounts_by_topic(self, topic: str) -> List[WeChatAccount]:
        topic_lower = topic.lower()
        matches: List[WeChatAccount] = []
        for accounts in self.account_directory.values():
            for acc in accounts:
                if any(topic_lower in t.lower() for t in acc.topics):
                    matches.append(acc)
                elif topic_lower in acc.desc.lower():
                    matches.append(acc)
        return matches

    def find_accounts_by_category(self, category: str) -> List[WeChatAccount]:
        cat_lower = category.lower()
        for key, accounts in self.account_directory.items():
            if cat_lower in key.lower():
                return accounts
        return []

    def search_by_account(
        self,
        account_name: str,
        keyword: str = "",
        max_results: int = 3,
    ) -> List[WeChatArticle]:
        acc = self.get_account(account_name)
        if acc and acc.search_tip:
            query = acc.search_tip
        else:
            query = account_name
        if keyword:
            query = f"{account_name} {keyword}"
        articles = self.search(query, max_results=max_results)
        for a in articles:
            a.account_name = account_name
        return articles

    def search_by_account_and_fetch(
        self,
        account_name: str,
        keyword: str = "",
        max_results: int = 3,
    ) -> List[WeChatArticle]:
        articles = self.search_by_account(account_name, keyword, max_results)
        for article in articles:
            self.fetch_article(article)
        return articles

    def search_by_category(
        self,
        category: str,
        keyword: str = "",
        max_results: int = 5,
    ) -> List[WeChatArticle]:
        accounts = self.find_accounts_by_category(category)
        if not accounts:
            return []
        results: List[WeChatArticle] = []
        for acc in accounts:
            query = f"{acc.name} {keyword}" if keyword else (acc.search_tip or acc.name)
            articles = self.search(query, max_results=1)
            for a in articles:
                a.account_name = acc.name
            results.extend(articles)
            if len(results) >= max_results:
                break
        return results[:max_results]

    def search_by_category_and_fetch(
        self,
        category: str,
        keyword: str = "",
        max_results: int = 5,
    ) -> List[WeChatArticle]:
        articles = self.search_by_category(category, keyword, max_results)
        for article in articles:
            self.fetch_article(article)
        return articles

    @staticmethod
    def _extract_abstract(a_el) -> str:
        parent = a_el.getparent()
        while parent is not None and "txt-box" not in (parent.get("class") or ""):
            parent = parent.getparent()
        if parent is not None:
            abs_el = parent.xpath('.//p[contains(@class,"txt-info")]')
            if abs_el:
                return "".join(abs_el[0].itertext()).strip()
        return ""

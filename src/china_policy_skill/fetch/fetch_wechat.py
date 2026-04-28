import re
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import quote

import requests
from lxml import etree

from china_policy_skill.fetch.fetch_html import HTMLFetcher, FetchResult
from china_policy_skill.parse.html_to_md import HTMLToMarkdown


@dataclass
class WeChatArticle:
    title: str
    url: str
    abstract: str
    markdown: Optional[str] = None
    source: str = "wechat"


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

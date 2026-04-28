import os
import tempfile
from unittest.mock import MagicMock, patch

import requests

from china_policy_skill.fetch.fetch_wechat import (
    WeChatAccount,
    WeChatArticle,
    WeChatSearcher,
    load_account_directory,
)


_SAMPLE_YAML = """\
central_policy:
  - name: 中国政府网
    wechat_id: zhengfuweixin
    desc: 国务院办公厅主办
    authority: S
    topics: [国务院文件, 政策解读]
    search_tip: "中国政府网 政策原文"

economy_finance:
  - name: 中国人民银行
    wechat_id: pbcgov
    desc: 央行官方号
    authority: A
    topics: [货币政策, 利率]
    search_tip: "中国人民银行 货币政策"
"""


class TestLoadAccountDirectory:
    def test_load_from_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as f:
            f.write(_SAMPLE_YAML)
            path = f.name
        try:
            directory = load_account_directory(path)
            assert "central_policy" in directory
            assert "economy_finance" in directory
            assert len(directory["central_policy"]) == 1
            acc = directory["central_policy"][0]
            assert acc.name == "中国政府网"
            assert acc.wechat_id == "zhengfuweixin"
            assert acc.authority == "S"
            assert "国务院文件" in acc.topics
            assert acc.category == "central_policy"
        finally:
            os.unlink(path)

    def test_load_missing_file(self):
        directory = load_account_directory("/nonexistent/path.yaml")
        assert directory == {}

    def test_load_empty_yaml(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as f:
            f.write("")
            path = f.name
        try:
            directory = load_account_directory(path)
            assert directory == {}
        finally:
            os.unlink(path)


class TestWeChatSearcherAccountLookup:
    def _searcher_with_dir(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as f:
            f.write(_SAMPLE_YAML)
            path = f.name
        searcher = WeChatSearcher()
        searcher._account_dir = load_account_directory(path)
        return searcher, path

    def test_get_account_by_name(self):
        searcher, path = self._searcher_with_dir()
        try:
            acc = searcher.get_account("中国政府网")
            assert acc is not None
            assert acc.wechat_id == "zhengfuweixin"
        finally:
            os.unlink(path)

    def test_get_account_by_wechat_id(self):
        searcher, path = self._searcher_with_dir()
        try:
            acc = searcher.get_account("pbcgov")
            assert acc is not None
            assert acc.name == "中国人民银行"
        finally:
            os.unlink(path)

    def test_get_account_not_found(self):
        searcher, path = self._searcher_with_dir()
        try:
            acc = searcher.get_account("不存在的号")
            assert acc is None
        finally:
            os.unlink(path)

    def test_find_accounts_by_topic(self):
        searcher, path = self._searcher_with_dir()
        try:
            matches = searcher.find_accounts_by_topic("货币政策")
            assert len(matches) >= 1
            assert any(a.name == "中国人民银行" for a in matches)
        finally:
            os.unlink(path)

    def test_find_accounts_by_category(self):
        searcher, path = self._searcher_with_dir()
        try:
            accounts = searcher.find_accounts_by_category("economy_finance")
            assert len(accounts) >= 1
            assert accounts[0].name == "中国人民银行"
        finally:
            os.unlink(path)

    def test_find_accounts_by_category_no_match(self):
        searcher, path = self._searcher_with_dir()
        try:
            accounts = searcher.find_accounts_by_category("nonexistent")
            assert accounts == []
        finally:
            os.unlink(path)


class TestWeChatSearchByAccount:
    def test_search_by_account_uses_search_tip(self):
        searcher = WeChatSearcher()
        mock_articles = [
            WeChatArticle(
                title="test policy",
                url="https://mp.weixin.qq.com/s/test",
                abstract="abstract",
            )
        ]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as f:
            f.write(_SAMPLE_YAML)
            path = f.name
        with patch.object(searcher, "search", return_value=mock_articles) as mock_search:
            searcher._account_dir = load_account_directory(path)
            results = searcher.search_by_account("中国政府网", keyword="最新")
            mock_search.assert_called_once_with("中国政府网 最新", max_results=3)
            assert len(results) == 1
            assert results[0].account_name == "中国政府网"
        os.unlink(path)

    def test_search_by_account_unknown_uses_name(self):
        searcher = WeChatSearcher()
        mock_articles = []
        with patch.object(searcher, "search", return_value=mock_articles) as mock_search:
            results = searcher.search_by_account("未知公众号", keyword="政策")
            mock_search.assert_called_once_with("未知公众号 政策", max_results=3)
            assert results == []


class TestWeChatArticleDataclass:
    def test_article_defaults(self):
        a = WeChatArticle(title="t", url="u", abstract="a")
        assert a.source == "wechat"
        assert a.account_name == ""
        assert a.markdown is None

    def test_article_with_account_name(self):
        a = WeChatArticle(title="t", url="u", abstract="a", account_name="央行")
        assert a.account_name == "央行"


class TestWeChatAccountDataclass:
    def test_account_defaults(self):
        a = WeChatAccount(name="test")
        assert a.wechat_id == ""
        assert a.topics == []
        assert a.authority == ""

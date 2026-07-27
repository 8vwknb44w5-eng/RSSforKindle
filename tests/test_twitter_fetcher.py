import pytest
from unittest.mock import MagicMock, patch
from src.config import ContentSource
from src.fetchers.twitter_fetcher import TwitterFetcher
from src.fetchers.base import FetchResult

# Mock FxTwitter JSON response data
MOCK_FXTWITTER_JSON = {
    "code": 200,
    "results": [
        {
            "type": "status",
            "id": "1111111111111111111",
            "url": "https://x.com/SomeoneElse/status/1111111111111111111",
            "text": "Check out this awesome post about physics! #science",
            "created_at": "Mon, 27 Jul 2026 10:00:00 GMT",
            "author": {
                "name": "Someone Else",
                "screen_name": "SomeoneElse"
            },
            "replying_to": None,
            "reposted_by": {
                "screen_name": "WolframResearch"
            },
            "media": {}
        },
        {
            "type": "status",
            "id": "2222222222222222222",
            "url": "https://x.com/WolframResearch/status/2222222222222222222",
            "text": "We are working on a fix for that issue. Stay tuned!",
            "created_at": "Mon, 27 Jul 2026 11:00:00 GMT",
            "author": {
                "name": "Wolfram",
                "screen_name": "WolframResearch"
            },
            "replying_to": {
                "screen_name": "some_user"
            },
            "reposted_by": None,
            "media": {}
        },
        {
            "type": "status",
            "id": "3333333333333333333",
            "url": "https://x.com/WolframResearch/status/3333333333333333333",
            "text": "This is a normal tweet! Check our blog for the latest update. It is extremely long and will definitely exceed eighty characters in length to test the truncation logic of the TwitterFetcher.",
            "created_at": "Mon, 27 Jul 2026 12:00:00 GMT",
            "author": {
                "name": "Wolfram",
                "screen_name": "WolframResearch"
            },
            "replying_to": None,
            "reposted_by": None,
            "media": {
                "photos": [
                    {"url": "https://pbs.twimg.com/media/test.jpg"}
                ]
            }
        },
        {
            "type": "status",
            "id": "4444444444444444444",
            "url": "https://x.com/WolframResearch/status/4444444444444444444",
            "text": "",
            "created_at": "Mon, 27 Jul 2026 13:00:00 GMT",
            "author": {
                "name": "Wolfram",
                "screen_name": "WolframResearch"
            },
            "replying_to": None,
            "reposted_by": None,
            "media": {}
        }
    ]
}


class TestTwitterFetcher:
    """TwitterFetcher 单元测试"""

    @pytest.mark.parametrize(
        "input_src,expected_username",
        [
            ("WolframResearch", "WolframResearch"),
            (" @WolframResearch ", "WolframResearch"),
            ("https://x.com/WolframResearch", "WolframResearch"),
            ("https://twitter.com/WolframResearch", "WolframResearch"),
            ("https://xcancel.com/WolframResearch/rss", "WolframResearch"),
            ("https://twitter.com/WolframResearch/status/12345678", "WolframResearch"),
            ("https://x.com", ""),
            ("", ""),
        ],
    )
    def test_extract_username(self, input_src, expected_username):
        """测试从各种形式 of src 中正确提取 X/Twitter 用户名"""
        source = ContentSource(type="twitter", src="WolframResearch")
        fetcher = TwitterFetcher(source)
        assert fetcher._extract_username(input_src) == expected_username

    def test_fetch_invalid_username(self):
        """测试输入的 src 无法解析出用户名时的错误处理"""
        source = ContentSource(type="twitter", src="https://x.com")
        fetcher = TwitterFetcher(source)
        result = fetcher.fetch()

        assert result.success is False
        assert "无法识别出有效的" in result.error

    @patch.object(TwitterFetcher, "_make_request")
    def test_fetch_all_fail(self, mock_make_request):
        """测试 FxTwitter API 失败时的错误处理"""
        mock_make_request.side_effect = Exception("API endpoint is completely down")

        source = ContentSource(type="twitter", src="WolframResearch")
        fetcher = TwitterFetcher(source)
        result = fetcher.fetch()

        assert result.success is False
        assert "API 抓取错误" in result.error

    @patch.object(TwitterFetcher, "_make_request")
    def test_fetch_filtering_and_parsing(self, mock_make_request):
        """测试推文解析、排除回复、排除转推、URL 转换、图片提取以及标题截断和兜底"""
        resp = MagicMock()
        resp.json.return_value = MOCK_FXTWITTER_JSON
        mock_make_request.return_value = resp

        # 默认不排除回复和转推
        source = ContentSource(
            type="twitter",
            src="WolframResearch",
            metadata={"exclude_replies": False, "exclude_rts": False}
        )
        fetcher = TwitterFetcher(source)
        result = fetcher.fetch()

        assert result.success is True
        # 全部4条推文都应该被获取
        assert len(result.articles) == 4

        # 1. 验证转推 (Repost/Retweet)
        rt_article = result.articles[0]
        assert rt_article.author == "@SomeoneElse"
        assert rt_article.url == "https://x.com/SomeoneElse/status/1111111111111111111"

        # 2. 验证回复 (Reply)
        reply_article = result.articles[1]
        assert reply_article.author == "@WolframResearch"
        assert "working on a fix" in reply_article.content

        # 3. 验证正常推文、图片以及标题截断逻辑 (正常标题不含换行符，且截断到最多 80 个字符 + ...)
        normal_article = result.articles[2]
        assert len(normal_article.title) == 83  # 80 chars + "..."
        assert normal_article.title.endswith("...")
        assert len(normal_article.images) == 1
        assert normal_article.images[0] == "https://pbs.twimg.com/media/test.jpg"
        assert '<img src="https://pbs.twimg.com/media/test.jpg"' in normal_article.content

        # 4. 验证空文字推文的标题兜底逻辑
        empty_text_article = result.articles[3]
        assert empty_text_article.title == "X 推文由 @WolframResearch 发布"

    @patch.object(TwitterFetcher, "_make_request")
    def test_exclude_replies_and_rts(self, mock_make_request):
        """测试开启 exclude_replies 和 exclude_rts 时的过滤效果"""
        resp = MagicMock()
        resp.json.return_value = MOCK_FXTWITTER_JSON
        mock_make_request.return_value = resp

        # 同时排除回复和转推
        source = ContentSource(
            type="twitter",
            src="WolframResearch",
            metadata={"exclude_replies": True, "exclude_rts": True}
        )
        fetcher = TwitterFetcher(source)
        result = fetcher.fetch()

        assert result.success is True
        # 原本4条，1条是转推 (reposted_by != None)，1条是回复 (replying_to != None)，
        # 排除后应该仅剩 2 条
        assert len(result.articles) == 2
        for article in result.articles:
            # 验证排除回复
            assert "working on a fix" not in article.content
            # 验证排除转推
            assert "Check out this awesome post about physics" not in article.content

    @patch.object(TwitterFetcher, "_make_request")
    def test_global_limit(self, mock_make_request):
        """测试 global_limit 限制抓取条数的功能"""
        resp = MagicMock()
        resp.json.return_value = MOCK_FXTWITTER_JSON
        mock_make_request.return_value = resp

        source = ContentSource(type="twitter", src="WolframResearch")
        # 限制最多获取 2 条
        fetcher = TwitterFetcher(source, global_limit=2)
        result = fetcher.fetch()

        assert result.success is True
        assert len(result.articles) == 2

    @patch.object(TwitterFetcher, "_make_request")
    def test_delete_keywords_filtering(self, mock_make_request):
        """测试 delete 过滤关键字功能"""
        resp = MagicMock()
        resp.json.return_value = MOCK_FXTWITTER_JSON
        mock_make_request.return_value = resp

        # 配置过滤含有 "physics" 的推文
        source = ContentSource(
            type="twitter",
            src="WolframResearch",
            delete="physics"
        )
        fetcher = TwitterFetcher(source)
        result = fetcher.fetch()

        assert result.success is True
        # 原本4条，排除了含 "physics" 的推文，剩下3条
        assert len(result.articles) == 3
        for article in result.articles:
            assert "physics" not in article.title

    @patch.object(TwitterFetcher, "_make_request")
    def test_metadata_limit_override(self, mock_make_request):
        """测试 metadata.limit 覆盖 global_limit"""
        resp = MagicMock()
        resp.json.return_value = MOCK_FXTWITTER_JSON
        mock_make_request.return_value = resp

        source = ContentSource(
            type="twitter",
            src="WolframResearch",
            metadata={"limit": 1}
        )
        fetcher = TwitterFetcher(source, global_limit=15)
        result = fetcher.fetch()

        assert result.success is True
        assert len(result.articles) == 1

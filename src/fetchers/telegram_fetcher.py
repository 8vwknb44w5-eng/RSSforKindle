from typing import List, Optional
import feedparser
import os

from src.config import ContentSource
from src.fetchers.base import BaseFetcher, FetchResult, Article
from src.utils.logger import get_logger
from src.utils.helpers import format_date

class TelegramFetcher(BaseFetcher):
    """
    Telegram 频道抓取器 (基于 RSSHub)
    支持直接输入频道 ID，通过 RSSHub 转换为 RSS 订阅
    """

    type_name = "telegram"
    src_placeholder = "Telegram 频道 ID, 例如: durov"
    
    config_schema = {
        "metadata.rsshub_host": {
            "type": "text",
            "label": "RSSHub 实例地址",
            "placeholder": "rsshub.rssforever.com",
            "hint": "默认使用 rsshub.rssforever.com"
        },
        "metadata.limit": {
            "type": "number",
            "label": "抓取条目数",
            "placeholder": "15"
        },
        "metadata.route_params": {
            "type": "text",
            "label": "额外路由参数",
            "placeholder": "showEmoji=1",
            "hint": "RSSHub Telegram 路由的额外参数"
        }
    }

    def fetch(self) -> FetchResult:
        """
        执行 Telegram 抓取
        """
        result = FetchResult(source=self.source, articles=[])
        
        try:
            # 1. 构造 RSSHub URL
            metadata = self.source.metadata or {}
            host = metadata.get("rsshub_host") or "rsshub.rssforever.com"
            # 移除可能存在的前缀/后缀斜杠
            host = host.strip().rstrip('/')
            if not host.startswith(('http://', 'https://')):
                host = 'https://' + host

            channel_id = self.source.src.strip()
            # 如果用户输入了完整的 URL 或带 @ 的 ID，进行简单处理
            channel_id = channel_id.split('/')[-1].replace('@', '')
            
            rss_url = f"{host}/telegram/channel/{channel_id}"
            
            # 添加额外参数
            route_params = metadata.get("route_params")
            if route_params:
                rss_url += f"?{route_params}"

            self.logger.info(f"Fetching Telegram channel via RSSHub: {rss_url}")

            # 2. 发送请求并解析
            # 使用基类的 _make_request 以确保一致的超时和请求头
            response = self._make_request(rss_url)
            feed = feedparser.parse(response.text)

            if not feed.entries:
                if feed.bozo:
                    raise Exception(f"RSS parsing error: {feed.bozo_exception}")
                result.success = True # 可能只是频道暂时没发消息
                return result

            # 设置源标题（频道名称）
            result.source_title = feed.feed.get("title", f"Telegram: {channel_id}")

            # 3. 限制条目数量
            limit = int(metadata.get("limit") or self.global_limit)
            entries = feed.entries[:limit]

            # 4. 解析条目
            for entry in entries:
                try:
                    article = self._parse_entry(entry)
                    if article and not self._should_delete(article.title):
                        result.articles.append(article)
                except Exception as e:
                    self.logger.error(f"Failed to parse Telegram entry: {e}")
                    result.add_error(f"Entry parsing failed: {e}")

            return result

        except Exception as e:
            self.logger.error(f"Telegram fetch failed: {e}")
            result.success = False
            result.error = str(e)
            return result

    def _parse_entry(self, entry: dict) -> Optional[Article]:
        """
        解析单个 Telegram 消息条目
        """
        # Telegram 消息通常没有独立的标题，RSSHub 会截取内容作为标题
        title = entry.get("title", "Telegram Message")
        link = entry.get("link", "")
        author = entry.get("author", "")
        published = format_date(entry.get("published", ""))

        # 提取内容：Telegram 的 RSSHub 输出通常在 summary 或 description 中
        content = ""
        if "content" in entry and len(entry.content) > 0:
            content = entry.content[0].get("value", "")
        else:
            content = entry.get("summary") or entry.get("description", "")

        if not content:
            return None

        # 提取图片：Telegram 消息中的图片通常直接嵌入在 HTML 中
        # 使用基类提供的 _extract_images
        images = self._extract_images(content, base_url=link)

        return Article(
            title=title,
            content=content,
            url=link,
            author=author,
            published_date=published,
            images=images,
            metadata={
                "source_type": "telegram",
                "original_link": entry.get("link")
            }
        )

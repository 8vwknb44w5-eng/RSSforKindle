"""
目录生成器模块
负责生成 EPUB 的目录结构
"""

from typing import List, Tuple, Optional, Union
from ebooklib import epub

from src.config import ContentSource
from src.fetchers.base import Article
from src.utils.logger import get_logger


# TOC 条目类型：可以是两级结构 (Section, [Link]) 或扁平 Link
TOCEntry = Union[Tuple[epub.Section, List[epub.Link]], epub.Link]


class TOCGenerator:
    """目录生成器"""

    def __init__(self):
        """初始化目录生成器"""
        self.logger = get_logger()

    def generate(
        self,
        sections: List[Tuple[ContentSource, List[Article], Optional[str]]]
    ) -> List[TOCEntry]:
        """
        生成目录结构

        Args:
            sections: 章节列表 (ContentSource, Articles, source_title)
                      source_title 为内容源的显示名称（如 RSS feed 标题）

        Returns:
            List[TOCEntry]: 目录结构
            - 所有 fetcher 均使用两级结构 (Section, [Link, ...])
        """
        toc: List[TOCEntry] = []
        chapter_counter = 0
        divider_counter = 0

        for source, articles, source_title in sections:
            if not articles:
                continue

            section_title = self._get_source_title(source, articles, source_title)

            # 两级结构（章节 → 文章列表）
            section_uid = f"section_{divider_counter}"
            section_href = f"divider_{divider_counter}.xhtml"
            section_link = epub.Link(section_href, section_title, section_uid)

            links = []
            for article in articles:
                chapter_filename = f"chapter_{chapter_counter}.xhtml"
                chapter_id = f"chapter_{chapter_counter}"

                link = epub.Link(chapter_filename, article.title, chapter_id)
                links.append(link)
                chapter_counter += 1

            toc.append((section_link, links))
            divider_counter += 1

        self.logger.info(f"Generated TOC with {len(toc)} entries")
        return toc

    def _get_source_title(
        self,
        source: ContentSource,
        articles: List[Article],
        source_title: Optional[str] = None
    ) -> str:
        """
        获取内容源的显示名称

        优先级：
        1. 用户自定义 title（config 中的 title 字段）
        2. 内容源特定名称：
           - rss: feed 标题（从 feedparser 提取）
           - web: 页面标题（第一篇文章的标题）
           - mail: namespace（source.src）
           - trending: 关键词/主题（source.src）

        Args:
            source: 内容源配置
            articles: 文章列表
            source_title: 内容源显示名称（如 RSS feed 标题）

        Returns:
            str: 章节显示名称
        """
        # 1. 优先使用用户自定义标题
        if source.title:
            return source.title

        # 2. 动态委派给对应的 fetcher class 来获取其默认章节名称
        from src.fetchers import get_fetcher_class
        fetcher_class = get_fetcher_class(source.type)
        if fetcher_class and hasattr(fetcher_class, "get_default_source_title"):
            return fetcher_class.get_default_source_title(source, articles, source_title)

        return source.src

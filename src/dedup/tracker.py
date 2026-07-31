"""
去重追踪器模块
负责记录已抓取的内容，避免重复抓取
"""

import os
from typing import Set
from src.utils.logger import get_logger
from src.utils.helpers import generate_content_id


class DedupTracker:
    """去重追踪器"""

    MAX_RECORDS = 500000  # 记录数上限，超过后自动清理旧记录

    def __init__(self, data_file: str = "data/fetched_urls.txt"):
        """
        初始化去重追踪器

        Args:
            data_file: 数据存储文件路径
        """
        self.data_file = data_file
        self.logger = get_logger()
        self.fetched_ids: Set[str] = set()
        self.new_ids: Set[str] = set()

        # 加载已有记录
        self._load()

    def _load(self):
        """加载已抓取的内容 ID"""
        if not os.path.exists(self.data_file):
            self.logger.info(f"No existing dedup file found at {self.data_file}")
            return

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    content_id = line.strip()
                    if content_id:
                        self.fetched_ids.add(content_id)

            self.logger.info(f"Loaded {len(self.fetched_ids)} fetched content IDs")

        except Exception as e:
            self.logger.error(f"Failed to load dedup file: {e}")

    def is_fetched(self, url: str, title: str = None, published_date: str = None) -> bool:
        """
        检查内容是否已抓取。

        - 阶段一（仅传 URL）：用 URL-only 哈希判断，同 URL 视为同文章，避免重复进阶段二。
        - 阶段三 / 非两阶段（传了 title 或 published_date）：用完整内容哈希判断，
          避免 Weather/Trending 等共用 URL、按日刷新的场景被误判为已抓取。
        """
        # 阶段一：仅 URL 去重
        if title is None and published_date is None:
            url_hash = generate_content_id(url, None, None)
            return url_hash in self.fetched_ids

        # 阶段三 / 非两阶段：完整内容哈希
        content_id = generate_content_id(url, title, published_date)
        if published_date:
            self.logger.debug(f"Dedup check [{published_date}]: url={url}, hash={content_id}")
        return content_id in self.fetched_ids

    def mark_as_fetched(self, url: str, title: str = None, published_date: str = None):
        """
        标记内容为已抓取。

        同时持久化：
        - URL-only 哈希：供阶段一仅凭 URL 跳过已抓文章
        - 完整内容哈希：供阶段三 / Weather·Trending 等带标题或日期的去重
        """
        url_hash = generate_content_id(url, None, None)
        content_id = generate_content_id(url, title, published_date)

        for hid in (url_hash, content_id):
            if hid not in self.fetched_ids:
                self.fetched_ids.add(hid)
                self.new_ids.add(hid)

        if published_date:
            self.logger.info(
                f"Marked as fetched [{published_date}]: url={url}, hash={content_id}"
            )
        else:
            self.logger.debug(f"Marked as fetched: {content_id}")

    def save(self):
        """保存新的抓取记录"""
        if not self.new_ids:
            self.logger.info("No new content to save")
            return

        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

            # 追加新记录
            with open(self.data_file, 'a', encoding='utf-8') as f:
                for content_id in self.new_ids:
                    f.write(f"{content_id}\n")

            self.logger.info(f"Saved {len(self.new_ids)} new content IDs")

            # 超过上限时自动清理旧记录
            self._cleanup_if_needed()

        except Exception as e:
            self.logger.error(f"Failed to save dedup file: {e}")

    def _cleanup_if_needed(self):
        """超过 MAX_RECORDS 条时，只保留最新的记录（文件末尾）"""
        try:
            if not os.path.exists(self.data_file):
                return

            with open(self.data_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

            if len(lines) <= self.MAX_RECORDS:
                return

            # 保留最新的记录（文件末尾的 MAX_RECORDS 条）
            kept = lines[-self.MAX_RECORDS:]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                for line in kept:
                    f.write(f"{line}\n")

            removed = len(lines) - len(kept)
            # 同步内存中的 set，避免后续判断与文件不一致
            self.fetched_ids = set(kept)
            self.logger.info(f"Dedup cleanup: removed {removed} old records, kept {len(kept)}")

        except Exception as e:
            self.logger.error(f"Failed to cleanup dedup file: {e}")

    def get_stats(self) -> dict:
        """
        获取统计信息

        Returns:
            dict: 统计信息
        """
        return {
            "total_fetched": len(self.fetched_ids),
            "new_fetched": len(self.new_ids)
        }

    def clear_new_ids(self):
        """清除新记录标记"""
        self.new_ids.clear()

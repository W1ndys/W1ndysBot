"""
QFNUMonitor 数据管理器
用于存储已通知的公告信息，避免重复通知
"""

import sqlite3
import os
from typing import Optional
from datetime import datetime
from .. import MODULE_NAME, DATA_DIR
from logger import logger


class DataManager:
    """公告数据管理器"""

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        db_path = os.path.join(DATA_DIR, f"{MODULE_NAME}.db")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建数据表"""
        # 已通知公告表
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS notified_announcements (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                date TEXT,
                summary TEXT,
                notified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        # 摘要缓存表（用于缓存已生成的摘要，避免重复调用 API）
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS summary_cache (
                url TEXT PRIMARY KEY,
                title TEXT,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        self.conn.commit()

    def is_notified(self, announcement_id: str) -> bool:
        """
        检查公告是否已通知

        Args:
            announcement_id: 公告ID

        Returns:
            是否已通知
        """
        try:
            self.cursor.execute(
                "SELECT 1 FROM notified_announcements WHERE id = ?", (announcement_id,)
            )
            return self.cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 检查公告是否已通知失败: {e}")
            return False

    def add_notified(
        self,
        announcement_id: str,
        title: str,
        url: str,
        date: str = "",
        summary: str = "",
    ) -> bool:
        """
        添加已通知公告记录

        Args:
            announcement_id: 公告ID
            title: 公告标题
            url: 公告链接
            date: 发布日期
            summary: 公告摘要

        Returns:
            是否添加成功
        """
        try:
            self.cursor.execute(
                """INSERT OR REPLACE INTO notified_announcements
                   (id, title, url, date, summary, notified_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (announcement_id, title, url, date, summary, datetime.now()),
            )
            self.conn.commit()
            logger.info(f"[{MODULE_NAME}] 添加已通知公告: {title}")
            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 添加已通知公告失败: {e}")
            return False

    def get_cached_summary(self, url: str) -> Optional[str]:
        """
        获取缓存的摘要

        Args:
            url: 页面URL

        Returns:
            缓存的摘要，不存在返回 None
        """
        try:
            self.cursor.execute(
                "SELECT summary FROM summary_cache WHERE url = ?", (url,)
            )
            result = self.cursor.fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 获取缓存摘要失败: {e}")
            return None

    def cache_summary(self, url: str, title: str, summary: str) -> bool:
        """
        缓存摘要

        Args:
            url: 页面URL
            title: 页面标题
            summary: 摘要内容

        Returns:
            是否缓存成功
        """
        try:
            self.cursor.execute(
                """INSERT OR REPLACE INTO summary_cache
                   (url, title, summary, created_at)
                   VALUES (?, ?, ?, ?)""",
                (url, title, summary, datetime.now()),
            )
            self.conn.commit()
            logger.info(f"[{MODULE_NAME}] 缓存摘要: {url}")
            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 缓存摘要失败: {e}")
            return False

    def get_notified_count(self) -> int:
        """获取已通知公告数量"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM notified_announcements")
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 获取已通知公告数量失败: {e}")
            return 0

    def clean_old_records(self, days: int = 90):
        """
        清理过期记录

        Args:
            days: 保留天数
        """
        try:
            self.cursor.execute(
                """DELETE FROM notified_announcements
                   WHERE notified_at < datetime('now', ?)""",
                (f"-{days} days",),
            )
            self.cursor.execute(
                """DELETE FROM summary_cache
                   WHERE created_at < datetime('now', ?)""",
                (f"-{days} days",),
            )
            self.conn.commit()
            logger.info(f"[{MODULE_NAME}] 清理了 {days} 天前的旧记录")
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 清理旧记录失败: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """关闭数据库连接"""
        try:
            self.conn.close()
        except Exception:
            pass

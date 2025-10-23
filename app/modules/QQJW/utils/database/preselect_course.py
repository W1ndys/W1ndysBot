import os
import sqlite3
from datetime import datetime, timedelta, timezone
from ... import MODULE_NAME
from logger import logger
import json


class PreselectCourseDatabase:
    def __init__(self):
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"data.db")
        self.table_name = "preselect_course"
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._init_table()

    def _init_table(self):
        """
        初始化预选课缓存表，如果不存在则创建
        表结构：
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        search_keyword TEXT NOT NULL, # 搜索关键词
        result_data   TEXT NOT NULL, # 查询结果（JSON格式）
        query_count   INTEGER DEFAULT 1, # 查询次数
        created_at    TEXT, # 创建时间
        updated_at    TEXT, # 更新时间
        last_accessed TEXT # 最后访问时间
        """
        try:
            self.cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS preselect_cache (
                        id             INTEGER PRIMARY KEY AUTOINCREMENT,
                        search_keyword TEXT NOT NULL,
                        result_data    TEXT NOT NULL,
                        query_count    INTEGER DEFAULT 1,
                        created_at     TEXT,
                        updated_at     TEXT,
                        last_accessed  TEXT
                    );
                """
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]初始化预选课缓存表失败: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def _get_beijing_time(self):
        """获取北京时间（东八区）"""
        beijing_tz = timezone(timedelta(hours=8))
        return datetime.now(beijing_tz).strftime("%Y-%m-%d %H:%M:%S")

    def get_cached_result(self, search_keyword, cache_duration_seconds=900):
        """
        获取缓存的查询结果

        Args:
            search_keyword (str): 搜索关键词
            cache_duration_seconds (int): 缓存有效期（秒）

        Returns:
            tuple: (is_valid, result_data) 是否有效和结果数据
        """
        try:
            # 使用北京时间保持一致性
            beijing_tz = timezone(timedelta(hours=8))
            current_time = datetime.now(beijing_tz)
            cache_expire_time = current_time - timedelta(seconds=cache_duration_seconds)

            # 转换为字符串格式，确保与数据库存储格式一致
            current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            cache_expire_time_str = cache_expire_time.strftime("%Y-%m-%d %H:%M:%S")

            # 添加详细调试日志
            logger.info(f"[{MODULE_NAME}]查询缓存: {search_keyword}")
            logger.info(
                f"[{MODULE_NAME}]当前时间: {current_time_str}, 过期阈值: {cache_expire_time_str}, 缓存有效期: {cache_duration_seconds}秒"
            )

            self.cursor.execute(
                """
                    SELECT result_data, created_at, updated_at, last_accessed, query_count 
                    FROM preselect_cache 
                    WHERE search_keyword = ? AND updated_at > ?
                """,
                (search_keyword, cache_expire_time_str),
            )

            result = self.cursor.fetchone()

            # 添加调试日志
            if result:
                result_data, created_at, updated_at, last_accessed, query_count = result
                logger.info(
                    f"[{MODULE_NAME}]找到有效缓存记录: {search_keyword}, 创建时间: {created_at}, 更新时间: {updated_at}"
                )
            else:
                # 查询是否存在该关键词的记录（不考虑时间）
                self.cursor.execute(
                    "SELECT created_at, updated_at FROM preselect_cache WHERE search_keyword = ?",
                    (search_keyword,),
                )
                existing_record = self.cursor.fetchone()
                if existing_record:
                    logger.warning(
                        f"[{MODULE_NAME}]找到过期缓存记录: {search_keyword}, 创建时间: {existing_record[0]}, 更新时间: {existing_record[1]}, 过期阈值: {cache_expire_time_str}"
                    )
                else:
                    logger.info(f"[{MODULE_NAME}]未找到任何缓存记录: {search_keyword}")

            if result:
                result_data, created_at, updated_at, last_accessed, query_count = result

                # 更新最后访问时间和查询次数
                self.cursor.execute(
                    """
                        UPDATE preselect_cache 
                        SET last_accessed = ?, query_count = query_count + 1 
                        WHERE search_keyword = ?
                    """,
                    (current_time_str, search_keyword),
                )
                self.conn.commit()

                logger.info(
                    f"[{MODULE_NAME}]命中缓存: {search_keyword}, 查询次数: {query_count + 1}"
                )
                return True, json.loads(result_data)
            else:
                return False, None

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]获取缓存结果失败: {e}")
            return False, None

    def cache_result(self, search_keyword, result_data):
        """
        缓存查询结果

        Args:
            search_keyword (str): 搜索关键词
            result_data (list): 查询结果数据
        """
        try:
            current_time = self._get_beijing_time()

            # 添加调试日志
            logger.info(
                f"[{MODULE_NAME}]准备缓存结果: {search_keyword}, 时间: {current_time}"
            )

            # 检查是否已存在该关键词的缓存
            self.cursor.execute(
                "SELECT id FROM preselect_cache WHERE search_keyword = ?",
                (search_keyword,),
            )

            existing_record = self.cursor.fetchone()

            if existing_record:
                # 更新现有记录
                self.cursor.execute(
                    """
                        UPDATE preselect_cache 
                        SET result_data = ?, updated_at = ?, last_accessed = ?
                        WHERE search_keyword = ?
                    """,
                    (
                        json.dumps(result_data),
                        current_time,
                        current_time,
                        search_keyword,
                    ),
                )
                logger.info(f"[{MODULE_NAME}]更新缓存: {search_keyword}")
            else:
                # 插入新记录
                self.cursor.execute(
                    """
                        INSERT INTO preselect_cache 
                        (search_keyword, result_data, created_at, updated_at, last_accessed)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        search_keyword,
                        json.dumps(result_data),
                        current_time,
                        current_time,
                        current_time,
                    ),
                )
                logger.info(f"[{MODULE_NAME}]新增缓存: {search_keyword}")

            self.conn.commit()

            # 验证缓存是否成功写入
            self.cursor.execute(
                "SELECT created_at FROM preselect_cache WHERE search_keyword = ?",
                (search_keyword,),
            )
            verify_result = self.cursor.fetchone()
            if verify_result:
                logger.info(
                    f"[{MODULE_NAME}]缓存写入验证成功: {search_keyword}, 存储时间: {verify_result[0]}"
                )
            else:
                logger.error(f"[{MODULE_NAME}]缓存写入验证失败: {search_keyword}")

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]缓存结果失败: {e}")
            self.conn.rollback()  # 添加回滚操作

    def clean_expired_cache(self, cache_duration_seconds=86400):
        """
        清理过期的缓存数据

        Args:
            cache_duration_seconds (int): 缓存有效期（秒）
        """
        try:
            # 使用北京时间保持一致性
            beijing_tz = timezone(timedelta(hours=8))
            current_time = datetime.now(beijing_tz)
            expire_time = current_time - timedelta(seconds=cache_duration_seconds)
            expire_time_str = expire_time.strftime("%Y-%m-%d %H:%M:%S")

            # 先查询要删除的记录数量和详情（用于调试）
            self.cursor.execute(
                "SELECT search_keyword, updated_at FROM preselect_cache WHERE updated_at < ?",
                (expire_time_str,),
            )
            to_delete = self.cursor.fetchall()

            if to_delete:
                logger.info(
                    f"[{MODULE_NAME}]准备清理过期缓存: {len(to_delete)} 条记录，过期阈值: {expire_time_str}"
                )
                for keyword, update_time in to_delete:
                    logger.info(
                        f"[{MODULE_NAME}]清理过期缓存项: {keyword}, 更新时间: {update_time}"
                    )

            # 使用 updated_at 字段来判断是否过期（与 get_cached_result 保持一致）
            self.cursor.execute(
                "DELETE FROM preselect_cache WHERE updated_at < ?",
                (expire_time_str,),
            )

            deleted_count = self.cursor.rowcount
            self.conn.commit()

            if deleted_count > 0:
                logger.info(f"[{MODULE_NAME}]成功清理过期缓存: {deleted_count} 条记录")
            else:
                logger.info(f"[{MODULE_NAME}]没有过期缓存需要清理")

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]清理过期缓存失败: {e}")

    def get_cache_time(self, search_keyword):
        """
        获取缓存数据的创建时间

        Args:
            search_keyword (str): 搜索关键词

        Returns:
            str or None: 缓存时间字符串，如果不存在则返回None
        """
        try:
            self.cursor.execute(
                "SELECT created_at FROM preselect_cache WHERE search_keyword = ?",
                (search_keyword,),
            )
            result = self.cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]获取缓存时间失败: {e}")
            return None

    def get_cache_statistics(self):
        """
        获取缓存统计信息

        Returns:
            dict: 缓存统计信息
        """
        try:
            # 总缓存数量
            self.cursor.execute("SELECT COUNT(*) FROM preselect_cache")
            total_count = self.cursor.fetchone()[0]

            # 今日新增缓存数量
            today = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute(
                "SELECT COUNT(*) FROM preselect_cache WHERE DATE(created_at) = ?",
                (today,),
            )
            today_count = self.cursor.fetchone()[0]

            # 最热门的搜索关键词（按查询次数排序）
            self.cursor.execute(
                """
                    SELECT search_keyword, query_count 
                    FROM preselect_cache 
                    ORDER BY query_count DESC 
                    LIMIT 5
                """
            )
            top_keywords = self.cursor.fetchall()

            return {
                "total_count": total_count,
                "today_count": today_count,
                "top_keywords": top_keywords,
            }

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]获取缓存统计信息失败: {e}")
            return {}

    def debug_cache_status(self, search_keyword):
        """
        调试缓存状态的辅助方法
        """
        try:
            # 查询所有相关记录
            self.cursor.execute(
                "SELECT * FROM preselect_cache WHERE search_keyword = ?",
                (search_keyword,),
            )
            all_records = self.cursor.fetchall()

            logger.info(f"[{MODULE_NAME}]调试缓存状态 - 关键词: {search_keyword}")
            logger.info(f"[{MODULE_NAME}]找到 {len(all_records)} 条记录")

            for record in all_records:
                logger.info(f"[{MODULE_NAME}]记录详情: {record}")

            # 查询表结构
            self.cursor.execute("PRAGMA table_info(preselect_cache)")
            table_info = self.cursor.fetchall()
            logger.info(f"[{MODULE_NAME}]表结构: {table_info}")

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]调试缓存状态失败: {e}")

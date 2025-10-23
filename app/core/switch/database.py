"""
开关系统数据库操作模块
负责数据库初始化、连接管理和基础数据库操作
"""

import sqlite3
import threading
import os
from logger import logger
from .config import DATABASE_PATH


class SwitchDatabase:
    """开关系统数据库管理类"""

    def __init__(self):
        # 线程锁，确保数据库操作线程安全
        self.db_lock = threading.Lock()
        self.init_database()

    def init_database(self):
        """
        初始化数据库，创建必要的表
        """
        with self.db_lock:
            try:
                # 确保Core目录存在
                os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()

                # 创建模块开关表
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS module_switches (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        module_name TEXT NOT NULL,
                        switch_type TEXT NOT NULL CHECK (switch_type IN ('group', 'private')),
                        group_id TEXT,
                        status INTEGER NOT NULL CHECK (status IN (0, 1)),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE (module_name, switch_type, group_id)
                    )
                """
                )

                # 创建索引以优化查询性能
                self._create_indexes(cursor)

                conn.commit()
                conn.close()
                logger.info("数据库初始化完成")
            except Exception as e:
                logger.error(f"数据库初始化失败: {e}")

    def _create_indexes(self, cursor):
        """创建数据库索引"""
        indexes = [
            ("idx_module_group", "module_switches", "module_name, group_id"),
            ("idx_module_type", "module_switches", "module_name, switch_type"),
            ("idx_group_id", "module_switches", "group_id"),
        ]

        for index_name, table, columns in indexes:
            cursor.execute(
                f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({columns})"
            )

    def get_connection(self):
        """
        获取数据库连接
        """
        return sqlite3.connect(DATABASE_PATH)

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """
        执行查询操作
        """
        with self.db_lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                result = None
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()

                conn.close()
                return result
            except Exception as e:
                logger.error(f"数据库查询失败: {e}")
                return None

    def execute_update(self, query, params=None):
        """
        执行更新操作（INSERT, UPDATE, DELETE）
        """
        with self.db_lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()

                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                affected_rows = cursor.rowcount
                conn.commit()
                conn.close()
                return affected_rows
            except Exception as e:
                logger.error(f"数据库更新失败: {e}")
                return 0

    def execute_batch(self, operations):
        """
        批量执行数据库操作
        operations: 操作列表，每个操作为 (query, params) 元组
        """
        with self.db_lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()

                for query, params in operations:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)

                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.error(f"批量数据库操作失败: {e}")
                return False


# 全局数据库实例
db = SwitchDatabase()

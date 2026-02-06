"""
数据库管理模块 - 王者荣耀小马糕

功能特性：
1. 自动判断数据库是否存在并创建
2. 基于表结构定义自动检测差异并迁移（无需手动管理版本号）
3. 支持 with 语句上下文管理
4. 异常时自动回滚，正常退出时自动提交
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from .. import MODULE_NAME


class DataManager:
    """
    数据库管理类

    支持上下文管理器协议，自动处理连接的创建、提交和关闭。
    基于 TABLES 定义自动检测并迁移数据库结构。
    """

    # ==================== 表结构定义 ====================
    TABLES = {
        "xmg_records": {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "group_id": "TEXT NOT NULL",           # 群号
            "user_id": "TEXT NOT NULL",            # 发送者QQ号
            "nickname": "TEXT",                    # 发送者昵称
            "full_message": "TEXT NOT NULL",       # 完整的小马糕消息
            "price": "INTEGER NOT NULL",           # 小马糕价格
            "store_date": "TEXT NOT NULL",         # 存储日期(YYYY-MM-DD)
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        }
    }

    # 表约束定义
    TABLE_CONSTRAINTS = {
        "xmg_records": [
            "UNIQUE(group_id, full_message, store_date)"  # 相同消息每天只保留一条
        ]
    }

    def __init__(self):
        """初始化数据库连接"""
        self.data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(self.data_dir, exist_ok=True)

        self.db_path = os.path.join(self.data_dir, f"{MODULE_NAME}.db")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self._auto_migrate()

    def _auto_migrate(self):
        """自动检测并迁移数据库结构"""
        for table_name, columns in self.TABLES.items():
            if not self._table_exists(table_name):
                self._create_table(table_name, columns)
            else:
                self._migrate_table(table_name, columns)
        self.conn.commit()

    def _table_exists(self, table: str) -> bool:
        """检查表是否存在"""
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
        )
        return self.cursor.fetchone() is not None

    def _get_existing_columns(self, table: str) -> Dict[str, str]:
        """获取表的现有列信息"""
        self.cursor.execute(f"PRAGMA table_info({table})")
        return {row[1]: row[2] for row in self.cursor.fetchall()}

    def _create_table(self, table_name: str, columns: Dict[str, str]):
        """创建新表"""
        cols_def = ", ".join(f"{col} {definition}" for col, definition in columns.items())
        constraints = self.TABLE_CONSTRAINTS.get(table_name, [])
        if constraints:
            cols_def += ", " + ", ".join(constraints)

        self.cursor.execute(f"CREATE TABLE {table_name} ({cols_def})")

    def _migrate_table(self, table_name: str, expected_columns: Dict[str, str]):
        """迁移表结构：添加缺失的列"""
        existing_columns = self._get_existing_columns(table_name)

        for col_name, col_def in expected_columns.items():
            if col_name not in existing_columns:
                self.cursor.execute(
                    f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}"
                )

    # ==================== 上下文管理器 ====================

    def __enter__(self):
        """进入上下文时返回自身"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文：异常时回滚，正常时提交，最后关闭连接"""
        try:
            if exc_type is not None:
                self.conn.rollback()
            else:
                self.conn.commit()
        finally:
            self.conn.close()
        return False

    # ==================== 数据操作方法 ====================

    def add_xmg(self, group_id: str, user_id: str, nickname: str, full_message: str, price: int) -> bool:
        """
        添加小马糕记录，相同消息不重复存储（通过数据库UNIQUE约束实现）

        Args:
            group_id: 群号
            user_id: 发送者QQ号
            nickname: 发送者昵称
            full_message: 完整的小马糕消息
            price: 小马糕价格

        Returns:
            bool: 是否成功添加（重复消息会返回False）
        """
        try:
            store_date = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute(
                """INSERT INTO xmg_records (group_id, user_id, nickname, full_message, price, store_date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (group_id, user_id, nickname, full_message, price, store_date),
            )
            return True
        except sqlite3.IntegrityError:
            # 重复消息，忽略
            return False
        except sqlite3.Error:
            return False

    def get_highest_price_xmg(self, group_id: str) -> Optional[Dict[str, Any]]:
        """
        获取当天该群组价格最高的小马糕

        Args:
            group_id: 群号

        Returns:
            最高价格的小马糕记录字典，如果没有则返回None
        """
        store_date = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            """SELECT id, group_id, user_id, nickname, full_message, price, store_date, created_at
               FROM xmg_records 
               WHERE group_id = ? AND store_date = ? 
               ORDER BY price DESC, created_at ASC 
               LIMIT 1""",
            (group_id, store_date),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_global_highest_price_xmg(self) -> Optional[Dict[str, Any]]:
        """
        获取当天全库价格最高的小马糕（所有群）

        Returns:
            最高价格的小马糕记录字典，如果没有则返回None
        """
        store_date = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            """SELECT id, group_id, user_id, nickname, full_message, price, store_date, created_at
               FROM xmg_records 
               WHERE store_date = ? 
               ORDER BY price DESC, created_at ASC 
               LIMIT 1""",
            (store_date,),
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def delete_by_xmg_code(self, group_id: str, xmg_code: str) -> bool:
        """
        根据小马糕代码删除记录（同一天内）

        Args:
            group_id: 群号
            xmg_code: 小马糕代码，如"东方不败1JGNNX"

        Returns:
            bool: 是否成功删除
        """
        store_date = datetime.now().strftime("%Y-%m-%d")
        # 使用LIKE匹配消息中的小马糕代码
        pattern = f"%【{xmg_code}】%"
        self.cursor.execute(
            """DELETE FROM xmg_records 
               WHERE group_id = ? AND store_date = ? AND full_message LIKE ?""",
            (group_id, store_date, pattern),
        )
        return self.cursor.rowcount > 0

    def delete_expired_records(self) -> int:
        """
        删除过期的记录（非当天的）

        Returns:
            int: 删除的记录数量
        """
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            "DELETE FROM xmg_records WHERE store_date != ?",
            (today,)
        )
        return self.cursor.rowcount

    def get_all_by_group(self, group_id: str) -> List[Dict[str, Any]]:
        """
        获取群组当天的所有小马糕记录

        Args:
            group_id: 群号

        Returns:
            小马糕记录列表
        """
        store_date = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute(
            """SELECT id, group_id, user_id, nickname, full_message, price, created_at 
               FROM xmg_records 
               WHERE group_id = ? AND store_date = ?
               ORDER BY price DESC""",
            (group_id, store_date),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def clear_group_data(self, group_id: str) -> int:
        """
        清空群组的所有数据，返回删除的记录数

        Args:
            group_id: 群号

        Returns:
            int: 删除的记录数
        """
        self.cursor.execute(
            "DELETE FROM xmg_records WHERE group_id = ?", (group_id,)
        )
        return self.cursor.rowcount

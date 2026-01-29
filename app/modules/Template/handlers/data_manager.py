"""
数据库管理模块模板

功能特性：
1. 自动判断数据库是否存在并创建
2. 基于表结构定义自动检测差异并迁移（无需手动管理版本号）
3. 支持 with 语句上下文管理
4. 异常时自动回滚，正常退出时自动提交

使用示例：
    with DataManager() as dm:
        dm.add_data(group_id="123", name="test", content="hello")
        data = dm.get_data(group_id="123", name="test")

修改表结构：
    只需修改 TABLES 字典中的表定义，重启后自动迁移
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any
from .. import MODULE_NAME


class DataManager:
    """
    数据库管理类

    支持上下文管理器协议，自动处理连接的创建、提交和关闭。
    基于 TABLES 定义自动检测并迁移数据库结构。
    """

    # ==================== 表结构定义 ====================
    # 修改此处即可自动迁移，支持：添加新表、添加新列
    # 格式: {"表名": {"列名": "列定义", ...}, ...}
    TABLES = {
        "template_data": {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "group_id": "TEXT NOT NULL",
            "name": "TEXT NOT NULL",
            "content": "TEXT NOT NULL",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            # 添加新列只需在此处添加，如:
            # "new_field": "TEXT DEFAULT ''",
        },
        # 添加新表只需在此处添加，如:
        # "another_table": {
        #     "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        #     "data": "TEXT",
        # },
    }

    # 表约束定义（可选）
    # 格式: {"表名": ["约束1", "约束2", ...], ...}
    TABLE_CONSTRAINTS = {
        "template_data": [
            "UNIQUE(group_id, name)",
        ],
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

    # ==================== 数据操作方法（示例） ====================

    def add_data(self, group_id: str, name: str, content: str) -> bool:
        """添加或更新数据"""
        try:
            self.cursor.execute(
                """INSERT OR REPLACE INTO template_data (group_id, name, content)
                   VALUES (?, ?, ?)""",
                (group_id, name, content),
            )
            return True
        except sqlite3.Error:
            return False

    def get_data(self, group_id: str, name: str) -> Optional[str]:
        """获取数据"""
        self.cursor.execute(
            "SELECT content FROM template_data WHERE group_id = ? AND name = ?",
            (group_id, name),
        )
        row = self.cursor.fetchone()
        return row["content"] if row else None

    def delete_data(self, group_id: str, name: str) -> bool:
        """删除数据"""
        self.cursor.execute(
            "DELETE FROM template_data WHERE group_id = ? AND name = ?",
            (group_id, name),
        )
        return self.cursor.rowcount > 0

    def get_all_by_group(self, group_id: str) -> List[Dict[str, Any]]:
        """获取群组的所有数据"""
        self.cursor.execute(
            "SELECT name, content, created_at FROM template_data WHERE group_id = ?",
            (group_id,),
        )
        return [dict(row) for row in self.cursor.fetchall()]

    def clear_group_data(self, group_id: str) -> int:
        """清空群组的所有数据，返回删除的记录数"""
        self.cursor.execute(
            "DELETE FROM template_data WHERE group_id = ?", (group_id,)
        )
        return self.cursor.rowcount

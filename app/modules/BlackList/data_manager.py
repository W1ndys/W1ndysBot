import sqlite3
import os
from datetime import datetime
from . import DATA_DIR


class BlackListDataManager:
    def __init__(self):
        self.db_path = os.path.join(DATA_DIR, "blacklist.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """
        创建黑名单表
        列：
            id: 自增ID
            group_id: 群组ID
            user_id: 用户ID
            created_at: 创建时间
        :raises: Exception 创建失败时抛出异常
        """
        try:
            self.cursor.execute(
                """CREATE TABLE IF NOT EXISTS blacklist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT,
                user_id TEXT,
                created_at TEXT
                )"""
            )
            self.conn.commit()
            self._close()
        except sqlite3.Error as e:
            raise Exception(f"创建黑名单表失败: {str(e)}")

    def _close(self):
        """
        关闭数据库连接
        """
        self.conn.close()

    def add_blacklist(self, group_id: str, user_id: str) -> bool:
        """
        添加黑名单
        :param group_id: 群组ID
        :param user_id: 用户ID
        :return: 是否添加成功
        :raises: Exception 添加失败时抛出异常
        """
        try:
            # 先检查是否已存在
            if self.is_in_blacklist(group_id, user_id):
                return False

            # 获取当前时间
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 插入数据
            self.cursor.execute(
                """INSERT INTO blacklist (group_id, user_id, created_at) 
                VALUES (?, ?, ?)""",
                (group_id, user_id, created_at),
            )
            self.conn.commit()
            self._close()
            return True
        except sqlite3.Error as e:
            raise Exception(f"添加黑名单失败: {str(e)}")

    def remove_blacklist(self, group_id: str, user_id: str) -> bool:
        """
        移除黑名单
        :param group_id: 群组ID
        :param user_id: 用户ID
        :return: 是否移除成功
        :raises: Exception 移除失败时抛出异常
        """
        try:
            self.cursor.execute(
                "DELETE FROM blacklist WHERE group_id = ? AND user_id = ?",
                (group_id, user_id),
            )
            self.conn.commit()
            self._close()
            return True
        except sqlite3.Error as e:
            raise Exception(f"移除黑名单失败: {str(e)}")

    def is_in_blacklist(self, group_id: str, user_id: str) -> bool:
        """
        检查用户是否在黑名单中
        :param group_id: 群组ID
        :param user_id: 用户ID
        :return: 是否在黑名单中
        :raises: Exception 查询失败时抛出异常
        """
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM blacklist WHERE group_id = ? AND user_id = ?",
                (group_id, user_id),
            )
            count = self.cursor.fetchone()[0]
            self._close()
            return count > 0
        except sqlite3.Error as e:
            raise Exception(f"查询黑名单失败: {str(e)}")

    def get_group_blacklist(self, group_id: str) -> list:
        """
        获取群组的所有黑名单
        :param group_id: 群组ID
        :return: [(user_id, created_at), ...]
        :raises: Exception 查询失败时抛出异常
        """
        try:
            self.cursor.execute(
                "SELECT user_id, created_at FROM blacklist WHERE group_id = ?",
                (group_id,),
            )
            self._close()
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            raise Exception(f"获取群组黑名单失败: {str(e)}")

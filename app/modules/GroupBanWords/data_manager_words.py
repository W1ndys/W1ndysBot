import sqlite3
import os
from . import MODULE_NAME


class DataManager:
    def __init__(self, group_id):
        """初始化数据管理器
        Args:
            group_id (str): 群组ID
        """
        self.data_dir = os.path.join("data", MODULE_NAME, group_id)
        os.makedirs(self.data_dir, exist_ok=True)
        self.db_path = os.path.join(self.data_dir, "data.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """建表函数，如果表不存在则创建，并兼容旧表结构升级
        Returns:
            None
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ban_words (
                word TEXT PRIMARY KEY,
                weight INTEGER NOT NULL
            )
            """
        )
        # 检查并升级旧表结构，添加update_time字段
        self.cursor.execute("PRAGMA table_info(ban_words)")
        columns = [row[1] for row in self.cursor.fetchall()]
        if "update_time" not in columns:
            self.cursor.execute(
                "ALTER TABLE ban_words ADD COLUMN update_time TIMESTAMP"
            )
        # 新增用户状态表
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_status (
                user_id TEXT PRIMARY KEY,
                status TEXT NOT NULL
            )
            """
        )
        # 检查并升级旧user_status表结构，添加update_time字段
        self.cursor.execute("PRAGMA table_info(user_status)")
        columns = [row[1] for row in self.cursor.fetchall()]
        if "update_time" not in columns:
            self.cursor.execute(
                "ALTER TABLE user_status ADD COLUMN update_time TIMESTAMP"
            )
        self.conn.commit()

    def __enter__(self):
        """上下文管理器入口
        Returns:
            DataManager: 返回当前实例
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，关闭数据库连接
        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪信息
        """
        self.conn.close()

    def add_word(self, word, weight=10):
        """添加敏感词及权值，若已存在则更新权值和时间
        Args:
            word (str): 敏感词
            weight (int, optional): 权值，默认为10
        Returns:
            bool: 操作是否成功
        """
        self.cursor.execute(
            "INSERT INTO ban_words (word, weight, update_time) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(word) DO UPDATE SET weight=excluded.weight, update_time=CURRENT_TIMESTAMP",
            (word, weight),
        )
        self.conn.commit()
        return True

    def get_all_words_and_weight(self):
        """获取所有敏感词及权值
        Returns:
            list: 包含(word, weight)元组的列表
        """
        self.cursor.execute("SELECT word, weight FROM ban_words")
        return self.cursor.fetchall()

    def update_word(self, word, new_weight):
        """更新敏感词的权值
        Args:
            word (str): 敏感词
            new_weight (int): 新的权值
        Returns:
            bool: 操作是否成功
        """
        self.cursor.execute(
            "UPDATE ban_words SET weight=? WHERE word=?", (new_weight, word)
        )
        self.conn.commit()
        return True

    def delete_word(self, word):
        """删除敏感词
        Args:
            word (str): 敏感词
        Returns:
            bool: 操作是否成功
        """
        self.cursor.execute("DELETE FROM ban_words WHERE word=?", (word,))
        self.conn.commit()
        return True

    def calc_message_weight(self, message):
        """计算消息的违禁程度（所有命中违禁词的权值求和）
        Args:
            message (str): 需要检查的消息文本
        Returns:
            tuple: (总权值, 命中的违禁词列表)
            total_weight: 总权值
            matched_words: 命中的违禁词列表和权值的元组列表
        """
        self.cursor.execute("SELECT word, weight FROM ban_words")
        matched_words = []
        total_weight = 0
        for word, weight in self.cursor.fetchall():
            if word in message:
                total_weight += weight
                matched_words.append((word, weight))
        return total_weight, matched_words

    def set_user_status(self, user_id, status):
        """设置某用户状态，若已存在则更新
        Args:
            user_id (str): 用户ID
            status (str): 用户状态
        Returns:
            bool: 操作是否成功
        """
        self.cursor.execute(
            "INSERT INTO user_status (user_id, status, update_time) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(user_id) DO UPDATE SET status=excluded.status, update_time=CURRENT_TIMESTAMP",
            (user_id, status),
        )
        self.conn.commit()
        return True

    def get_user_status(self, user_id):
        """获取某用户状态
        Args:
            user_id (str): 用户ID
        Returns:
            str: 用户状态，如果用户不存在则返回None
        """
        self.cursor.execute(
            "SELECT status FROM user_status WHERE user_id=?", (user_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def delete_user_status(self, user_id):
        """删除某用户状态
        Args:
            user_id (str): 用户ID
        Returns:
            bool: 操作是否成功
        """
        self.cursor.execute("DELETE FROM user_status WHERE user_id=?", (user_id,))
        self.conn.commit()
        return True

    def get_all_user_status(self):
        """获取所有用户状态
        Returns:
            list: 包含(user_id, status, update_time)元组的列表
        """
        self.cursor.execute("SELECT user_id, status, update_time FROM user_status")
        return self.cursor.fetchall()

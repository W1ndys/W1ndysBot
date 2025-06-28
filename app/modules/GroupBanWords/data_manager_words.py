import sqlite3
import os
import re
import glob
from typing import Optional
from . import MODULE_NAME


class DataManager:
    # 类级别的数据库连接，所有实例共享
    _db_path = os.path.join("data", MODULE_NAME, "global_data.db")
    _conn: Optional[sqlite3.Connection] = None
    _initialized = False

    # 全局词库群号常量
    GLOBAL_GROUP_ID = "0"

    def __init__(self, group_id):
        """初始化数据管理器
        Args:
            group_id (str): 群组ID，"0"表示全局词库
        """
        self.group_id = str(group_id)

        # 确保数据目录存在
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)

        # 初始化全局数据库连接
        if not DataManager._initialized:
            DataManager._init_global_db()

    @classmethod
    def _init_global_db(cls):
        """初始化全局数据库连接和表结构"""
        if cls._conn is None:
            cls._conn = sqlite3.connect(cls._db_path, check_same_thread=False)
            cls._conn.execute("PRAGMA foreign_keys = ON")
            cls._create_tables()
            cls._initialized = True

    @classmethod
    def _create_tables(cls):
        """创建表结构"""
        assert cls._conn is not None  # 添加断言确保连接存在
        cursor = cls._conn.cursor()

        # 创建违禁词表（群号"0"为全局词库）
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ban_words (
                group_id TEXT NOT NULL,
                word TEXT NOT NULL,
                weight INTEGER NOT NULL,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (group_id, word)
            )
            """
        )

        # 创建用户状态表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_status (
                group_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                status TEXT NOT NULL,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (group_id, user_id)
            )
            """
        )

        cls._conn.commit()

    def add_word(self, word, weight=10):
        """添加敏感词及权值，若已存在则更新权值和时间
        Args:
            word (str): 敏感词
            weight (int, optional): 权值，默认为10
        Returns:
            bool: 操作是否成功
        """
        assert self._conn is not None  # 添加断言确保连接存在
        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT INTO ban_words (group_id, word, weight, update_time) 
            VALUES (?, ?, ?, CURRENT_TIMESTAMP) 
            ON CONFLICT(group_id, word) DO UPDATE SET 
                weight=excluded.weight, 
                update_time=CURRENT_TIMESTAMP
            """,
            (self.group_id, word, weight),
        )
        self._conn.commit()
        return True

    def get_all_words_and_weight(self):
        """获取当前群组的所有敏感词及权值
        Returns:
            list: 包含(word, weight)元组的列表
        """
        assert self._conn is not None  # 添加断言确保连接存在
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT word, weight FROM ban_words WHERE group_id=?", (self.group_id,)
        )
        return cursor.fetchall()

    def update_word(self, word, new_weight):
        """更新敏感词的权值
        Args:
            word (str): 敏感词
            new_weight (int): 新的权值
        Returns:
            bool: 操作是否成功
        """
        assert self._conn is not None  # 添加断言确保连接存在
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE ban_words SET weight=?, update_time=CURRENT_TIMESTAMP WHERE group_id=? AND word=?",
            (new_weight, self.group_id, word),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def delete_word(self, word):
        """删除敏感词
        Args:
            word (str): 敏感词
        Returns:
            bool: 操作是否成功，如果词不存在则返回False
        """
        assert self._conn is not None  # 添加断言确保连接存在
        cursor = self._conn.cursor()
        cursor.execute(
            "DELETE FROM ban_words WHERE group_id=? AND word=?", (self.group_id, word)
        )
        rows_affected = cursor.rowcount
        self._conn.commit()
        return rows_affected > 0

    def calc_message_weight(self, message):
        """计算消息的违禁程度（所有命中违禁词的权值求和）
        群专属词库优先级大于全局词库（群号"0"），如果同一个词在两个词库都存在，使用群专属的权重
        Args:
            message (str): 需要检查的消息文本
        Returns:
            tuple: (总权值, 命中的违禁词列表)
            total_weight: 总权值
            matched_words: 命中的违禁词列表和权值的元组列表
        """
        assert self._conn is not None  # 添加断言确保连接存在
        cursor = self._conn.cursor()

        # 获取群专属违禁词
        cursor.execute(
            "SELECT word, weight FROM ban_words WHERE group_id=?", (self.group_id,)
        )
        group_words = dict(cursor.fetchall())

        # 获取全局违禁词（群号为"0"）
        cursor.execute(
            "SELECT word, weight FROM ban_words WHERE group_id=?",
            (self.GLOBAL_GROUP_ID,),
        )
        global_words = dict(cursor.fetchall())

        # 合并词库，群专属优先
        merged_words = global_words.copy()
        merged_words.update(group_words)  # 群专属词库覆盖全局词库

        matched_words = []
        total_weight = 0
        for word, weight in merged_words.items():
            try:
                if re.search(word, message):
                    total_weight += weight
                    # 标记来源
                    source = "群专属" if word in group_words else "全局"
                    matched_words.append((f"{word}({source})", weight))
            except re.error:
                # 如果正则表达式无效，则退回到普通字符串匹配
                if word in message:
                    total_weight += weight
                    # 标记来源
                    source = "群专属" if word in group_words else "全局"
                    matched_words.append((f"{word}({source})", weight))
        return total_weight, matched_words

    def set_user_status(self, user_id, status, group_id=None):
        """设置某用户状态，若已存在则更新
        Args:
            user_id (str): 用户ID
            status (str): 用户状态
            group_id (str, optional): 群组ID，如果不提供则使用实例的group_id
        Returns:
            bool: 操作是否成功
        """
        assert self._conn is not None  # 添加断言确保连接存在
        cursor = self._conn.cursor()
        # 如果提供了group_id参数则使用，否则使用实例的group_id
        target_group_id = group_id if group_id is not None else self.group_id
        cursor.execute(
            """
            INSERT INTO user_status (group_id, user_id, status, update_time) 
            VALUES (?, ?, ?, CURRENT_TIMESTAMP) 
            ON CONFLICT(group_id, user_id) DO UPDATE SET 
                status=excluded.status, 
                update_time=CURRENT_TIMESTAMP
            """,
            (target_group_id, user_id, status),
        )
        self._conn.commit()
        return True

    def get_user_status(self, user_id, group_id=None):
        """获取某用户状态
        Args:
            user_id (str): 用户ID
            group_id (str, optional): 群组ID，如果不提供则使用实例的group_id
        Returns:
            str: 用户状态，如果用户不存在则返回None
        """
        assert self._conn is not None  # 添加断言确保连接存在
        cursor = self._conn.cursor()
        # 如果提供了group_id参数则使用，否则使用实例的group_id
        target_group_id = group_id if group_id is not None else self.group_id
        cursor.execute(
            "SELECT status FROM user_status WHERE group_id=? AND user_id=?",
            (target_group_id, user_id),
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def delete_user_status(self, user_id):
        """删除某用户状态
        Args:
            user_id (str): 用户ID
        Returns:
            bool: 操作是否成功
        """
        assert self._conn is not None  # 添加断言确保连接存在
        cursor = self._conn.cursor()
        cursor.execute(
            "DELETE FROM user_status WHERE group_id=? AND user_id=?",
            (self.group_id, user_id),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def get_all_user_status(self):
        """获取当前群组的所有用户状态
        Returns:
            list: 包含(user_id, status, update_time)元组的列表
        """
        assert self._conn is not None  # 添加断言确保连接存在
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT user_id, status, update_time FROM user_status WHERE group_id=?",
            (self.group_id,),
        )
        return cursor.fetchall()

    @classmethod
    def get_global_stats(cls):
        """获取全局统计信息
        Returns:
            dict: 包含各种统计信息的字典
        """
        if cls._conn is None:
            cls._init_global_db()

        assert cls._conn is not None  # 添加断言确保连接存在
        cursor = cls._conn.cursor()

        # 统计群组数量（排除全局群号"0"）
        cursor.execute(
            "SELECT COUNT(DISTINCT group_id) FROM ban_words WHERE group_id != '0'"
        )
        groups_with_words = cursor.fetchone()[0]

        # 统计总违禁词数量（排除全局）
        cursor.execute("SELECT COUNT(*) FROM ban_words WHERE group_id != '0'")
        total_words = cursor.fetchone()[0]

        # 统计全局违禁词数量（群号为"0"）
        cursor.execute("SELECT COUNT(*) FROM ban_words WHERE group_id = '0'")
        total_global_words = cursor.fetchone()[0]

        # 统计总用户状态数量
        cursor.execute("SELECT COUNT(*) FROM user_status")
        total_user_status = cursor.fetchone()[0]

        # 按群组统计违禁词数量（排除全局）
        cursor.execute(
            "SELECT group_id, COUNT(*) FROM ban_words WHERE group_id != '0' GROUP BY group_id ORDER BY COUNT(*) DESC"
        )
        words_by_group = cursor.fetchall()

        return {
            "groups_with_words": groups_with_words,
            "total_words": total_words,
            "total_global_words": total_global_words,
            "total_user_status": total_user_status,
            "words_by_group": words_by_group,
        }

    @classmethod
    def get_group_list(cls):
        """获取所有有数据的群组列表
        Returns:
            list: 群组ID列表
        """
        if cls._conn is None:
            cls._init_global_db()

        assert cls._conn is not None  # 添加断言确保连接存在
        cursor = cls._conn.cursor()
        cursor.execute(
            "SELECT DISTINCT group_id FROM ban_words UNION SELECT DISTINCT group_id FROM user_status ORDER BY group_id"
        )
        return [row[0] for row in cursor.fetchall()]

    def __enter__(self):
        """上下文管理器入口
        Returns:
            DataManager: 返回当前实例
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口
        注意：不再关闭数据库连接，因为是全局共享的
        """
        pass

    @classmethod
    def close_global_connection(cls):
        """关闭全局数据库连接（在程序退出时调用）"""
        if cls._conn:
            cls._conn.close()
            cls._conn = None
            cls._initialized = False

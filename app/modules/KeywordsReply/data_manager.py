import sqlite3
import os
from . import MODULE_NAME


class DataManager:
    def __init__(self):
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"data.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """建表函数，如果表不存在则创建"""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS keywords_reply (
                group_id TEXT,
                keyword TEXT,
                reply TEXT NOT NULL,
                adder_qq TEXT,
                add_time TEXT,
                PRIMARY KEY (group_id, keyword)
            )
            """
        )
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def add_keyword(self, group_id, keyword, reply, adder_qq, add_time):
        """添加或更新关键词及回复内容，若关键词已存在则覆盖，需指定群号、添加者、时间"""
        self.cursor.execute(
            "REPLACE INTO keywords_reply (group_id, keyword, reply, adder_qq, add_time) VALUES (?, ?, ?, ?, ?)",
            (group_id, keyword, reply, adder_qq, add_time),
        )
        self.conn.commit()

    def delete_keyword(self, group_id, keyword):
        """根据群号和关键词删除对应记录"""
        self.cursor.execute(
            "DELETE FROM keywords_reply WHERE group_id = ? AND keyword = ?",
            (group_id, keyword),
        )
        self.conn.commit()

    def get_reply(self, group_id, keyword):
        """根据群号和关键词返回回复内容，找不到返回None"""
        self.cursor.execute(
            "SELECT reply FROM keywords_reply WHERE group_id = ? AND keyword = ?",
            (group_id, keyword),
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def clear_keywords(self, group_id):
        """清空指定群的所有关键词"""
        self.cursor.execute(
            "DELETE FROM keywords_reply WHERE group_id = ?", (group_id,)
        )
        self.conn.commit()

    def get_all_keywords(self, group_id):
        """查看指定群的所有关键词，返回关键词列表"""
        self.cursor.execute(
            "SELECT keyword FROM keywords_reply WHERE group_id = ?", (group_id,)
        )
        return [row[0] for row in self.cursor.fetchall()]

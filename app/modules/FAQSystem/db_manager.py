import sqlite3
import os
from typing import List, Tuple, Optional
from . import DATA_DIR


class FAQDatabaseManager:
    def __init__(self, group_id: str):
        """
        初始化 QADatabaseManager 实例，为指定群组创建/连接数据库。
        参数:
            group_id: str 群组ID
        """
        self.db_path = os.path.join(DATA_DIR, group_id, "FAQ_data.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def __enter__(self):
        """
        支持with语句的进入方法。
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        支持with语句的退出方法，自动关闭数据库连接。
        """
        self.cursor.close()
        self.conn.close()

    def _create_table(self):
        """
        创建存储问答对的表（如不存在则新建）。
        """
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS FAQ_pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL
            )
        """
        )
        self.conn.commit()

    def add_FAQ_pair(self, question: str, answer: str) -> Optional[int]:
        """
        添加问答到数据库。如果问题已存在，则更新答案，否则插入新问答对。
        参数:
            question: str 问题内容
            answer: str 答案内容
        返回:
            int 问答对的ID（主键），失败时返回None
        """
        # 检查问题是否已存在
        self.cursor.execute("SELECT id FROM FAQ_pairs WHERE question = ?", (question,))
        row = self.cursor.fetchone()
        if row:
            # 已存在，更新答案
            qa_id = row[0]
            self.cursor.execute(
                "UPDATE FAQ_pairs SET answer = ? WHERE id = ?", (answer, qa_id)
            )
            self.conn.commit()
            return qa_id
        else:
            # 不存在，插入新问答对
            self.cursor.execute(
                "INSERT INTO FAQ_pairs (question, answer) VALUES (?, ?)",
                (question, answer),
            )
            self.conn.commit()
            last_id = self.cursor.lastrowid
            return last_id

    def get_FAQ_pair(self, qa_id: int) -> Optional[Tuple[int, str, str]]:
        """
        根据ID获取单个问答对。
        参数:
            qa_id: int 问答对ID
        返回:
            (id, question, answer) 元组，未找到时返回None
        """
        self.cursor.execute(
            "SELECT id, question, answer FROM FAQ_pairs WHERE id = ?", (qa_id,)
        )
        result = self.cursor.fetchone()
        return result

    def get_all_FAQ_pairs(self) -> List[Tuple[int, str, str]]:
        """
        获取所有问答对。
        返回:
            包含所有 (id, question, answer) 元组的列表
        """
        self.cursor.execute("SELECT id, question, answer FROM FAQ_pairs")
        result = self.cursor.fetchall()
        return result

    def update_FAQ_pair(self, qa_id: int, question: str, answer: str) -> bool:
        """
        更新指定ID的问答对内容。
        参数:
            qa_id: int 问答对ID
            question: str 新的问题内容
            answer: str 新的答案内容
        返回:
            bool 是否更新成功
        """
        self.cursor.execute(
            "UPDATE FAQ_pairs SET question = ?, answer = ? WHERE id = ?",
            (question, answer, qa_id),
        )
        self.conn.commit()
        updated = self.cursor.rowcount > 0
        return updated

    def delete_FAQ_pair(self, qa_id: int) -> bool:
        """
        删除指定ID的问答对。
        参数:
            qa_id: int 问答对ID
        返回:
            bool 是否删除成功
        """
        self.cursor.execute("DELETE FROM FAQ_pairs WHERE id = ?", (qa_id,))
        self.conn.commit()
        deleted = self.cursor.rowcount > 0
        return deleted

import sqlite3
import os
from typing import List, Tuple, Optional
from . import DATA_DIR


class QADatabaseManager:
    def __init__(self, group_id: str):
        """
        初始化 QADatabaseManager 实例，为指定群组创建/连接数据库。
        参数:
            group_id: str 群组ID
        """
        self.db_path = os.path.join(DATA_DIR, group_id, "qa_data.db")
        self._create_table()

    def _create_table(self):
        """
        创建存储问答对的表（如不存在则新建）。
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS qa_pairs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL
                )
            """
            )
            conn.commit()

    def add_qa_pair(self, question: str, answer: str) -> Optional[int]:
        """
        添加问答对到数据库。
        参数:
            question: str 问题内容
            answer: str 答案内容
        返回:
            int 新增问答对的ID（主键），失败时返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO qa_pairs (question, answer) VALUES (?, ?)",
                (question, answer),
            )
            conn.commit()
            return cursor.lastrowid

    def get_qa_pair(self, qa_id: int) -> Optional[Tuple[int, str, str]]:
        """
        根据ID获取单个问答对。
        参数:
            qa_id: int 问答对ID
        返回:
            (id, question, answer) 元组，未找到时返回None
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, question, answer FROM qa_pairs WHERE id = ?", (qa_id,)
            )
            return cursor.fetchone()

    def get_all_qa_pairs(self) -> List[Tuple[int, str, str]]:
        """
        获取所有问答对。
        返回:
            包含所有 (id, question, answer) 元组的列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, question, answer FROM qa_pairs")
            return cursor.fetchall()

    def update_qa_pair(self, qa_id: int, question: str, answer: str) -> bool:
        """
        更新指定ID的问答对内容。
        参数:
            qa_id: int 问答对ID
            question: str 新的问题内容
            answer: str 新的答案内容
        返回:
            bool 是否更新成功
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE qa_pairs SET question = ?, answer = ? WHERE id = ?",
                (question, answer, qa_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_qa_pair(self, qa_id: int) -> bool:
        """
        删除指定ID的问答对。
        参数:
            qa_id: int 问答对ID
        返回:
            bool 是否删除成功
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM qa_pairs WHERE id = ?", (qa_id,))
            conn.commit()
            return cursor.rowcount > 0

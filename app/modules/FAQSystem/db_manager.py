import sqlite3
import os
from typing import List, Tuple, Optional
from modules.FAQSystem import DATA_DIR


class FAQDatabaseManager:
    def __init__(self, group_id: str):
        """
        初始化 FAQDatabaseManager 实例，为指定群组创建/连接数据库。
        参数:
            group_id: str 群组ID
        """
        self.group_id = group_id
        self.table_name = f"FAQ_group_{group_id}"
        self.db_path = os.path.join(DATA_DIR, "FAQ_data.db")
        os.makedirs(DATA_DIR, exist_ok=True)
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
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
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
        self.cursor.execute(
            f"SELECT id FROM {self.table_name} WHERE question = ?", (question,)
        )
        row = self.cursor.fetchone()
        if row:
            # 已存在，更新答案
            qa_id = row[0]
            self.cursor.execute(
                f"UPDATE {self.table_name} SET answer = ? WHERE id = ?", (answer, qa_id)
            )
            self.conn.commit()
            return qa_id
        else:
            # 不存在，插入新问答对
            self.cursor.execute(
                f"INSERT INTO {self.table_name} (question, answer) VALUES (?, ?)",
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
            f"SELECT id, question, answer FROM {self.table_name} WHERE id = ?", (qa_id,)
        )
        result = self.cursor.fetchone()
        return result

    def get_all_FAQ_pairs(self) -> List[Tuple[int, str, str]]:
        """
        获取当前群（表）下的所有问答对。
        返回:
            包含该群所有 (id, question, answer) 元组的列表
        """
        self.cursor.execute(f"SELECT id, question, answer FROM {self.table_name}")
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
            f"UPDATE {self.table_name} SET question = ?, answer = ? WHERE id = ?",
            (question, answer, qa_id),
        )
        self.conn.commit()
        updated = self.cursor.rowcount > 0
        return updated

    def delete_FAQ_pair(self, qa_id: int) -> dict:
        """
        删除指定ID的问答对。
        参数:
            qa_id: int 问答对ID
        返回:
            dict 包含删除结果的字典：
            {
                'success': bool,  # 是否删除成功
                'message': str,   # 提示信息
                'data': dict or None  # 被删除的问答对信息（如果存在）
            }
        """
        # 先检查问答对是否存在
        self.cursor.execute(
            f"SELECT id, question, answer FROM {self.table_name} WHERE id = ?", (qa_id,)
        )
        existing_pair = self.cursor.fetchone()

        if not existing_pair:
            return {
                "success": False,
                "message": f"问答对ID {qa_id} 不存在",
                "data": None,
            }

        # 存在则执行删除
        self.cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (qa_id,))
        self.conn.commit()

        deleted = self.cursor.rowcount > 0
        if deleted:
            return {
                "success": True,
                "message": f"问答对ID {qa_id} 删除成功",
                "data": {
                    "id": existing_pair[0],
                    "question": existing_pair[1],
                    "answer": existing_pair[2],
                },
            }
        else:
            return {
                "success": False,
                "message": f"问答对ID {qa_id} 删除失败",
                "data": None,
            }

    @classmethod
    def get_all_groups(cls) -> List[str]:
        """
        获取所有存在FAQ数据的群组ID列表。
        返回:
            群组ID列表
        """
        db_path = os.path.join(DATA_DIR, "FAQ_data.db")
        if not os.path.exists(db_path):
            return []

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 获取所有以FAQ_group_开头的表名
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'FAQ_group_%'"
        )
        tables = cursor.fetchall()

        conn.close()

        # 提取群组ID
        group_ids = []
        for table in tables:
            table_name = table[0]
            group_id = table_name.replace("FAQ_group_", "")
            group_ids.append(group_id)

        return group_ids

    def drop_group_data(self) -> bool:
        """
        删除当前群组的所有FAQ数据（删除表）。
        返回:
            bool 是否删除成功
        """
        self.cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")
        self.conn.commit()
        return True

    def get_FAQ_id_by_question(self, question: str) -> int:
        """
        根据问题内容获取问答对ID。
        参数:
            question: str 问题内容
        返回:
            int 问答对ID，未找到时返回-1
        """
        self.cursor.execute(
            f"SELECT id FROM {self.table_name} WHERE question = ?", (question,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else -1

    def search_FAQ_by_keyword(self, keyword: str) -> List[Tuple[int, str, str]]:
        """
        根据关键词搜索问答对（支持模糊匹配）。
        参数:
            keyword: str 搜索关键词
        返回:
            包含匹配的 (id, question, answer) 元组的列表
        """
        self.cursor.execute(
            f"SELECT id, question, answer FROM {self.table_name} WHERE question LIKE ? OR answer LIKE ?",
            (f"%{keyword}%", f"%{keyword}%"),
        )
        result = self.cursor.fetchall()
        return result

    def get_FAQ_count(self) -> int:
        """
        获取当前群组的问答对总数。
        返回:
            int 问答对总数
        """
        self.cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
        result = self.cursor.fetchone()
        return result[0] if result else 0

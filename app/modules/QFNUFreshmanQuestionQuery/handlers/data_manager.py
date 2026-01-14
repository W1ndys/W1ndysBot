import sqlite3
import os


class DataManager:
    def __init__(self):
        # 数据库文件位于模块目录下
        module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(module_dir, "freshman_questions.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def search_questions(self, keyword: str, limit: int = 5) -> list:
        """
        根据关键词搜索题目（使用简单的字符串模糊匹配）

        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制

        Returns:
            匹配的题目列表，每个元素为元组:
            (id, type, question, optionA, optionB, optionC, optionD, optionAnswer)
        """
        if not keyword or not keyword.strip():
            return []

        keyword = keyword.strip()

        # 使用 LIKE 进行模糊匹配
        self.cursor.execute(
            """SELECT id, type, question, optionA, optionB, optionC, optionD, optionAnswer
               FROM questions
               WHERE question LIKE ?
               LIMIT ?""",
            (f"%{keyword}%", limit),
        )
        return self.cursor.fetchall()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

import sqlite3
import os
from . import MODULE_NAME


class DataManager:
    def __init__(
        self, group_id
    ):  #  这里以群聊为例，如果需要处理私聊，可以传入user_id或其他实现方法
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(
            data_dir, f"group_{group_id}.db"
        )  # 这里以群聊为例，如果需要处理私聊，可以传入user_id或其他实现方法
        self._create_table()

    def _create_table(self):
        """建表函数，如果表不存在则创建"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS data_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL
                )
            """
            )

    # 其他函数，使用sqlite3.connect(self.db_path) as conn:进行数据库操作
    def insert_data(self, data):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO data_table (data) VALUES (?)", (data,))
            conn.commit()

    def get_data(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT data FROM data_table")
            data = cursor.fetchall()
            return [row[0] for row in data]

    def delete_data(self, id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM data_table WHERE id = ?", (id,))
            conn.commit()

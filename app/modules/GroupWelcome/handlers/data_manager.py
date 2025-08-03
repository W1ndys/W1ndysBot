import sqlite3
import os
from .. import MODULE_NAME


class DataManager:
    def __init__(self):
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"{MODULE_NAME}.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """建表函数，如果表不存在则创建"""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS welcome_notices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                notice_type TEXT NOT NULL CHECK (notice_type IN ('in', 'out')),
                notice_content TEXT NOT NULL,
                UNIQUE(group_id, notice_type)
            )
        """
        )
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def set_notice_content(self, group_id: str, notice_type: str, notice_content: str):
        """存储指定群号指定通知类型的通知内容"""
        if notice_type not in ["in", "out"]:
            raise ValueError("通知类型必须是 'in' 或 'out'")

        # 使用 INSERT OR REPLACE 来处理更新或插入
        self.cursor.execute(
            """
            INSERT OR REPLACE INTO welcome_notices (group_id, notice_type, notice_content)
            VALUES (?, ?, ?)
        """,
            (group_id, notice_type, notice_content),
        )
        self.conn.commit()

    def get_notice_content(self, group_id: str, notice_type: str) -> str:
        """根据群号和通知类型获取通知内容"""
        if notice_type not in ["in", "out"]:
            raise ValueError("通知类型必须是 'in' 或 'out'")

        self.cursor.execute(
            """
            SELECT notice_content FROM welcome_notices 
            WHERE group_id = ? AND notice_type = ?
        """,
            (group_id, notice_type),
        )

        result = self.cursor.fetchone()
        return result[0] if result else ""

    def get_all_notices_by_group(self, group_id: str) -> dict:
        """获取指定群的所有通知内容"""
        self.cursor.execute(
            """
            SELECT notice_type, notice_content FROM welcome_notices 
            WHERE group_id = ?
        """,
            (group_id,),
        )

        results = self.cursor.fetchall()
        return {notice_type: content for notice_type, content in results}

    def delete_notice(self, group_id: str, notice_type: str = ""):
        """删除指定群的通知内容，如果不指定类型则删除该群所有通知"""
        if notice_type:
            if notice_type not in ["in", "out"]:
                raise ValueError("通知类型必须是 'in' 或 'out'")
            self.cursor.execute(
                """
                DELETE FROM welcome_notices 
                WHERE group_id = ? AND notice_type = ?
            """,
                (group_id, notice_type),
            )
        else:
            self.cursor.execute(
                """
                DELETE FROM welcome_notices 
                WHERE group_id = ?
            """,
                (group_id,),
            )
        self.conn.commit()

    def get_all_groups_with_notices(self) -> list:
        """获取所有设置了欢迎消息的群号"""
        self.cursor.execute(
            """
            SELECT DISTINCT group_id FROM welcome_notices
        """
        )
        return [row[0] for row in self.cursor.fetchall()]

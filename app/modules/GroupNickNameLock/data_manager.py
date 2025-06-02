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
        self._create_tables()

    def _create_tables(self):
        """建表函数，创建正则、默认名、锁定昵称表"""
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS group_regex (
                group_id TEXT PRIMARY KEY,
                regex TEXT
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS group_default_name (
                group_id TEXT PRIMARY KEY,
                default_name TEXT
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS group_user_lock (
                group_id TEXT,
                user_id TEXT,
                lock_name TEXT,
                PRIMARY KEY (group_id, user_id)
            )
            """
        )
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    # 群正则相关
    def set_group_regex(self, group_id, regex):
        self.cursor.execute(
            "REPLACE INTO group_regex (group_id, regex) VALUES (?, ?)", (group_id, regex)
        )
        self.conn.commit()

    def get_group_regex(self, group_id):
        self.cursor.execute(
            "SELECT regex FROM group_regex WHERE group_id = ?", (group_id,)
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    def del_group_regex(self, group_id):
        self.cursor.execute(
            "DELETE FROM group_regex WHERE group_id = ?", (group_id,)
        )
        self.conn.commit()

    # 群默认名相关
    def set_group_default_name(self, group_id, default_name):
        self.cursor.execute(
            "REPLACE INTO group_default_name (group_id, default_name) VALUES (?, ?)", (group_id, default_name)
        )
        self.conn.commit()

    def get_group_default_name(self, group_id):
        self.cursor.execute(
            "SELECT default_name FROM group_default_name WHERE group_id = ?", (group_id,)
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    # 用户锁定昵称相关
    def set_user_lock_name(self, group_id, user_id, lock_name):
        self.cursor.execute(
            "REPLACE INTO group_user_lock (group_id, user_id, lock_name) VALUES (?, ?, ?)", (group_id, user_id, lock_name)
        )
        self.conn.commit()

    def get_user_lock_name(self, group_id, user_id):
        self.cursor.execute(
            "SELECT lock_name FROM group_user_lock WHERE group_id = ? AND user_id = ?", (group_id, user_id)
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    def del_user_lock_name(self, group_id, user_id):
        self.cursor.execute(
            "DELETE FROM group_user_lock WHERE group_id = ? AND user_id = ?", (group_id, user_id)
        )
        self.conn.commit()

    def get_all_user_locks(self, group_id):
        self.cursor.execute(
            "SELECT user_id, lock_name FROM group_user_lock WHERE group_id = ?", (group_id,)
        )
        return self.cursor.fetchall()

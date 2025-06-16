import sqlite3
import os
from . import MODULE_NAME
import logger


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
            """CREATE TABLE IF NOT EXISTS system_credential (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            cookies TEXT,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
        )

        # 创建用户可用次数表
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS user_usage (
            user_id INTEGER PRIMARY KEY,
            available_times INTEGER NOT NULL DEFAULT 0
        )"""
        )

        # 创建邀请记录表
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS invitation_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            invited_user_id INTEGER NOT NULL,
            invite_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, invited_user_id)
        )"""
        )

        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    # 账号密码和cookies相关操作
    def save_credential(self, username, password, cookies=None):
        """保存或更新系统唯一的凭据"""
        self.cursor.execute("DELETE FROM system_credential")
        self.cursor.execute(
            """
            INSERT INTO system_credential (id, username, password, cookies, update_time)
            VALUES (1, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
            (username, password, cookies),
        )
        self.conn.commit()
        logger.info(f"[{MODULE_NAME}]保存凭据成功: {username} {password} {cookies}")

    def update_cookies(self, cookies):
        """更新cookies"""
        self.cursor.execute(
            """
            UPDATE system_credential SET cookies=?, update_time=CURRENT_TIMESTAMP
            WHERE id=1
        """,
            (cookies,),
        )
        self.conn.commit()
        logger.info(f"[{MODULE_NAME}]更新cookies成功: {cookies}")
        return self.cursor.rowcount > 0

    def get_credential(self):
        """获取凭据"""
        self.cursor.execute(
            """
            SELECT username, password, cookies, update_time
            FROM system_credential WHERE id=1
        """
        )
        result = self.cursor.fetchone()
        logger.info(f"[{MODULE_NAME}]获取凭据成功: {result}")
        return result

    def has_credential(self):
        """检查是否已存储凭据"""
        self.cursor.execute("SELECT COUNT(*) FROM system_credential")
        return self.cursor.fetchone()[0] > 0

    # 用户可用次数相关操作
    def get_user_available_times(self, user_id):
        """获取用户可用次数"""
        self.cursor.execute(
            "SELECT available_times FROM user_usage WHERE user_id = ?", (user_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def set_user_available_times(self, user_id, times):
        """设置用户可用次数"""
        self.cursor.execute(
            """INSERT INTO user_usage (user_id, available_times) 
            VALUES (?, ?) 
            ON CONFLICT(user_id) DO UPDATE SET available_times = ?""",
            (user_id, times, times),
        )
        self.conn.commit()

    def add_user_available_times(self, user_id, times_to_add):
        """增加用户可用次数"""
        current_times = self.get_user_available_times(user_id)
        new_times = current_times + times_to_add
        self.set_user_available_times(user_id, new_times)
        return new_times

    def decrease_user_available_times(self, user_id):
        """减少用户可用次数，如果次数不足返回False"""
        current_times = self.get_user_available_times(user_id)
        if current_times <= 0:
            return False
        self.set_user_available_times(user_id, current_times - 1)
        return True

    # 邀请记录相关操作
    def add_invitation_record(self, user_id, group_id, invited_user_id):
        """添加邀请记录"""
        try:
            self.cursor.execute(
                """INSERT INTO invitation_records 
                (user_id, group_id, invited_user_id) 
                VALUES (?, ?, ?)""",
                (user_id, group_id, invited_user_id),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # 已存在相同的邀请记录
            return False

    def get_user_invitations(self, user_id):
        """获取用户的所有邀请记录"""
        self.cursor.execute(
            """SELECT invited_user_id, group_id, invite_time 
            FROM invitation_records 
            WHERE user_id = ?
            ORDER BY invite_time DESC""",
            (user_id,),
        )
        return self.cursor.fetchall()

    def get_invitation_count(self, user_id):
        """获取用户邀请的总人数"""
        self.cursor.execute(
            "SELECT COUNT(*) FROM invitation_records WHERE user_id = ?", (user_id,)
        )
        return self.cursor.fetchone()[0]

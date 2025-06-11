import sqlite3
import os
from . import MODULE_NAME
import datetime


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
            CREATE TABLE IF NOT EXISTS mute_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                date TEXT NOT NULL,
                duration INTEGER NOT NULL,
                UNIQUE(group_id, user_id, date)
            )
        """
        )

        # 创建索引以提高查询性能
        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_group_user_date ON mute_records(group_id, user_id, date)
        """
        )

        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_group_date ON mute_records(group_id, date)
        """
        )

        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_duration ON mute_records(duration DESC)
        """
        )

        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def update_mute_record(self, group_id, user_id, duration):
        """
        更新用户的禁言记录，如果当日时长更长则更新

        参数:
            group_id: 群号
            user_id: QQ号
            duration: 禁言时长(秒)

        返回:
            tuple: (是否创建新记录, 是否打破个人记录, 是否打破群记录, 旧的记录时长)
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        # 检查今日记录
        self.cursor.execute(
            "SELECT duration FROM mute_records WHERE group_id=? AND user_id=? AND date=?",
            (group_id, user_id, today),
        )
        result = self.cursor.fetchone()

        is_new_record = False
        break_personal_record = False
        break_group_record = False
        old_duration = 0

        if result:
            old_duration = result[0]
            # 只有当新时长大于旧时长时才更新
            if duration > old_duration:
                self.cursor.execute(
                    "UPDATE mute_records SET duration=? WHERE group_id=? AND user_id=? AND date=?",
                    (duration, group_id, user_id, today),
                )
                self.conn.commit()
                break_personal_record = True
        else:
            # 新增记录
            self.cursor.execute(
                "INSERT INTO mute_records (group_id, user_id, date, duration) VALUES (?, ?, ?, ?)",
                (group_id, user_id, today, duration),
            )
            self.conn.commit()
            is_new_record = True

        # 检查是否打破群记录
        if break_personal_record or is_new_record:
            self.cursor.execute(
                "SELECT MAX(duration) FROM mute_records WHERE group_id=? AND date=? AND user_id!=?",
                (group_id, today, user_id),
            )
            max_group_duration = self.cursor.fetchone()[0]

            if max_group_duration is None or duration > max_group_duration:
                break_group_record = True

        return (is_new_record, break_personal_record, break_group_record, old_duration)

    def get_user_today_mute_duration(self, group_id, user_id):
        """
        获取某群某用户今日禁言时长

        参数:
            group_id: 群号
            user_id: QQ号

        返回:
            int: 禁言时长(秒)，未禁言过则返回0
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        self.cursor.execute(
            "SELECT duration FROM mute_records WHERE group_id=? AND user_id=? AND date=?",
            (group_id, user_id, today),
        )
        result = self.cursor.fetchone()

        return result[0] if result else 0

    def get_group_today_top_mute_user(self, group_id):
        """
        获取某群今日禁言时长最高的用户

        参数:
            group_id: 群号

        返回:
            tuple: (user_id, duration) 或 None
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        self.cursor.execute(
            "SELECT user_id, MAX(duration) FROM mute_records WHERE group_id=? AND date=?",
            (group_id, today),
        )
        result = self.cursor.fetchone()

        return result if result and result[0] else None

    def get_global_top_mute_user(self):
        """
        获取全数据库禁言时长最高的用户

        返回:
            tuple: (group_id, user_id, date, duration) 或 None
        """
        self.cursor.execute(
            "SELECT group_id, user_id, date, MAX(duration) FROM mute_records"
        )
        result = self.cursor.fetchone()

        return result if result and result[0] else None

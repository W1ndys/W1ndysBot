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
        # 创建禁言记录表
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

        # 创建宵禁设置表
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS curfew_settings (
                group_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                is_enabled INTEGER NOT NULL DEFAULT 1
            )
        """
        )

        # 创建宵禁触发日志表
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS curfew_trigger_log (
                group_id TEXT PRIMARY KEY,
                last_trigger_time TEXT NOT NULL
            )
        """
        )

        # 创建禁言记录表的索引
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

        # 创建宵禁设置表的索引
        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_curfew_group ON curfew_settings(group_id)
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

    def set_curfew_settings(self, group_id, start_time, end_time, is_enabled=True):
        """
        设置群宵禁配置

        参数:
            group_id: 群号
            start_time: 开始时间 (格式: "HH:MM")
            end_time: 结束时间 (格式: "HH:MM")
            is_enabled: 是否启用 (默认True)

        返回:
            bool: 操作是否成功
        """
        try:
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO curfew_settings (group_id, start_time, end_time, is_enabled)
                VALUES (?, ?, ?, ?)
                """,
                (group_id, start_time, end_time, int(is_enabled)),
            )
            self.conn.commit()
            return True
        except Exception as e:
            return False

    def get_curfew_settings(self, group_id):
        """
        获取群宵禁配置

        参数:
            group_id: 群号

        返回:
            tuple: (start_time, end_time, is_enabled) 或 None
        """
        self.cursor.execute(
            "SELECT start_time, end_time, is_enabled FROM curfew_settings WHERE group_id=?",
            (group_id,),
        )
        result = self.cursor.fetchone()

        if result:
            return (result[0], result[1], bool(result[2]))
        return None

    def toggle_curfew_status(self, group_id):
        """
        切换群宵禁开关状态

        参数:
            group_id: 群号

        返回:
            bool: 切换后的状态，如果群不存在宵禁设置则返回None
        """
        # 先获取当前状态
        current_settings = self.get_curfew_settings(group_id)
        if current_settings is None:
            return None

        # 切换状态
        new_status = not current_settings[2]
        self.cursor.execute(
            "UPDATE curfew_settings SET is_enabled=? WHERE group_id=?",
            (int(new_status), group_id),
        )
        self.conn.commit()
        return new_status

    def delete_curfew_settings(self, group_id):
        """
        删除群宵禁配置

        参数:
            group_id: 群号

        返回:
            bool: 操作是否成功
        """
        try:
            self.cursor.execute(
                "DELETE FROM curfew_settings WHERE group_id=?", (group_id,)
            )
            self.conn.commit()
            return True
        except Exception as e:
            return False

    def is_curfew_time(self, group_id):
        """
        检查当前时间是否在宵禁时间内

        参数:
            group_id: 群号

        返回:
            bool: 是否在宵禁时间内
        """
        settings = self.get_curfew_settings(group_id)
        if not settings or not settings[2]:  # 如果没有设置或未启用
            return False

        start_time, end_time, is_enabled = settings
        current_time = datetime.datetime.now().strftime("%H:%M")

        # 处理跨日情况（如23:00-06:00）
        if start_time <= end_time:
            # 不跨日情况（如08:00-22:00）
            return start_time <= current_time <= end_time
        else:
            # 跨日情况（如23:00-06:00）
            return current_time >= start_time or current_time <= end_time

    def get_all_enabled_curfew_groups(self):
        """
        获取所有启用宵禁的群设置

        返回:
            list: [(group_id, start_time, end_time)] 列表
        """
        self.cursor.execute(
            "SELECT group_id, start_time, end_time FROM curfew_settings WHERE is_enabled = 1"
        )
        return self.cursor.fetchall()

    def should_trigger_curfew_action(self, group_id, current_time_str):
        """
        检查是否应该触发宵禁动作（开始或结束）

        参数:
            group_id: 群号
            current_time_str: 当前时间字符串 (格式: "HH:MM")

        返回:
            str: "start" 表示开始宵禁, "end" 表示结束宵禁, None 表示无需操作
        """
        settings = self.get_curfew_settings(group_id)
        if not settings or not settings[2]:  # 如果没有设置或未启用
            return None

        start_time, end_time, is_enabled = settings

        if current_time_str == start_time:
            return "start"
        elif current_time_str == end_time:
            return "end"

        return None

    def get_last_curfew_trigger_time(self, group_id):
        """
        获取群最后一次宵禁触发时间

        参数:
            group_id: 群号

        返回:
            str: 最后触发时间 (格式: "YYYY-MM-DD HH:MM") 或 None
        """
        self.cursor.execute(
            "SELECT last_trigger_time FROM curfew_trigger_log WHERE group_id=?",
            (group_id,),
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def update_curfew_trigger_time(self, group_id, trigger_time):
        """
        更新群宵禁触发时间记录

        参数:
            group_id: 群号
            trigger_time: 触发时间 (格式: "YYYY-MM-DD HH:MM")
        """
        self.cursor.execute(
            """
            INSERT OR REPLACE INTO curfew_trigger_log (group_id, last_trigger_time)
            VALUES (?, ?)
            """,
            (group_id, trigger_time),
        )
        self.conn.commit()

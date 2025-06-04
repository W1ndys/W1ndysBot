import sqlite3
import os
from . import MODULE_NAME, STATUS_UNVERIFIED, WARNING_COUNT


class DataManager:
    def __init__(self):
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"data.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """
        建表函数，如果表不存在则创建
        列：
        group_id: 群号 字符串
        user_id: 用户ID 字符串
        code: 验证码 字符串
        status: 验证状态 字符串
        created_at: 创建时间（字符串格式，建议为'YYYY-MM-DD HH:MM:SS'）
        warning_count: 剩余警告次数 整数
        要求：群号和QQ号两者无重复（即二者联合唯一）
        """
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS data_table (
            group_id TEXT,
            user_id TEXT,
            code TEXT,
            status TEXT,
            created_at TEXT,  -- 存储为字符串格式的时间，如'2024-06-01 12:00:00'
            warning_count INTEGER,  -- 剩余警告次数
            UNIQUE(group_id, user_id)
            )"""
        )
        # 检查 warning_count 列是否存在，不存在则添加（用于老库升级）
        self.cursor.execute("PRAGMA table_info(data_table)")
        columns = [row[1] for row in self.cursor.fetchall()]
        if "warning_count" not in columns:
            self.cursor.execute(
                "ALTER TABLE data_table ADD COLUMN warning_count INTEGER DEFAULT ?",
                (WARNING_COUNT,),
            )
            self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def add_data(
        self, group_id, user_id, code, status, created_at, warning_count=WARNING_COUNT
    ):
        """
        增加一条数据，如果已存在则更新
        :param group_id: 群号
        :param user_id: QQ号
        :param code: 验证码
        :param status: 验证状态
        :param created_at: 创建时间（字符串格式）
        :param warning_count: 剩余警告次数
        """
        self.cursor.execute(
            """
            INSERT INTO data_table (group_id, user_id, code, status, created_at, warning_count)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(group_id, user_id) DO UPDATE SET
                code=excluded.code,
                status=excluded.status,
                created_at=excluded.created_at,
                warning_count=excluded.warning_count
            """,
            (group_id, user_id, code, status, created_at, warning_count),
        )
        self.conn.commit()

    def get_data(self, group_id, user_id):
        """
        根据群号和QQ号获取一条数据
        :param group_id: 群号
        :param user_id: QQ号
        :return: 数据字典或None
        """
        self.cursor.execute(
            "SELECT group_id, user_id, code, status, created_at, warning_count FROM data_table WHERE group_id=? AND user_id=?",
            (group_id, user_id),
        )
        row = self.cursor.fetchone()
        if row:
            return {
                "group_id": row[0],
                "user_id": row[1],
                "code": row[2],
                "status": row[3],
                "created_at": row[4],
                "warning_count": row[5],
            }
        else:
            return None

    def get_code_with_group_and_user(self, group_id, user_id):
        """
        根据群号和QQ号获取对应的验证码，且验证状态必须为待验证
        :param group_id: 群号
        :param user_id: QQ号
        :return: 验证码字符串或None
        """
        self.cursor.execute(
            "SELECT code FROM data_table WHERE group_id=? AND user_id=? AND status=?",
            (group_id, user_id, STATUS_UNVERIFIED),
        )
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def get_group_with_code_and_user(self, user_id, code):
        """
        根据用户ID和验证码获取未验证的群号
        :param user_id: QQ号
        :param code: 验证码
        :return: 群号字符串或None
        """
        self.cursor.execute(
            "SELECT group_id FROM data_table WHERE user_id=? AND code=? AND status=?",
            (user_id, code, STATUS_UNVERIFIED),
        )
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def update_status(self, group_id, user_id, new_status):
        """
        更新验证状态
        :param group_id: 群号
        :param user_id: QQ号
        :param new_status: 新的验证状态
        """
        self.cursor.execute(
            "UPDATE data_table SET status=? WHERE group_id=? AND user_id=?",
            (new_status, group_id, user_id),
        )
        self.conn.commit()

    def get_warning_count(self, group_id, user_id):
        """
        获取指定用户的剩余警告次数
        :param group_id: 群号
        :param user_id: QQ号
        :return: 剩余警告次数（int）或 None
        """
        self.cursor.execute(
            "SELECT warning_count FROM data_table WHERE group_id=? AND user_id=?",
            (group_id, user_id),
        )
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def update_warning_count(self, group_id, user_id, new_count):
        """
        更新指定用户的剩余警告次数
        :param group_id: 群号
        :param user_id: QQ号
        :param new_count: 新的剩余警告次数
        """
        self.cursor.execute(
            "UPDATE data_table SET warning_count=? WHERE group_id=? AND user_id=?",
            (new_count, group_id, user_id),
        )
        self.conn.commit()

    def get_all_unverified_users_with_code_and_warning(self):
        """
        获取所有未验证的用户，按群号分类返回，并包含用户的验证码和剩余警告次数
        :return: {group_id: [(user_id, warning_count, code), ...], ...}
        """
        self.cursor.execute(
            "SELECT group_id, user_id, warning_count, code FROM data_table WHERE status=?",
            (STATUS_UNVERIFIED,),
        )
        rows = self.cursor.fetchall()
        result = {}
        for group_id, user_id, warning_count, code in rows:
            result.setdefault(group_id, []).append((user_id, warning_count, code))
        return result

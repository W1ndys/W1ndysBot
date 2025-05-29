import sqlite3
import os
from . import MODULE_NAME, MAX_ATTEMPTS, MAX_WARNINGS


class DataManager:
    def __init__(
        self, group_id
    ):  #  这里以群聊为例，如果需要处理私聊，可以传入user_id或其他实现方法
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"group_human_verification.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """
        建表函数，如果表不存在则创建
        group_id: 群聊ID
        qq_id: 用户QQ号
        unique_id: 唯一ID(验证码)
        verify_status: 验证状态
        join_time: 入群时间
        remaining_attempts: 剩余验证次数
        remaining_warnings: 剩余警告次数
        created_at: 创建时间
        """
        self.cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS group_human_verification (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id TEXT,
                qq_id TEXT,
                unique_id TEXT,
                verify_status TEXT DEFAULT '未验证',
                join_time INTEGER,
                remaining_attempts INTEGER DEFAULT {MAX_ATTEMPTS},
                remaining_warnings INTEGER DEFAULT {MAX_WARNINGS},
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"""
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def get_max_id(self):
        """获取当前最大ID"""
        self.cursor.execute("SELECT MAX(id) FROM group_human_verification")
        return self.cursor.fetchone()[0]

    def check_unique_id_exists(self, unique_id):
        """检查唯一ID是否存在"""
        self.cursor.execute(
            "SELECT COUNT(*) FROM group_human_verification WHERE unique_id = ?",
            (unique_id,),
        )
        return self.cursor.fetchone()[0] > 0

    def update_verify_status(self, unique_id, verify_status):
        """更新验证状态"""
        self.cursor.execute(
            "UPDATE group_human_verification SET verify_status = ? WHERE unique_id = ?",
            (verify_status, unique_id),
        )
        self.conn.commit()

    def insert_data(
        self,
        group_id,
        qq_id,
        unique_id,
        verify_status,
        join_time,
        remaining_attempts,
        remaining_warnings,
    ):
        """
        插入数据
        group_id: 群聊ID
        qq_id: 用户QQ号
        unique_id: 唯一ID
        verify_status: 验证状态
        join_time: 入群时间
        remaining_attempts: 剩余验证次数
        remaining_warnings: 剩余警告次数
        """
        self.cursor.execute(
            "INSERT INTO group_human_verification (group_id, qq_id, unique_id, verify_status, join_time, remaining_attempts, remaining_warnings) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                group_id,
                qq_id,
                unique_id,
                verify_status,
                join_time,
                remaining_attempts,
                remaining_warnings,
            ),
        )
        self.conn.commit()

    def get_record_by_unique_id(self, unique_id):
        """通过unique_id获取一条验证记录"""
        self.cursor.execute(
            "SELECT * FROM group_human_verification WHERE unique_id = ?",
            (unique_id,),
        )
        return self.cursor.fetchone()

    def get_unverified_users(self, group_id=None):
        """
        获取所有未验证用户
        group_id: 指定群号，若为None则获取所有群的未验证用户
        返回：list，每个元素为一条记录
        """
        if group_id:
            self.cursor.execute(
                "SELECT * FROM group_human_verification WHERE group_id = ? AND verify_status = '未验证'",
                (group_id,),
            )
        else:
            self.cursor.execute(
                "SELECT * FROM group_human_verification WHERE verify_status = '未验证'"
            )
        return self.cursor.fetchall()

    def update_warning_count(self, unique_id, new_count):
        """
        更新剩余警告次数
        """
        self.cursor.execute(
            "UPDATE group_human_verification SET remaining_warnings = ? WHERE unique_id = ?",
            (new_count, unique_id),
        )
        self.conn.commit()

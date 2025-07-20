import sqlite3
import os
from .. import MODULE_NAME


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
            """CREATE TABLE IF NOT EXISTS message_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_sender_id INTEGER NOT NULL,
            original_message_id INTEGER NOT NULL,
            forwarded_message_id INTEGER UNIQUE,   
            raw_message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )"""
        )
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def add_original_message(
        self, original_sender_id, original_message_id, raw_message
    ):
        """先存储原始消息ID和原始消息内容"""
        try:
            from datetime import datetime

            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                "INSERT INTO message_mapping (original_sender_id, original_message_id, forwarded_message_id, raw_message, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    original_sender_id,
                    original_message_id,
                    None,
                    raw_message,
                    created_at,
                ),
            )
            self.conn.commit()
            print(
                f"[{MODULE_NAME}]已添加原始消息：发送者ID={original_sender_id}, 原始消息ID={original_message_id}, 原始消息内容={raw_message}"
            )
            return True
        except sqlite3.IntegrityError:
            # 如果原始消息ID已存在，返回False
            print(f"[{MODULE_NAME}]原始消息ID已存在：{original_message_id}")
            return False

    def update_forwarded_message_id(self, original_message_id, forwarded_message_id):
        """更新对应的转发消息ID"""

        self.cursor.execute(
            "UPDATE message_mapping SET forwarded_message_id = ? WHERE original_message_id = ?",
            (forwarded_message_id, original_message_id),
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def add_message_mapping(
        self, original_sender_id, original_message_id, forwarded_message_id
    ):
        """添加消息映射关系（转发完成后调用）"""
        try:
            from datetime import datetime

            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                "INSERT INTO message_mapping (original_sender_id, original_message_id, forwarded_message_id, created_at) VALUES (?, ?, ?, ?)",
                (
                    original_sender_id,
                    original_message_id,
                    forwarded_message_id,
                    created_at,
                ),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # 如果映射关系已存在，返回False
            return False

    def get_original_message_id(self, forwarded_message_id):
        """根据转发后的消息ID获取原始消息ID（核心功能）"""
        self.cursor.execute(
            "SELECT original_message_id FROM message_mapping WHERE forwarded_message_id = ?",
            (forwarded_message_id,),
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_original_sender_id(self, forwarded_message_id):
        """根据转发后的消息ID获取原始发送者ID"""
        self.cursor.execute(
            "SELECT original_sender_id FROM message_mapping WHERE forwarded_message_id = ?",
            (forwarded_message_id,),
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_original_message_info(self, forwarded_message_id):
        """根据转发后的消息ID获取原始消息的完整信息"""
        self.cursor.execute(
            "SELECT original_sender_id, original_message_id FROM message_mapping WHERE forwarded_message_id = ?",
            (forwarded_message_id,),
        )
        result = self.cursor.fetchone()
        if result:
            return {"original_sender_id": result[0], "original_message_id": result[1]}
        return None

    def get_forwarded_message_id(self, original_message_id):
        """根据原始消息ID获取转发后的消息ID"""
        self.cursor.execute(
            "SELECT forwarded_message_id FROM message_mapping WHERE original_message_id = ?",
            (original_message_id,),
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def delete_message_mapping(
        self, original_message_id=None, forwarded_message_id=None
    ):
        """删除消息映射关系"""
        if original_message_id:
            self.cursor.execute(
                "DELETE FROM message_mapping WHERE original_message_id = ?",
                (original_message_id,),
            )
        elif forwarded_message_id:
            self.cursor.execute(
                "DELETE FROM message_mapping WHERE forwarded_message_id = ?",
                (forwarded_message_id,),
            )
        self.conn.commit()

    def get_all_mappings(self):
        """获取所有消息映射关系"""
        self.cursor.execute(
            "SELECT original_message_id, forwarded_message_id, created_at FROM message_mapping"
        )
        return self.cursor.fetchall()

    def get_pending_messages(self):
        """获取所有还未转发的消息（forwarded_message_id为NULL的记录）"""
        self.cursor.execute(
            "SELECT original_message_id, created_at FROM message_mapping WHERE forwarded_message_id IS NULL"
        )
        return self.cursor.fetchall()

    def is_message_forwarded(self, original_message_id):
        """检查消息是否已经转发"""
        self.cursor.execute(
            "SELECT forwarded_message_id FROM message_mapping WHERE original_message_id = ? AND forwarded_message_id IS NOT NULL",
            (original_message_id,),
        )
        return self.cursor.fetchone() is not None

    def get_sender_messages(self, original_sender_id, limit=10):
        """获取指定发送者的最近消息记录"""
        self.cursor.execute(
            "SELECT original_sender_id, original_message_id, forwarded_message_id, created_at FROM message_mapping WHERE original_sender_id = ? ORDER BY created_at DESC LIMIT ?",
            (original_sender_id, limit),
        )
        return self.cursor.fetchall()

    def cleanup_old_mappings(self, days=30):
        """清理超过指定天数的旧映射记录"""
        from datetime import datetime, timedelta

        cutoff_date = (datetime.now() - timedelta(days=days)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.cursor.execute(
            "DELETE FROM message_mapping WHERE created_at < ?", (cutoff_date,)
        )
        self.conn.commit()
        return self.cursor.rowcount

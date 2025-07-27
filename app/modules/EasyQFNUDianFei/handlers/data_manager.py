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
            """
            CREATE TABLE IF NOT EXISTS user_openid_mapping (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                openid TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id)
            )
        """
        )
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def add_user_openid(self, user_id, openid):
        """添加用户ID和openid的映射关系"""
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO user_openid_mapping (user_id, openid) VALUES (?, ?)",
                (user_id, openid),
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"添加用户openid映射失败: {e}")
            return False

    def get_openid_by_user_id(self, user_id):
        """根据用户ID获取openid"""
        self.cursor.execute(
            "SELECT openid FROM user_openid_mapping WHERE user_id = ?", (user_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_user_id_by_openid(self, openid):
        """根据openid获取用户ID"""
        self.cursor.execute(
            "SELECT user_id FROM user_openid_mapping WHERE openid = ?", (openid,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_all_mappings(self):
        """获取所有用户ID和openid的映射关系"""
        self.cursor.execute(
            "SELECT id, user_id, openid, created_at FROM user_openid_mapping ORDER BY id"
        )
        return self.cursor.fetchall()

    def delete_mapping_by_user_id(self, user_id):
        """根据用户ID删除映射关系"""
        try:
            self.cursor.execute(
                "DELETE FROM user_openid_mapping WHERE user_id = ?", (user_id,)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"删除用户openid映射失败: {e}")
            return False

    def update_openid(self, user_id, new_openid):
        """更新用户的openid"""
        try:
            self.cursor.execute(
                "UPDATE user_openid_mapping SET openid = ? WHERE user_id = ?",
                (new_openid, user_id),
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"更新用户openid失败: {e}")
            return False

    def check_user_exists(self, user_id):
        """检查用户是否已存在"""
        self.cursor.execute(
            "SELECT 1 FROM user_openid_mapping WHERE user_id = ?", (user_id,)
        )
        return self.cursor.fetchone() is not None

import sqlite3
import os
from .. import MODULE_NAME
from .database.enable_groups import EnableGroupsDatabase


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
        try:
            with self.conn as conn:
                cursor = conn.cursor()

                # 创建授权群聊白名单表
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS enable_groups (
                        id           INTEGER PRIMARY KEY AUTOINCREMENT,
                        group_id     INTEGER UNIQUE NOT NULL,
                        is_active    INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1)),
                        created_at   TEXT
                    );
                """
                )

                conn.commit()
                return True
        except Exception:
            return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    # --------------------------------------------------------启用群相关操作---------------------------------------

    def add_enable_group(self, group_id) -> dict:
        """添加启用群"""
        with EnableGroupsDatabase() as enable_groups_db:
            return enable_groups_db.add_enable_group(group_id)

    def disable_enable_group(self, group_id) -> dict:
        """禁用启用群"""
        with EnableGroupsDatabase() as enable_groups_db:
            return enable_groups_db.disable_enable_group(group_id)

    def get_enable_group_list(self) -> dict:
        """获取启用群列表"""
        with EnableGroupsDatabase() as enable_groups_db:
            return enable_groups_db.get_enable_group_list()

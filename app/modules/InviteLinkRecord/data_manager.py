import os
import sqlite3
from . import DATA_DIR
import logger


class InviteLinkRecordDataManager:
    def __init__(self, msg):
        self.msg = msg
        self.group_id = self.msg.get("group_id")
        self.operator_id = self.msg.get("operator_id")
        self.invited_id = self.msg.get("user_id")
        self.invite_time = self.msg.get("time")
        self.db_path = os.path.join(DATA_DIR, self.group_id, "invite_link_record.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """
        创建邀请链接记录表，id为自增，group_id为群组id，operator_id为邀请者id，invited_id为被邀请者id，invite_time为邀请时间
        """
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS invite_link_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT,
            operator_id TEXT,
            invited_id TEXT,
            invite_time TEXT)"""
        )

    def add_invite_link_record(self):
        """
        添加邀请链接记录，成功返回True，失败返回False
        """
        try:
            self.cursor.execute(
                """INSERT INTO invite_link_record (group_id, operator_id, invited_id, invite_time) VALUES (?, ?, ?, ?)""",
                (self.group_id, self.operator_id, self.invited_id, self.invite_time),
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"添加邀请链接记录失败: {e}")
            return False

    def get_invited_users_by_operator(self, operator_id):
        """
        查询某个邀请者(operator_id)邀请的所有用户，返回被邀请者id列表
        """
        try:
            self.cursor.execute(
                """SELECT invited_id FROM invite_link_record WHERE operator_id = ? AND group_id = ?""",
                (operator_id, self.group_id)
            )
            rows = self.cursor.fetchall()
            # 返回被邀请者id的列表
            return [row[0] for row in rows]
        except Exception as e:
            logger.error(f"查询邀请者{operator_id}邀请的用户失败: {e}")
            return []
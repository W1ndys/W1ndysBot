import os
import sqlite3
from . import DATA_DIR
import logger


class InviteLinkRecordDataManager:
    def __init__(self, msg):
        self.msg = msg
        self.group_id = str(self.msg.get("group_id"))
        self.operator_id = str(self.msg.get("operator_id"))
        self.invited_id = str(self.msg.get("user_id"))
        self.invite_time = str(self.msg.get("time"))
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
        添加邀请链接记录，如果已存在相同群号、邀请者、被邀请者，则刷新邀请时间，其余不变。成功返回True，失败返回False
        """
        try:
            # 检查是否已存在相同记录
            self.cursor.execute(
                """SELECT id FROM invite_link_record WHERE group_id = ? AND operator_id = ? AND invited_id = ?""",
                (self.group_id, self.operator_id, self.invited_id),
            )
            row = self.cursor.fetchone()
            if row:
                # 已存在，更新invite_time
                self.cursor.execute(
                    """UPDATE invite_link_record SET invite_time = ? WHERE id = ?""",
                    (self.invite_time, row[0]),
                )
            else:
                # 不存在，插入新记录
                self.cursor.execute(
                    """INSERT INTO invite_link_record (group_id, operator_id, invited_id, invite_time) VALUES (?, ?, ?, ?)""",
                    (
                        self.group_id,
                        self.operator_id,
                        self.invited_id,
                        self.invite_time,
                    ),
                )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"添加或更新邀请链接记录失败: {e}")
            return False

    def get_all_invited_users_recursive(self, operator_id, visited=None):
        """
        递归查询某个邀请者(operator_id)及其所有下级邀请的用户，返回所有被邀请者id列表（去重）
        """
        if visited is None:
            visited = set()
        all_invited = []
        try:
            # 查询直接被邀请者
            self.cursor.execute(
                """SELECT invited_id FROM invite_link_record WHERE operator_id = ? AND group_id = ?""",
                (operator_id, self.group_id),
            )
            rows = self.cursor.fetchall()
            for row in rows:
                invited_id = row[0]
                if invited_id not in visited:
                    visited.add(invited_id)
                    all_invited.append(invited_id)
                    # 递归查找被邀请者邀请的人
                    all_invited.extend(
                        self.get_all_invited_users_recursive(invited_id, visited)
                    )
            return all_invited
        except Exception as e:
            logger.error(f"递归查询邀请者{operator_id}邀请的用户失败: {e}")
            return all_invited

    def get_invite_tree_str(
        self, operator_id, level=0, visited=None, is_last=True, prefix=""
    ):
        """
        递归生成邀请链的层级结构字符串，严格树状结构（无环、无重复、无"已出现"提示）
        """
        if visited is None:
            visited = set()
        result = ""
        # 构建前缀
        if level == 0:
            branch = ""
            new_prefix = ""
        else:
            branch = "`-- " if is_last else "|-- "
            new_prefix = prefix + ("    " if is_last else "|   ")
        # 跳过已出现节点（不输出任何内容）
        if operator_id in visited:
            return result
        visited.add(operator_id)
        result += f"{prefix}{branch}{operator_id}\n"
        try:
            self.cursor.execute(
                """SELECT invited_id FROM invite_link_record WHERE operator_id = ? AND group_id = ?""",
                (operator_id, self.group_id),
            )
            rows = self.cursor.fetchall()
            for idx, row in enumerate(rows):
                invited_id = row[0]
                last = idx == len(rows) - 1
                result += self.get_invite_tree_str(
                    invited_id, level + 1, visited, is_last=last, prefix=new_prefix
                )
        except Exception as e:
            logger.error(f"生成邀请链结构失败: {e}")
        return result

import os
import sqlite3
from . import DATA_DIR
import logger


class InviteLinkRecordDataManager:
    def __init__(self, websocket, msg):
        self.websocket = websocket
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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()

    def _create_table(self):
        """
        创建邀请树接记录表，id为自增，group_id为群组id，operator_id为邀请者id，invited_id为被邀请者id，invite_time为邀请时间
        """
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS invite_link_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT,
            operator_id TEXT,
            invited_id TEXT,
            invite_time TEXT)"""
        )
        self.conn.commit()

    def _close(self):
        """
        关闭数据库连接
        """
        self.conn.close()

    def add_invite_link_record(self):
        """
        添加邀请树接记录，如果已存在相同群号、邀请者、被邀请者，则刷新邀请时间，其余不变。成功返回True，失败返回False
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
            logger.info(
                f"已添加或更新群{self.group_id}，邀请者：{self.operator_id}，被邀请者：{self.invited_id} 的邀请记录"
            )
            return True
        except Exception as e:
            logger.error(f"添加或更新邀请树接记录失败: {e}")
            return False

    def get_invite_tree_str(
        self, operator_id, level=0, visited=None, is_last=True, prefix=""
    ):
        """
        递归生成邀请树的层级结构字符串，严格树状结构（无环、无重复、无"已出现"提示）
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
            return result
        except Exception as e:
            logger.error(f"生成邀请树结构失败: {e}")
            return ""

    def _get_all_related_users_and_root(self, user_id):
        """
        获取用户相关的所有用户和根节点
        返回: (related_users_set, root_id, chain_list)
        """
        related_users = set()
        related_users.add(user_id)  # 包含自身

        # 向上查找所有邀请者，构建链路
        chain = []
        current_id = user_id
        visited_up = set()
        while True:
            if current_id in visited_up:
                break  # 防止环
            visited_up.add(current_id)
            chain.append(current_id)
            self.cursor.execute(
                """SELECT operator_id FROM invite_link_record WHERE invited_id = ? AND group_id = ?""",
                (current_id, self.group_id),
            )
            row = self.cursor.fetchone()
            if row and row[0]:
                operator_id = row[0]
                related_users.add(operator_id)
                current_id = operator_id
            else:
                break

        chain = chain[::-1]  # 反转，root在前
        root_id = chain[0]

        # 向下查找所有被邀请者
        def find_down(inviter_id, visited_down):
            self.cursor.execute(
                """SELECT invited_id FROM invite_link_record WHERE operator_id = ? AND group_id = ?""",
                (inviter_id, self.group_id),
            )
            rows = self.cursor.fetchall()
            for row in rows:
                invited_id = row[0]
                if invited_id not in visited_down:
                    related_users.add(invited_id)
                    visited_down.add(invited_id)
                    find_down(invited_id, visited_down)

        find_down(user_id, set())

        return related_users, root_id, chain

    def get_full_invite_chain_str(self, user_id):
        """
        生成完整邀请树：先递归向上查找所有邀请者，找到最顶层root，再以root为起点递归向下生成树状结构。
        """
        related_users, root_id, chain = self._get_all_related_users_and_root(user_id)

        # 以root为起点，递归向下生成树状结构
        tree_str = self.get_invite_tree_str(root_id)

        # 标记目标user_id
        if user_id != root_id:
            tree_str = tree_str.replace(f"{user_id}\n", f"{user_id}  <--- 查询对象\n")

        # 展示链路
        chain_str = " -> ".join(chain)
        logger.info(f"已查询群{self.group_id}，{user_id} 的完整邀请树：{chain_str}")
        return f"邀请树路：{chain_str}\n\n{tree_str}"

    def get_related_invite_users(self, user_id):
        """
        返回被查询者的上级和下级所有相关邀请者，结果为去重后的id列表（包含自身）。
        上级：递归向上查找所有邀请者
        下级：递归向下查找所有被邀请者
        """
        related_users, _, _ = self._get_all_related_users_and_root(user_id)
        logger.info(
            f"已查询群{self.group_id}，{user_id} 的上下级相关邀请者：{related_users}"
        )
        return list(related_users)

    def delete_invite_record_by_invited_id(self, invited_id):
        """
        根据群号和被邀请者id删除所有相关邀请记录。
        """
        try:
            self.cursor.execute(
                """DELETE FROM invite_link_record WHERE group_id = ? AND invited_id = ?""",
                (self.group_id, invited_id),
            )
            self.conn.commit()
            logger.info(f"已删除群{self.group_id}，被邀请者：{invited_id} 的邀请记录")
            return True
        except Exception as e:
            logger.error(
                f"删除群{self.group_id}，被邀请者：{invited_id} 的邀请记录失败: {e}"
            )
            return False

    def delete_all_invite_records_by_user_id(self, user_id):
        """
        根据群号和用户id删除该用户相关的所有邀请记录（包括作为邀请者和被邀请者的记录）。
        """
        try:
            # 删除该用户作为被邀请者的记录
            self.cursor.execute(
                """DELETE FROM invite_link_record WHERE group_id = ? AND invited_id = ?""",
                (self.group_id, user_id),
            )
            # 删除该用户作为邀请者的记录
            self.cursor.execute(
                """DELETE FROM invite_link_record WHERE group_id = ? AND operator_id = ?""",
                (self.group_id, user_id),
            )
            self.conn.commit()
            logger.info(f"已删除群{self.group_id}，用户：{user_id} 的所有相关邀请记录")
            return True
        except Exception as e:
            logger.error(
                f"删除群{self.group_id}，用户：{user_id} 的所有相关邀请记录失败: {e}"
            )
            return False

    def get_invite_count(self, operator_id=None):
        """
        获取某个邀请者在本群邀请了多少人
        """
        if operator_id is None:
            operator_id = self.operator_id
        try:
            self.cursor.execute(
                """SELECT COUNT(*) FROM invite_link_record WHERE group_id = ? AND operator_id = ?""",
                (self.group_id, operator_id),
            )
            row = self.cursor.fetchone()
            return row[0] if row else 0
        except Exception as e:
            logger.error(f"统计邀请次数失败: {e}")
            return 0

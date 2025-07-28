from .database_base import DatabaseBase
from datetime import datetime


class InviteDataHandler(DatabaseBase):
    """邀请数据处理类"""

    def __init__(self, year=None):
        super().__init__(year)
        self._create_invite_data_table()

    def _create_invite_data_table(self):
        """创建邀请数据表 invite_data"""
        table_schema = """
            CREATE TABLE IF NOT EXISTS invite_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                operator_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                invite_time TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self.cursor.execute(table_schema)
        self.conn.commit()

    def add_invite_record(self, group_id, operator_id, user_id, invite_time=None):
        """添加邀请记录"""
        try:
            if invite_time is None:
                invite_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.cursor.execute(
                """
                INSERT INTO invite_data (group_id, operator_id, user_id, invite_time)
                VALUES (?, ?, ?, ?)
                """,
                (group_id, operator_id, user_id, invite_time),
            )
            self.conn.commit()

            # 获取刚插入的记录ID
            record_id = self.cursor.lastrowid

            return {
                "code": 200,
                "data": {
                    "id": record_id,
                    "group_id": group_id,
                    "operator_id": operator_id,
                    "user_id": user_id,
                    "invite_time": invite_time,
                },
                "message": "邀请记录添加成功",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"添加邀请记录失败: {str(e)}"}

    def get_invite_records_by_group(self, group_id, limit=50, offset=0):
        """获取群组的邀请记录"""
        try:
            query = """
                SELECT id, group_id, operator_id, user_id, invite_time, created_at
                FROM invite_data
                WHERE group_id = ?
                ORDER BY invite_time DESC
                LIMIT ? OFFSET ?
            """
            self.cursor.execute(query, (group_id, limit, offset))
            records = self.cursor.fetchall()

            return {
                "code": 200,
                "data": records,
                "message": f"获取群组 {group_id} 的邀请记录成功，共 {len(records)} 条",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"获取邀请记录失败: {str(e)}"}

    def get_invite_records_by_operator(self, group_id, operator_id, limit=50):
        """获取特定操作者的邀请记录"""
        try:
            query = """
                SELECT id, group_id, operator_id, user_id, invite_time, created_at
                FROM invite_data
                WHERE group_id = ? AND operator_id = ?
                ORDER BY invite_time DESC
                LIMIT ?
            """
            self.cursor.execute(query, (group_id, operator_id, limit))
            records = self.cursor.fetchall()

            return {
                "code": 200,
                "data": records,
                "message": f"获取操作者 {operator_id} 的邀请记录成功，共 {len(records)} 条",
            }
        except Exception as e:
            return {
                "code": 500,
                "data": None,
                "message": f"获取操作者邀请记录失败: {str(e)}",
            }

    def get_invite_records_by_user(self, group_id, user_id, limit=50):
        """获取特定用户被邀请的记录"""
        try:
            query = """
                SELECT id, group_id, operator_id, user_id, invite_time, created_at
                FROM invite_data
                WHERE group_id = ? AND user_id = ?
                ORDER BY invite_time DESC
                LIMIT ?
            """
            self.cursor.execute(query, (group_id, user_id, limit))
            records = self.cursor.fetchall()

            return {
                "code": 200,
                "data": records,
                "message": f"获取用户 {user_id} 被邀请记录成功，共 {len(records)} 条",
            }
        except Exception as e:
            return {
                "code": 500,
                "data": None,
                "message": f"获取用户被邀请记录失败: {str(e)}",
            }

    def get_operator_invite_stats(self, group_id, operator_id):
        """获取操作者的邀请统计信息"""
        try:
            # 获取总邀请次数
            total_query = """
                SELECT COUNT(*) as total_invites
                FROM invite_data
                WHERE group_id = ? AND operator_id = ?
            """
            self.cursor.execute(total_query, (group_id, operator_id))
            total_result = self.cursor.fetchone()
            total_invites = total_result[0] if total_result else 0

            # 获取今日邀请次数
            today = datetime.now().strftime("%Y-%m-%d")
            today_query = """
                SELECT COUNT(*) as today_invites
                FROM invite_data
                WHERE group_id = ? AND operator_id = ? AND DATE(invite_time) = ?
            """
            self.cursor.execute(today_query, (group_id, operator_id, today))
            today_result = self.cursor.fetchone()
            today_invites = today_result[0] if today_result else 0

            # 获取最近一次邀请时间
            latest_query = """
                SELECT invite_time
                FROM invite_data
                WHERE group_id = ? AND operator_id = ?
                ORDER BY invite_time DESC
                LIMIT 1
            """
            self.cursor.execute(latest_query, (group_id, operator_id))
            latest_result = self.cursor.fetchone()
            latest_invite_time = latest_result[0] if latest_result else None

            return {
                "code": 200,
                "data": {
                    "operator_id": operator_id,
                    "group_id": group_id,
                    "total_invites": total_invites,
                    "today_invites": today_invites,
                    "latest_invite_time": latest_invite_time,
                },
                "message": "获取操作者邀请统计成功",
            }
        except Exception as e:
            return {
                "code": 500,
                "data": None,
                "message": f"获取操作者邀请统计失败: {str(e)}",
            }

    def get_group_invite_stats(self, group_id):
        """获取群组邀请统计信息"""
        try:
            # 获取总邀请次数
            total_query = """
                SELECT COUNT(*) as total_invites
                FROM invite_data
                WHERE group_id = ?
            """
            self.cursor.execute(total_query, (group_id,))
            total_result = self.cursor.fetchone()
            total_invites = total_result[0] if total_result else 0

            # 获取今日邀请次数
            today = datetime.now().strftime("%Y-%m-%d")
            today_query = """
                SELECT COUNT(*) as today_invites
                FROM invite_data
                WHERE group_id = ? AND DATE(invite_time) = ?
            """
            self.cursor.execute(today_query, (group_id, today))
            today_result = self.cursor.fetchone()
            today_invites = today_result[0] if today_result else 0

            # 获取活跃邀请者数量
            operators_query = """
                SELECT COUNT(DISTINCT operator_id) as active_operators
                FROM invite_data
                WHERE group_id = ?
            """
            self.cursor.execute(operators_query, (group_id,))
            operators_result = self.cursor.fetchone()
            active_operators = operators_result[0] if operators_result else 0

            # 获取被邀请用户数量
            invited_users_query = """
                SELECT COUNT(DISTINCT user_id) as invited_users
                FROM invite_data
                WHERE group_id = ?
            """
            self.cursor.execute(invited_users_query, (group_id,))
            invited_users_result = self.cursor.fetchone()
            invited_users = invited_users_result[0] if invited_users_result else 0

            return {
                "code": 200,
                "data": {
                    "group_id": group_id,
                    "total_invites": total_invites,
                    "today_invites": today_invites,
                    "active_operators": active_operators,
                    "invited_users": invited_users,
                },
                "message": "获取群组邀请统计成功",
            }
        except Exception as e:
            return {
                "code": 500,
                "data": None,
                "message": f"获取群组邀请统计失败: {str(e)}",
            }

    def get_top_inviters(self, group_id, limit=10):
        """获取群组内邀请次数最多的用户排行榜"""
        try:
            query = """
                SELECT operator_id, COUNT(*) as invite_count, 
                       MIN(invite_time) as first_invite_time,
                       MAX(invite_time) as latest_invite_time
                FROM invite_data
                WHERE group_id = ?
                GROUP BY operator_id
                ORDER BY invite_count DESC
                LIMIT ?
            """
            self.cursor.execute(query, (group_id, limit))
            records = self.cursor.fetchall()

            return {
                "code": 200,
                "data": records,
                "message": f"获取群组 {group_id} 邀请排行榜成功，共 {len(records)} 位用户",
            }
        except Exception as e:
            return {
                "code": 500,
                "data": None,
                "message": f"获取邀请排行榜失败: {str(e)}",
            }

    def delete_invite_record(self, record_id):
        """删除指定的邀请记录"""
        try:
            # 先检查记录是否存在
            check_query = "SELECT id FROM invite_data WHERE id = ?"
            self.cursor.execute(check_query, (record_id,))
            if not self.cursor.fetchone():
                return {
                    "code": 404,
                    "data": None,
                    "message": f"邀请记录 {record_id} 不存在",
                }

            # 删除记录
            delete_query = "DELETE FROM invite_data WHERE id = ?"
            self.cursor.execute(delete_query, (record_id,))
            self.conn.commit()

            return {
                "code": 200,
                "data": {"deleted_id": record_id},
                "message": f"邀请记录 {record_id} 删除成功",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"删除邀请记录失败: {str(e)}"}

    def delete_user_invite_records(self, group_id, user_id):
        """删除特定用户的所有邀请相关记录（作为操作者和被邀请者的记录）"""
        try:
            # 统计要删除的记录数
            count_query = """
                SELECT COUNT(*) FROM invite_data 
                WHERE group_id = ? AND (operator_id = ? OR user_id = ?)
            """
            self.cursor.execute(count_query, (group_id, user_id, user_id))
            count_result = self.cursor.fetchone()
            delete_count = count_result[0] if count_result else 0

            if delete_count == 0:
                return {
                    "code": 404,
                    "data": None,
                    "message": f"用户 {user_id} 在群组 {group_id} 中没有邀请相关记录",
                }

            # 删除记录
            delete_query = """
                DELETE FROM invite_data 
                WHERE group_id = ? AND (operator_id = ? OR user_id = ?)
            """
            self.cursor.execute(delete_query, (group_id, user_id, user_id))
            self.conn.commit()

            return {
                "code": 200,
                "data": {"deleted_count": delete_count},
                "message": f"删除用户 {user_id} 的邀请记录成功，共删除 {delete_count} 条记录",
            }
        except Exception as e:
            return {
                "code": 500,
                "data": None,
                "message": f"删除用户邀请记录失败: {str(e)}",
            }

    def delete_group_invite_records(self, group_id):
        """删除群组的所有邀请记录"""
        try:
            # 统计要删除的记录数
            count_query = "SELECT COUNT(*) FROM invite_data WHERE group_id = ?"
            self.cursor.execute(count_query, (group_id,))
            count_result = self.cursor.fetchone()
            delete_count = count_result[0] if count_result else 0

            if delete_count == 0:
                return {
                    "code": 404,
                    "data": None,
                    "message": f"群组 {group_id} 没有邀请记录",
                }

            # 删除记录
            delete_query = "DELETE FROM invite_data WHERE group_id = ?"
            self.cursor.execute(delete_query, (group_id,))
            self.conn.commit()

            return {
                "code": 200,
                "data": {"deleted_count": delete_count},
                "message": f"删除群组 {group_id} 的邀请记录成功，共删除 {delete_count} 条记录",
            }
        except Exception as e:
            return {
                "code": 500,
                "data": None,
                "message": f"删除群组邀请记录失败: {str(e)}",
            }


# 测试代码
if __name__ == "__main__":
    import os

    # 测试邀请数据处理器
    with InviteDataHandler() as handler:
        print("=" * 70)
        print("测试邀请记录管理类")
        print("=" * 70)

        # 测试添加邀请记录
        print("\n1. 测试添加邀请记录:")
        result1 = handler.add_invite_record(123456, 111111, 222222)
        print("添加邀请记录1:", result1["message"])

        result2 = handler.add_invite_record(123456, 111111, 333333)
        print("添加邀请记录2:", result2["message"])

        result3 = handler.add_invite_record(123456, 444444, 555555)
        print("添加邀请记录3:", result3["message"])

        # 测试获取群组邀请记录
        print("\n2. 测试获取群组邀请记录:")
        records_result = handler.get_invite_records_by_group(123456)
        print("群组邀请记录:", records_result["message"])
        if records_result["code"] == 200:
            for record in records_result["data"]:
                print(
                    f"  ID:{record[0]} 操作者:{record[2]} 邀请:{record[3]} 时间:{record[4]}"
                )

        # 测试获取操作者邀请记录
        print("\n3. 测试获取操作者邀请记录:")
        operator_records = handler.get_invite_records_by_operator(123456, 111111)
        print("操作者邀请记录:", operator_records["message"])

        # 测试获取操作者邀请统计
        print("\n4. 测试获取操作者邀请统计:")
        operator_stats = handler.get_operator_invite_stats(123456, 111111)
        if operator_stats["code"] == 200:
            stats = operator_stats["data"]
            print(
                f"操作者统计: 总邀请{stats['total_invites']}次，今日{stats['today_invites']}次"
            )

        # 测试获取群组邀请统计
        print("\n5. 测试获取群组邀请统计:")
        group_stats = handler.get_group_invite_stats(123456)
        if group_stats["code"] == 200:
            stats = group_stats["data"]
            print(
                f"群组统计: 总邀请{stats['total_invites']}次，活跃邀请者{stats['active_operators']}人"
            )

        # 测试获取邀请排行榜
        print("\n6. 测试获取邀请排行榜:")
        top_inviters = handler.get_top_inviters(123456)
        if top_inviters["code"] == 200:
            print("邀请排行榜:")
            for i, record in enumerate(top_inviters["data"], 1):
                print(f"  {i}. 用户{record[0]}: {record[1]}次邀请")

        print("\n" + "=" * 70)
        print("邀请记录管理类测试完成")
        print("=" * 70)

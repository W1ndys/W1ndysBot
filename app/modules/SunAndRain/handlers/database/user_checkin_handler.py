from .database_base import DatabaseBase


class UserCheckinHandler(DatabaseBase):
    """用户签到信息表处理类"""

    def __init__(self, year=None):
        super().__init__(year)
        self._create_user_checkin_table()

    def _create_user_checkin_table(self):
        """创建用户基本信息表 user_checkin"""
        table_schema = """
            CREATE TABLE IF NOT EXISTS user_checkin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                type INTEGER DEFAULT 0,
                count INTEGER DEFAULT 0,
                consecutive_days INTEGER DEFAULT 0,
                last_checkin_date TEXT DEFAULT '',
                total_checkin_days INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(group_id, user_id, type)
            )
        """
        self.create_table("user_checkin", table_schema)

    def add_user(self, group_id, user_id, user_type=0):
        """添加新用户记录 - 用户只能选择阳光或雨露中的一个"""
        try:
            current_time = self.get_current_time()
            type_name = self.get_type_name(user_type)

            # 首先检查用户是否已经选择过任何类型
            existing_user_info = self.get_user_info(group_id, user_id)

            if existing_user_info["code"] == 200 and existing_user_info["data"]:
                # 用户已经选择过类型
                existing_user_data = existing_user_info["data"][0]
                existing_type = existing_user_data[3]  # type字段
                existing_type_name = self.get_type_name(existing_type)
                existing_count = existing_user_data[4]  # count字段

                if existing_type == user_type:
                    # 重复选择同一类型
                    return {
                        "code": 409,
                        "data": None,
                        "message": f"⚠️ 您已经选择过{type_name}了！\n"
                        f"💎 当前拥有：{existing_count}个{type_name}\n"
                        f"📝 提示：每日可通过签到获得更多{type_name}！",
                    }
                else:
                    # 尝试选择不同的类型
                    return {
                        "code": 409,
                        "data": None,
                        "message": f"⚠️ 您已经选择了{existing_type_name}类型！\n"
                        f"💎 当前拥有：{existing_count}个{existing_type_name}\n"
                        f"❌ 无法更换为{type_name}类型\n"
                        f"📝 每个用户只能选择一种类型（阳光或雨露）",
                    }

            # 用户还没有选择过类型，可以添加新记录
            query = """
                INSERT INTO user_checkin (group_id, user_id, type, count, created_at, updated_at)
                VALUES (?, ?, ?, 0, ?, ?)
            """
            self.execute_update(
                query, (group_id, user_id, user_type, current_time, current_time)
            )

            return {
                "code": 200,
                "data": {
                    "group_id": group_id,
                    "user_id": user_id,
                    "type": user_type,
                    "type_name": type_name,
                    "count": 0,
                    "selected_time": current_time,
                },
                "message": f"🌟 选择成功！\n"
                f"✨ 您选择了：{type_name}\n"
                f"💎 当前拥有：0个{type_name}\n"
                f"⏰ 选择时间：{current_time}\n"
                f"📝 提示：每日可通过签到获得{type_name}奖励哦！\n"
                f"⚠️ 注意：选择后无法更改类型",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"❌ 数据库错误: {str(e)}"}

    def get_user_info(self, group_id, user_id, user_type=None):
        """获取用户信息"""
        try:
            if user_type is not None:
                query = """
                    SELECT * FROM user_checkin 
                    WHERE group_id = ? AND user_id = ? AND type = ?
                """
                results = self.execute_query(query, (group_id, user_id, user_type))
            else:
                query = """
                    SELECT * FROM user_checkin 
                    WHERE group_id = ? AND user_id = ?
                """
                results = self.execute_query(query, (group_id, user_id))

            if results:
                return {"code": 200, "data": results, "message": "获取用户信息成功"}
            else:
                return {"code": 404, "data": None, "message": "用户信息不存在"}
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def update_user_count(self, group_id, user_id, user_type, increment=1):
        """更新用户的数值"""
        try:
            # 首先检查用户是否存在
            user_info = self.get_user_info(group_id, user_id, user_type)
            if user_info["code"] != 200:
                return {
                    "code": 404,
                    "data": None,
                    "message": "用户不存在，请先选择阳光或雨露",
                }

            current_time = self.get_current_time()
            query = """
                UPDATE user_checkin 
                SET count = count + ?, updated_at = ?
                WHERE group_id = ? AND user_id = ? AND type = ?
            """
            rowcount = self.execute_update(
                query, (increment, current_time, group_id, user_id, user_type)
            )

            if rowcount > 0:
                # 获取更新后的数值
                new_count = self.get_user_count(group_id, user_id, user_type)
                return {
                    "code": 200,
                    "data": {
                        "group_id": group_id,
                        "user_id": user_id,
                        "type": user_type,
                        "count": new_count["data"],
                        "increment": increment,
                    },
                    "message": "更新用户数值成功",
                }
            else:
                return {"code": 404, "data": None, "message": "更新失败，用户不存在"}
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_user_count(self, group_id, user_id, user_type):
        """获取用户特定类型的数值"""
        try:
            query = """
                SELECT count FROM user_checkin 
                WHERE group_id = ? AND user_id = ? AND type = ?
            """
            results = self.execute_query(query, (group_id, user_id, user_type))

            if results:
                return {
                    "code": 200,
                    "data": results[0][0],
                    "message": "获取用户数值成功",
                }
            else:
                return {"code": 404, "data": 0, "message": "用户不存在"}
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_group_ranking(self, group_id, user_type, limit=10):
        """获取群组内指定类型的排行榜"""
        try:
            query = """
                SELECT user_id, count FROM user_checkin 
                WHERE group_id = ? AND type = ?
                ORDER BY count DESC
                LIMIT ?
            """
            results = self.execute_query(query, (group_id, user_type, limit))

            return {
                "code": 200,
                "data": results,
                "message": f"获取排行榜成功，共{len(results)}条记录",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_all_group_users(self, group_id):
        """获取群组内所有用户的信息"""
        try:
            query = """
                SELECT user_id, type, count FROM user_checkin 
                WHERE group_id = ?
                ORDER BY user_id, type
            """
            results = self.execute_query(query, (group_id,))

            return {
                "code": 200,
                "data": results,
                "message": f"获取群组用户信息成功，共{len(results)}条记录",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def delete_user(self, group_id, user_id):
        """删除用户的基本信息记录"""
        try:
            query = """
                DELETE FROM user_checkin 
                WHERE group_id = ? AND user_id = ?
            """
            user_deleted = self.execute_update(query, (group_id, user_id))

            return {
                "code": 200,
                "data": {"user_records": user_deleted},
                "message": f"删除用户基本信息成功，删除了{user_deleted}条记录",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def reset_group_data(self, group_id):
        """重置群组的所有用户数据"""
        try:
            query = "DELETE FROM user_checkin WHERE group_id = ?"
            deleted_count = self.execute_update(query, (group_id,))

            return {
                "code": 200,
                "data": {"deleted_count": deleted_count},
                "message": f"重置群组数据成功，删除了{deleted_count}条记录",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_total_stats(self, group_id):
        """获取群组的统计信息"""
        try:
            query = """
                SELECT 
                    type,
                    COUNT(*) as user_count,
                    SUM(count) as total_count,
                    AVG(count) as avg_count
                FROM user_checkin 
                WHERE group_id = ?
                GROUP BY type
            """
            results = self.execute_query(query, (group_id,))

            return {"code": 200, "data": results, "message": "获取统计信息成功"}
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_user_checkin_stats(self, group_id, user_id, user_type=None):
        """获取用户签到统计信息"""
        try:
            if user_type is not None:
                query = """
                    SELECT consecutive_days, last_checkin_date, total_checkin_days, count
                    FROM user_checkin 
                    WHERE group_id = ? AND user_id = ? AND type = ?
                """
                results = self.execute_query(query, (group_id, user_id, user_type))
            else:
                query = """
                    SELECT type, consecutive_days, last_checkin_date, total_checkin_days, count
                    FROM user_checkin 
                    WHERE group_id = ? AND user_id = ?
                """
                results = self.execute_query(query, (group_id, user_id))

            if results:
                return {"code": 200, "data": results, "message": "获取签到统计成功"}
            else:
                return {"code": 404, "data": None, "message": "用户信息不存在"}
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_consecutive_ranking(self, group_id, user_type, limit=10):
        """获取连续签到天数排行榜"""
        try:
            query = """
                SELECT user_id, consecutive_days, total_checkin_days
                FROM user_checkin 
                WHERE group_id = ? AND type = ?
                ORDER BY consecutive_days DESC, total_checkin_days DESC
                LIMIT ?
            """
            results = self.execute_query(query, (group_id, user_type, limit))

            return {
                "code": 200,
                "data": results,
                "message": f"获取连续签到排行榜成功，共{len(results)}条记录",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def update_checkin_info(
        self,
        group_id,
        user_id,
        user_type,
        total_reward,
        consecutive_days,
        current_date,
        current_time,
    ):
        """更新用户的签到信息"""
        try:
            query = """
                UPDATE user_checkin 
                SET count = count + ?, 
                    consecutive_days = ?, 
                    last_checkin_date = ?,
                    total_checkin_days = total_checkin_days + 1,
                    updated_at = ?
                WHERE group_id = ? AND user_id = ? AND type = ?
            """
            rowcount = self.execute_update(
                query,
                (
                    total_reward,
                    consecutive_days,
                    current_date,
                    current_time,
                    group_id,
                    user_id,
                    user_type,
                ),
            )

            return rowcount > 0
        except Exception as e:
            raise Exception(f"更新签到信息失败: {str(e)}")

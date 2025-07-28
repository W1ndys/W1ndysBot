from .database_base import DatabaseBase
from ... import CONSECUTIVE_BONUS_CONFIG


class CheckinRecordsHandler(DatabaseBase):
    """签到记录表处理类"""

    def __init__(self, year=None):
        super().__init__(year)
        self._create_checkin_records_table()

    def _create_checkin_records_table(self):
        """创建签到记录表 checkin_records"""
        table_schema = """
            CREATE TABLE IF NOT EXISTS checkin_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                checkin_date TEXT NOT NULL,
                type INTEGER NOT NULL,
                reward_amount INTEGER DEFAULT 0,
                consecutive_days INTEGER DEFAULT 0,
                bonus_amount INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                UNIQUE(group_id, user_id, checkin_date, type)
            )
        """
        self.create_table("checkin_records", table_schema)

    def add_checkin_record(
        self,
        group_id,
        user_id,
        checkin_date,
        user_type,
        base_reward,
        consecutive_days,
        bonus_reward,
        current_time,
    ):
        """添加签到记录"""
        try:
            query = """
                INSERT INTO checkin_records 
                (group_id, user_id, checkin_date, type, reward_amount, consecutive_days, bonus_amount, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.execute_update(
                query,
                (
                    group_id,
                    user_id,
                    checkin_date,
                    user_type,
                    base_reward,
                    consecutive_days,
                    bonus_reward,
                    current_time,
                ),
            )
            return True
        except Exception as e:
            raise Exception(f"添加签到记录失败: {str(e)}")

    def check_today_checkin(self, group_id, user_id, current_date, user_type):
        """检查今日是否已签到"""
        try:
            query = """
                SELECT checkin_date, reward_amount, consecutive_days, bonus_amount, created_at 
                FROM checkin_records
                WHERE group_id = ? AND user_id = ? AND checkin_date = ? AND type = ?
            """
            results = self.execute_query(
                query, (group_id, user_id, current_date, user_type)
            )

            if results:
                return {"already_checked": True, "checkin_data": results[0]}
            else:
                return {"already_checked": False}
        except Exception:
            # 发生异常时返回默认值，不抛出异常
            return {"already_checked": False}

    def get_checkin_history(self, group_id, user_id, user_type, days=7):
        """获取用户签到历史记录"""
        try:
            query = """
                SELECT checkin_date, reward_amount, consecutive_days, bonus_amount
                FROM checkin_records 
                WHERE group_id = ? AND user_id = ? AND type = ?
                ORDER BY checkin_date DESC
                LIMIT ?
            """
            results = self.execute_query(query, (group_id, user_id, user_type, days))

            return {
                "code": 200,
                "data": results,
                "message": f"获取签到历史成功，共{len(results)}条记录",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def delete_user_records(self, group_id, user_id):
        """删除用户的所有签到记录"""
        try:
            query = """
                DELETE FROM checkin_records 
                WHERE group_id = ? AND user_id = ?
            """
            deleted_count = self.execute_update(query, (group_id, user_id))

            return {
                "code": 200,
                "data": {"checkin_records": deleted_count},
                "message": f"删除签到记录成功，删除了{deleted_count}条记录",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def reset_group_records(self, group_id):
        """重置群组的所有签到记录"""
        try:
            query = "DELETE FROM checkin_records WHERE group_id = ?"
            deleted_count = self.execute_update(query, (group_id,))

            return {
                "code": 200,
                "data": {"deleted_count": deleted_count},
                "message": f"重置群组签到记录成功，删除了{deleted_count}条记录",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_total_checkins_count(self, group_id):
        """获取群组总签到次数"""
        try:
            query = """
                SELECT COUNT(*) as total_checkins
                FROM checkin_records 
                WHERE group_id = ?
            """
            results = self.execute_query(query, (group_id,))

            return results[0][0] if results else 0
        except Exception as e:
            raise Exception(f"获取总签到次数失败: {str(e)}")

    def get_user_checkin_count(self, group_id, user_id, user_type=None):
        """获取用户总签到次数"""
        try:
            if user_type is not None:
                query = """
                    SELECT COUNT(*) as user_checkins
                    FROM checkin_records 
                    WHERE group_id = ? AND user_id = ? AND type = ?
                """
                results = self.execute_query(query, (group_id, user_id, user_type))
            else:
                query = """
                    SELECT COUNT(*) as user_checkins
                    FROM checkin_records 
                    WHERE group_id = ? AND user_id = ?
                """
                results = self.execute_query(query, (group_id, user_id))

            return results[0][0] if results else 0
        except Exception as e:
            raise Exception(f"获取用户签到次数失败: {str(e)}")

    def get_monthly_checkin_stats(self, group_id, user_id, user_type, year_month):
        """获取用户某月的签到统计"""
        try:
            query = """
                SELECT 
                    COUNT(*) as checkin_days,
                    SUM(reward_amount) as total_base_rewards,
                    SUM(bonus_amount) as total_bonus_rewards,
                    MAX(consecutive_days) as max_consecutive_days
                FROM checkin_records 
                WHERE group_id = ? AND user_id = ? AND type = ? 
                AND checkin_date LIKE ?
            """
            like_pattern = f"{year_month}-%"
            results = self.execute_query(
                query, (group_id, user_id, user_type, like_pattern)
            )

            return {
                "code": 200,
                "data": results[0] if results else (0, 0, 0, 0),
                "message": f"获取{year_month}月签到统计成功",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_group_checkin_calendar(self, group_id, user_type, year_month):
        """获取群组某月的签到日历（哪些日期有人签到）"""
        try:
            query = """
                SELECT DISTINCT checkin_date, COUNT(*) as checkin_count
                FROM checkin_records 
                WHERE group_id = ? AND type = ? AND checkin_date LIKE ?
                GROUP BY checkin_date
                ORDER BY checkin_date
            """
            like_pattern = f"{year_month}-%"
            results = self.execute_query(query, (group_id, user_type, like_pattern))

            return {
                "code": 200,
                "data": results,
                "message": f"获取{year_month}月签到日历成功",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_top_checkin_users(self, group_id, user_type, limit=10):
        """获取签到次数最多的用户排行榜"""
        try:
            query = """
                SELECT 
                    user_id, 
                    COUNT(*) as total_checkins,
                    SUM(reward_amount + bonus_amount) as total_rewards,
                    MAX(consecutive_days) as max_consecutive
                FROM checkin_records 
                WHERE group_id = ? AND type = ?
                GROUP BY user_id
                ORDER BY total_checkins DESC, total_rewards DESC
                LIMIT ?
            """
            results = self.execute_query(query, (group_id, user_type, limit))

            return {
                "code": 200,
                "data": results,
                "message": f"获取签到排行榜成功，共{len(results)}条记录",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_recent_checkins(self, group_id, user_type, days=7):
        """获取最近几天的签到记录"""
        try:
            query = """
                SELECT 
                    user_id, checkin_date, reward_amount, bonus_amount, consecutive_days
                FROM checkin_records 
                WHERE group_id = ? AND type = ? 
                AND date(checkin_date) >= date('now', '-{} days')
                ORDER BY checkin_date DESC, created_at DESC
            """.format(
                days
            )
            results = self.execute_query(query, (group_id, user_type))

            return {
                "code": 200,
                "data": results,
                "message": f"获取最近{days}天签到记录成功，共{len(results)}条记录",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    @staticmethod
    def calculate_consecutive_bonus(consecutive_days):
        """计算连续签到奖励"""
        # 从大到小检查连续天数，返回对应奖励
        for required_days in sorted(CONSECUTIVE_BONUS_CONFIG.keys(), reverse=True):
            if consecutive_days >= required_days:
                return CONSECUTIVE_BONUS_CONFIG[required_days]
        return 0  # 少于最小天数无奖励

    @staticmethod
    def get_next_bonus_days(current_days):
        """获取下一个奖励里程碑需要的天数"""
        # 从小到大检查，找到第一个大于当前天数的里程碑
        for required_days in sorted(CONSECUTIVE_BONUS_CONFIG.keys()):
            if current_days < required_days:
                return required_days
        return 0  # 已达到最高奖励

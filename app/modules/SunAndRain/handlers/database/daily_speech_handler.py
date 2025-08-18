from .database_base import DatabaseBase
from datetime import datetime, timezone, timedelta


class DailySpeechHandler(DatabaseBase):
    """每日发言统计处理类"""

    def __init__(self, year=None):
        super().__init__(year)
        self._create_daily_speech_table()

    def _create_daily_speech_table(self):
        """创建每日发言统计表 daily_speech_stats"""
        table_schema = """
            CREATE TABLE IF NOT EXISTS daily_speech_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                user_type INTEGER NOT NULL,
                speech_date TEXT NOT NULL,
                daily_reward_count INTEGER DEFAULT 0,
                speech_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(group_id, user_id, user_type, speech_date)
            )
        """
        self.create_table("daily_speech_stats", table_schema)

    def get_current_date_china(self):
        """获取东八区当前日期"""
        china_tz = timezone(timedelta(hours=8))
        return datetime.now(china_tz).strftime("%Y-%m-%d")

    def get_daily_speech_stats(self, group_id, user_id, user_type, date=None):
        """获取用户指定日期的发言统计"""
        try:
            if date is None:
                date = self.get_current_date_china()

            query = """
                SELECT group_id, user_id, user_type, speech_date, 
                       daily_reward_count, speech_count, created_at, updated_at
                FROM daily_speech_stats 
                WHERE group_id = ? AND user_id = ? AND user_type = ? AND speech_date = ?
            """
            params = (group_id, user_id, user_type, date)
            result = self.execute_query(query, params)

            if result:
                return {
                    "code": 200,
                    "message": "获取每日发言统计成功",
                    "data": result[0],
                }
            else:
                return {"code": 404, "message": "未找到当日发言统计记录", "data": None}
        except Exception as e:
            return {
                "code": 500,
                "message": f"获取每日发言统计失败: {str(e)}",
                "data": None,
            }

    def add_speech_reward(self, group_id, user_id, user_type, reward_amount):
        """添加发言奖励记录"""
        try:
            current_date = self.get_current_date_china()
            current_time = self.get_current_time()

            # 首先获取当日统计
            stats = self.get_daily_speech_stats(
                group_id, user_id, user_type, current_date
            )

            if stats["code"] == 200:
                # 记录存在，更新统计
                current_reward = stats["data"][4]  # daily_reward_count字段
                current_speech_count = stats["data"][5]  # speech_count字段

                new_reward_count = current_reward + reward_amount
                new_speech_count = current_speech_count + 1

                query = """
                    UPDATE daily_speech_stats 
                    SET daily_reward_count = ?, speech_count = ?, updated_at = ?
                    WHERE group_id = ? AND user_id = ? AND user_type = ? AND speech_date = ?
                """
                params = (
                    new_reward_count,
                    new_speech_count,
                    current_time,
                    group_id,
                    user_id,
                    user_type,
                    current_date,
                )

                self.execute_update(query, params)

                return {
                    "code": 200,
                    "message": "更新每日发言统计成功",
                    "data": {
                        "daily_reward_count": new_reward_count,
                        "speech_count": new_speech_count,
                        "date": current_date,
                    },
                }
            else:
                # 记录不存在，创建新记录
                query = """
                    INSERT INTO daily_speech_stats 
                    (group_id, user_id, user_type, speech_date, daily_reward_count, 
                     speech_count, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    group_id,
                    user_id,
                    user_type,
                    current_date,
                    reward_amount,
                    1,
                    current_time,
                    current_time,
                )

                self.execute_update(query, params)

                return {
                    "code": 200,
                    "message": "创建每日发言统计成功",
                    "data": {
                        "daily_reward_count": reward_amount,
                        "speech_count": 1,
                        "date": current_date,
                    },
                }

        except Exception as e:
            return {
                "code": 500,
                "message": f"添加发言奖励记录失败: {str(e)}",
                "data": None,
            }

    def check_daily_reward_limit(
        self, group_id, user_id, user_type, reward_amount, daily_limit
    ):
        """检查是否超过每日发言奖励上限"""
        try:
            current_date = self.get_current_date_china()
            stats = self.get_daily_speech_stats(
                group_id, user_id, user_type, current_date
            )

            if stats["code"] == 200:
                current_reward = stats["data"][4]  # daily_reward_count字段
            else:
                current_reward = 0

            new_total = current_reward + reward_amount

            if new_total > daily_limit:
                # 超过上限，计算实际可以给予的奖励
                actual_reward = max(0, daily_limit - current_reward)
                return {
                    "code": 200,
                    "message": "检查每日奖励上限成功",
                    "data": {
                        "can_reward": actual_reward > 0,
                        "actual_reward": actual_reward,
                        "current_total": current_reward,
                        "would_exceed": True,
                        "daily_limit": daily_limit,
                    },
                }
            else:
                return {
                    "code": 200,
                    "message": "检查每日奖励上限成功",
                    "data": {
                        "can_reward": True,
                        "actual_reward": reward_amount,
                        "current_total": current_reward,
                        "would_exceed": False,
                        "daily_limit": daily_limit,
                    },
                }

        except Exception as e:
            return {
                "code": 500,
                "message": f"检查每日奖励上限失败: {str(e)}",
                "data": None,
            }

    def delete_user_speech_records(self, group_id, user_id):
        """删除用户的所有发言统计记录"""
        try:
            query = "DELETE FROM daily_speech_stats WHERE group_id = ? AND user_id = ?"
            params = (group_id, user_id)
            deleted_count = self.execute_update(query, params)

            return {
                "code": 200,
                "message": f"删除用户发言统计记录成功，共删除 {deleted_count} 条记录",
                "data": {"deleted_count": deleted_count},
            }

        except Exception as e:
            return {
                "code": 500,
                "message": f"删除用户发言统计记录失败: {str(e)}",
                "data": None,
            }

    def get_user_speech_history(self, group_id, user_id, user_type, days=7):
        """获取用户最近几天的发言统计历史"""
        try:
            query = """
                SELECT speech_date, daily_reward_count, speech_count
                FROM daily_speech_stats 
                WHERE group_id = ? AND user_id = ? AND user_type = ?
                ORDER BY speech_date DESC
                LIMIT ?
            """
            params = (group_id, user_id, user_type, days)
            result = self.execute_query(query, params)

            return {
                "code": 200,
                "message": f"获取用户最近{days}天发言历史成功",
                "data": result,
            }

        except Exception as e:
            return {
                "code": 500,
                "message": f"获取用户发言历史失败: {str(e)}",
                "data": None,
            }

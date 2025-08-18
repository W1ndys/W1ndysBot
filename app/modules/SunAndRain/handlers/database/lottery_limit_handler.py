import sqlite3
from datetime import datetime, timedelta
from .database_base import DatabaseBase


class LotteryLimitHandler(DatabaseBase):
    """抽奖限制处理器"""

    def __init__(self, year=None):
        super().__init__(year)
        self._create_lottery_limit_table()

    def _create_lottery_limit_table(self):
        """创建抽奖限制表"""
        table_schema = """
        CREATE TABLE IF NOT EXISTS lottery_limit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            user_type INTEGER NOT NULL,
            last_lottery_time TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(group_id, user_id, user_type)
        )
        """
        self.create_table("lottery_limit", table_schema)

        # 创建索引以提高查询性能
        try:
            self.cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_lottery_limit_lookup ON lottery_limit(group_id, user_id, user_type)"
            )
            self.cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_lottery_limit_time ON lottery_limit(last_lottery_time)"
            )
            self.conn.commit()
        except Exception:
            pass  # 索引可能已存在

    def check_lottery_cooldown(self, group_id, user_id, user_type, cooldown_minutes=1):
        """
        检查用户是否在冷却时间内

        Args:
            group_id: 群号
            user_id: 用户ID
            user_type: 用户类型 (0=阳光, 1=雨露)
            cooldown_minutes: 冷却时间（分钟），默认1分钟

        Returns:
            dict: {
                "code": 200/403,
                "data": {
                    "can_lottery": bool,
                    "last_lottery_time": str,
                    "remaining_seconds": int,
                    "cooldown_minutes": int
                },
                "message": str
            }
        """
        try:
            current_time = datetime.now()

            # 查询用户上次抽奖时间
            query = """
                SELECT last_lottery_time 
                FROM lottery_limit 
                WHERE group_id = ? AND user_id = ? AND user_type = ?
            """
            result = self.execute_query(query, (group_id, user_id, user_type))

            if not result:
                # 用户第一次抽奖，没有限制
                return {
                    "code": 200,
                    "data": {
                        "can_lottery": True,
                        "last_lottery_time": None,
                        "remaining_seconds": 0,
                        "cooldown_minutes": cooldown_minutes,
                    },
                    "message": "首次抽奖，无限制",
                }

            last_lottery_time_str = result[0][0]
            last_lottery_time = datetime.strptime(
                last_lottery_time_str, "%Y-%m-%d %H:%M:%S"
            )

            # 计算冷却结束时间
            cooldown_end_time = last_lottery_time + timedelta(minutes=cooldown_minutes)

            if current_time >= cooldown_end_time:
                # 冷却时间已过，可以抽奖
                return {
                    "code": 200,
                    "data": {
                        "can_lottery": True,
                        "last_lottery_time": last_lottery_time_str,
                        "remaining_seconds": 0,
                        "cooldown_minutes": cooldown_minutes,
                    },
                    "message": "冷却时间已过，可以抽奖",
                }
            else:
                # 还在冷却时间内
                remaining_seconds = int(
                    (cooldown_end_time - current_time).total_seconds()
                )
                return {
                    "code": 403,
                    "data": {
                        "can_lottery": False,
                        "last_lottery_time": last_lottery_time_str,
                        "remaining_seconds": remaining_seconds,
                        "cooldown_minutes": cooldown_minutes,
                    },
                    "message": f"冷却中，还需等待{remaining_seconds}秒",
                }

        except Exception as e:
            return {"code": 500, "data": None, "message": f"检查抽奖冷却失败: {str(e)}"}

    def update_lottery_time(self, group_id, user_id, user_type, lottery_time=None):
        """
        更新用户抽奖时间

        Args:
            group_id: 群号
            user_id: 用户ID
            user_type: 用户类型
            lottery_time: 抽奖时间，默认为当前时间

        Returns:
            dict: 操作结果
        """
        try:
            if lottery_time is None:
                lottery_time = self.get_current_time()

            # 使用 INSERT OR REPLACE 来处理插入或更新
            query = """
                INSERT OR REPLACE INTO lottery_limit 
                (group_id, user_id, user_type, last_lottery_time, created_at, updated_at)
                VALUES (?, ?, ?, ?, 
                    COALESCE((SELECT created_at FROM lottery_limit WHERE group_id = ? AND user_id = ? AND user_type = ?), ?),
                    ?)
            """
            current_time = self.get_current_time()
            params = (
                group_id,
                user_id,
                user_type,
                lottery_time,
                group_id,
                user_id,
                user_type,
                current_time,  # COALESCE 参数
                current_time,
            )

            rows_affected = self.execute_update(query, params)

            return {
                "code": 200,
                "data": {
                    "group_id": group_id,
                    "user_id": user_id,
                    "user_type": user_type,
                    "lottery_time": lottery_time,
                    "rows_affected": rows_affected,
                },
                "message": "更新抽奖时间成功",
            }

        except Exception as e:
            return {"code": 500, "data": None, "message": f"更新抽奖时间失败: {str(e)}"}

    def get_user_lottery_history(self, group_id, user_id, user_type=None, limit=10):
        """
        获取用户抽奖历史记录

        Args:
            group_id: 群号
            user_id: 用户ID
            user_type: 用户类型，None表示获取所有类型
            limit: 返回记录数量限制

        Returns:
            dict: 查询结果
        """
        try:
            if user_type is not None:
                query = """
                    SELECT group_id, user_id, user_type, last_lottery_time, created_at, updated_at
                    FROM lottery_limit 
                    WHERE group_id = ? AND user_id = ? AND user_type = ?
                    ORDER BY last_lottery_time DESC
                    LIMIT ?
                """
                params = (group_id, user_id, user_type, limit)
            else:
                query = """
                    SELECT group_id, user_id, user_type, last_lottery_time, created_at, updated_at
                    FROM lottery_limit 
                    WHERE group_id = ? AND user_id = ?
                    ORDER BY last_lottery_time DESC
                    LIMIT ?
                """
                params = (group_id, user_id, limit)

            result = self.execute_query(query, params)

            return {
                "code": 200,
                "data": result,
                "message": f"获取抽奖历史成功，共{len(result)}条记录",
            }

        except Exception as e:
            return {"code": 500, "data": None, "message": f"获取抽奖历史失败: {str(e)}"}

    def clean_old_records(self, days_to_keep=7):
        """
        清理旧的抽奖记录

        Args:
            days_to_keep: 保留天数，默认7天

        Returns:
            dict: 清理结果
        """
        try:
            cutoff_time = (datetime.now() - timedelta(days=days_to_keep)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            query = "DELETE FROM lottery_limit WHERE last_lottery_time < ?"
            rows_deleted = self.execute_update(query, (cutoff_time,))

            return {
                "code": 200,
                "data": {"deleted_count": rows_deleted},
                "message": f"清理完成，删除了{rows_deleted}条记录",
            }

        except Exception as e:
            return {"code": 500, "data": None, "message": f"清理旧记录失败: {str(e)}"}

    def delete_user_lottery_records(self, group_id, user_id):
        """
        删除指定用户的所有抽奖限制记录

        Args:
            group_id: 群号
            user_id: 用户ID

        Returns:
            dict: 删除结果
        """
        try:
            query = "DELETE FROM lottery_limit WHERE group_id = ? AND user_id = ?"
            rows_deleted = self.execute_update(query, (group_id, user_id))

            return {
                "code": 200,
                "data": {"deleted_count": rows_deleted},
                "message": f"删除用户抽奖记录成功，删除了{rows_deleted}条记录",
            }

        except Exception as e:
            return {
                "code": 500,
                "data": None,
                "message": f"删除用户抽奖记录失败: {str(e)}",
            }

    def get_group_lottery_stats(self, group_id, hours=24):
        """
        获取群组内指定时间段的抽奖统计

        Args:
            group_id: 群号
            hours: 统计时间段（小时），默认24小时

        Returns:
            dict: 统计结果
        """
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            query = """
                SELECT user_type, COUNT(*) as lottery_count
                FROM lottery_limit 
                WHERE group_id = ? AND last_lottery_time >= ?
                GROUP BY user_type
                ORDER BY user_type
            """
            result = self.execute_query(query, (group_id, cutoff_time))

            stats = {}
            total_count = 0
            for user_type, count in result:
                type_name = self.get_type_name(user_type)
                stats[type_name] = count
                total_count += count

            return {
                "code": 200,
                "data": {
                    "group_id": group_id,
                    "hours": hours,
                    "total_lottery_count": total_count,
                    "type_stats": stats,
                    "cutoff_time": cutoff_time,
                },
                "message": f"获取群组抽奖统计成功，{hours}小时内共{total_count}次抽奖",
            }

        except Exception as e:
            return {
                "code": 500,
                "data": None,
                "message": f"获取群组抽奖统计失败: {str(e)}",
            }

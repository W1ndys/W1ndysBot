import sqlite3
import os
from datetime import datetime
from .. import MODULE_NAME
import random


class DataManager:
    def __init__(self):
        data_dir = os.path.join("data", MODULE_NAME)
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"data.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """创建用户签到信息表和签到记录表"""
        # 创建用户基本信息表 user_checkin
        # 字段说明：
        #   id: 主键，自增
        #   group_id: 群号
        #   user_id: 用户QQ号
        #   type: 用户类型（0=阳光，1=雨露等）
        #   count: 当前拥有的阳光/雨露数量
        #   consecutive_days: 连续签到天数
        #   last_checkin_date: 上次签到日期
        #   total_checkin_days: 累计签到天数
        #   created_at: 创建时间
        #   updated_at: 更新时间
        #   UNIQUE(group_id, user_id, type): 保证同一群同一用户同一类型唯一
        self.cursor.execute(
            """
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
        )

        # 创建签到记录表 checkin_records
        # 字段说明：
        #   id: 主键，自增
        #   group_id: 群号
        #   user_id: 用户QQ号
        #   checkin_date: 签到日期（YYYY-MM-DD）
        #   type: 用户类型
        #   reward_amount: 本次签到基础奖励
        #   consecutive_days: 本次签到后连续天数
        #   bonus_amount: 连续签到奖励
        #   created_at: 签到时间戳
        #   UNIQUE(group_id, user_id, checkin_date, type): 保证同一天同一用户同一类型只能签到一次
        self.cursor.execute(
            """
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
        )

        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def add_user(self, group_id, user_id, user_type=0):
        """添加新用户记录"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                """
                INSERT INTO user_checkin (group_id, user_id, type, count, created_at, updated_at)
                VALUES (?, ?, ?, 0, ?, ?)
            """,
                (group_id, user_id, user_type, current_time, current_time),
            )
            self.conn.commit()
            return {
                "code": 200,
                "data": {
                    "group_id": group_id,
                    "user_id": user_id,
                    "type": user_type,
                    "count": 0,
                },
                "message": "用户添加成功",
            }
        except sqlite3.IntegrityError:
            return {"code": 409, "data": None, "message": "用户已存在"}
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_user_info(self, group_id, user_id, user_type=None):
        """获取用户信息"""
        try:
            if user_type is not None:
                self.cursor.execute(
                    """
                    SELECT * FROM user_checkin 
                    WHERE group_id = ? AND user_id = ? AND type = ?
                """,
                    (group_id, user_id, user_type),
                )
            else:
                self.cursor.execute(
                    """
                    SELECT * FROM user_checkin 
                    WHERE group_id = ? AND user_id = ?
                """,
                    (group_id, user_id),
                )

            results = self.cursor.fetchall()
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
                    "message": "用户不存在，请先选择阳光或雨滴",
                }

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                """
                UPDATE user_checkin 
                SET count = count + ?, updated_at = ?
                WHERE group_id = ? AND user_id = ? AND type = ?
            """,
                (increment, current_time, group_id, user_id, user_type),
            )
            self.conn.commit()

            if self.cursor.rowcount > 0:
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
            self.cursor.execute(
                """
                SELECT count FROM user_checkin 
                WHERE group_id = ? AND user_id = ? AND type = ?
            """,
                (group_id, user_id, user_type),
            )
            result = self.cursor.fetchone()

            if result:
                return {"code": 200, "data": result[0], "message": "获取用户数值成功"}
            else:
                return {"code": 404, "data": 0, "message": "用户不存在"}
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_group_ranking(self, group_id, user_type, limit=10):
        """获取群组内指定类型的排行榜"""
        try:
            self.cursor.execute(
                """
                SELECT user_id, count FROM user_checkin 
                WHERE group_id = ? AND type = ?
                ORDER BY count DESC
                LIMIT ?
            """,
                (group_id, user_type, limit),
            )
            results = self.cursor.fetchall()

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
            self.cursor.execute(
                """
                SELECT user_id, type, count FROM user_checkin 
                WHERE group_id = ?
                ORDER BY user_id, type
            """,
                (group_id,),
            )
            results = self.cursor.fetchall()

            return {
                "code": 200,
                "data": results,
                "message": f"获取群组用户信息成功，共{len(results)}条记录",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def delete_user(self, group_id, user_id):
        """删除用户的所有记录"""
        try:
            self.cursor.execute(
                """
                DELETE FROM user_checkin 
                WHERE group_id = ? AND user_id = ?
            """,
                (group_id, user_id),
            )
            self.conn.commit()

            if self.cursor.rowcount > 0:
                return {
                    "code": 200,
                    "data": {"deleted_count": self.cursor.rowcount},
                    "message": f"删除用户成功，删除了{self.cursor.rowcount}条记录",
                }
            else:
                return {"code": 404, "data": None, "message": "用户不存在，无需删除"}
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def reset_group_data(self, group_id):
        """重置群组的所有数据"""
        try:
            self.cursor.execute(
                """
                DELETE FROM user_checkin WHERE group_id = ?
            """,
                (group_id,),
            )
            self.conn.commit()

            return {
                "code": 200,
                "data": {"deleted_count": self.cursor.rowcount},
                "message": f"重置群组数据成功，删除了{self.cursor.rowcount}条记录",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_total_stats(self, group_id):
        """获取群组的统计信息"""
        try:
            self.cursor.execute(
                """
                SELECT 
                    type,
                    COUNT(*) as user_count,
                    SUM(count) as total_count,
                    AVG(count) as avg_count
                FROM user_checkin 
                WHERE group_id = ?
                GROUP BY type
            """,
                (group_id,),
            )
            results = self.cursor.fetchall()

            return {"code": 200, "data": results, "message": "获取统计信息成功"}
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def daily_checkin(self, group_id, user_id, user_type, base_reward=None):
        """每日签到功能，包含连续签到奖励"""
        try:

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_date = datetime.now().strftime("%Y-%m-%d")

            # 检查今日是否已签到
            self.cursor.execute(
                """
                SELECT id FROM checkin_records
                WHERE group_id = ? AND user_id = ? AND checkin_date = ? AND type = ?
            """,
                (group_id, user_id, current_date, user_type),
            )

            if self.cursor.fetchone():
                return {"code": 409, "data": None, "message": "今日已签到，请明天再来"}

            # 获取用户信息
            user_info = self.get_user_info(group_id, user_id, user_type)
            if user_info["code"] != 200:
                return {
                    "code": 404,
                    "data": None,
                    "message": "用户不存在，请先选择阳光或雨滴",
                }

            user_data = user_info["data"][0]
            last_checkin_date = user_data[6]  # last_checkin_date字段
            consecutive_days = user_data[5]  # consecutive_days字段

            # 计算连续签到天数
            if last_checkin_date:
                last_date = datetime.strptime(last_checkin_date, "%Y-%m-%d")
                today = datetime.strptime(current_date, "%Y-%m-%d")

                if (today - last_date).days == 1:
                    # 连续签到
                    consecutive_days += 1
                elif (today - last_date).days > 1:
                    # 中断了，重新开始
                    consecutive_days = 1
                else:
                    # 今天已经签到过了（理论上不会到这里）
                    consecutive_days = consecutive_days
            else:
                # 第一次签到
                consecutive_days = 1

            # 计算基础奖励
            if base_reward is None:
                base_reward = random.randint(5, 15)

            # 计算连续签到奖励
            bonus_reward = self._calculate_consecutive_bonus(consecutive_days)
            total_reward = base_reward + bonus_reward

            # 更新用户基本信息
            self.cursor.execute(
                """
                UPDATE user_checkin 
                SET count = count + ?, 
                    consecutive_days = ?, 
                    last_checkin_date = ?,
                    total_checkin_days = total_checkin_days + 1,
                    updated_at = ?
                WHERE group_id = ? AND user_id = ? AND type = ?
            """,
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

            # 记录签到历史
            self.cursor.execute(
                """
                INSERT INTO checkin_records 
                (group_id, user_id, checkin_date, type, reward_amount, consecutive_days, bonus_amount, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    group_id,
                    user_id,
                    current_date,
                    user_type,
                    base_reward,
                    consecutive_days,
                    bonus_reward,
                    current_time,
                ),
            )

            self.conn.commit()

            return {
                "code": 200,
                "data": {
                    "base_reward": base_reward,
                    "bonus_reward": bonus_reward,
                    "total_reward": total_reward,
                    "consecutive_days": consecutive_days,
                    "new_total": self.get_user_count(group_id, user_id, user_type)[
                        "data"
                    ]
                    + total_reward,
                },
                "message": "签到成功",
            }

        except Exception as e:
            return {"code": 500, "data": None, "message": f"签到失败: {str(e)}"}

    def _calculate_consecutive_bonus(self, consecutive_days):
        """计算连续签到奖励"""
        if consecutive_days >= 30:
            return 30  # 连续30天+30奖励
        elif consecutive_days >= 15:
            return 20  # 连续15天+20奖励
        elif consecutive_days >= 7:
            return 15  # 连续7天+15奖励
        elif consecutive_days >= 3:
            return 10  # 连续3天+10奖励
        else:
            return 0  # 少于3天无奖励

    def get_user_checkin_stats(self, group_id, user_id, user_type=None):
        """获取用户签到统计信息"""
        try:
            if user_type is not None:
                self.cursor.execute(
                    """
                    SELECT consecutive_days, last_checkin_date, total_checkin_days, count
                    FROM user_checkin 
                    WHERE group_id = ? AND user_id = ? AND type = ?
                """,
                    (group_id, user_id, user_type),
                )
            else:
                self.cursor.execute(
                    """
                    SELECT type, consecutive_days, last_checkin_date, total_checkin_days, count
                    FROM user_checkin 
                    WHERE group_id = ? AND user_id = ?
                """,
                    (group_id, user_id),
                )

            results = self.cursor.fetchall()
            if results:
                return {"code": 200, "data": results, "message": "获取签到统计成功"}
            else:
                return {"code": 404, "data": None, "message": "用户信息不存在"}
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_checkin_history(self, group_id, user_id, user_type, days=7):
        """获取用户签到历史记录"""
        try:
            self.cursor.execute(
                """
                SELECT checkin_date, reward_amount, consecutive_days, bonus_amount
                FROM checkin_records 
                WHERE group_id = ? AND user_id = ? AND type = ?
                ORDER BY checkin_date DESC
                LIMIT ?
            """,
                (group_id, user_id, user_type, days),
            )
            results = self.cursor.fetchall()

            return {
                "code": 200,
                "data": results,
                "message": f"获取签到历史成功，共{len(results)}条记录",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_consecutive_ranking(self, group_id, user_type, limit=10):
        """获取连续签到天数排行榜"""
        try:
            self.cursor.execute(
                """
                SELECT user_id, consecutive_days, total_checkin_days
                FROM user_checkin 
                WHERE group_id = ? AND type = ?
                ORDER BY consecutive_days DESC, total_checkin_days DESC
                LIMIT ?
            """,
                (group_id, user_type, limit),
            )
            results = self.cursor.fetchall()

            return {
                "code": 200,
                "data": results,
                "message": f"获取连续签到排行榜成功，共{len(results)}条记录",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}


if __name__ == "__main__":
    # 使用with语句确保数据库连接正确关闭
    with DataManager() as dm:
        # 添加用户（阳光类型）
        result1 = dm.add_user(123456, 987654, 0)
        print("添加用户:", result1)

        # 测试签到功能
        result2 = dm.daily_checkin(123456, 987654, 0)
        print("第一次签到:", result2)

        # 测试重复签到
        result3 = dm.daily_checkin(123456, 987654, 0)
        print("重复签到:", result3)

        # 获取签到统计
        result4 = dm.get_user_checkin_stats(123456, 987654, 0)
        print("签到统计:", result4)

        # 获取签到历史
        result5 = dm.get_checkin_history(123456, 987654, 0)
        print("签到历史:", result5)

        # 获取连续签到排行榜
        result6 = dm.get_consecutive_ranking(123456, 0)
        print("连续签到排行榜:", result6)

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
        """添加新用户记录 - 用户只能选择阳光或雨露中的一个"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            type_name = "阳光" if user_type == 0 else "雨露"

            # 首先检查用户是否已经选择过任何类型
            existing_user_info = self.get_user_info(group_id, user_id)

            if existing_user_info["code"] == 200 and existing_user_info["data"]:
                # 用户已经选择过类型
                existing_user_data = existing_user_info["data"][0]
                existing_type = existing_user_data[3]  # type字段
                existing_type_name = "阳光" if existing_type == 0 else "雨露"
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
                    "message": "用户不存在，请先选择阳光或雨露",
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
            # 先删除签到记录
            self.cursor.execute(
                """
                DELETE FROM checkin_records 
                WHERE group_id = ? AND user_id = ?
            """,
                (group_id, user_id),
            )
            checkin_deleted = self.cursor.rowcount

            # 再删除用户信息
            self.cursor.execute(
                """
                DELETE FROM user_checkin 
                WHERE group_id = ? AND user_id = ?
            """,
                (group_id, user_id),
            )
            user_deleted = self.cursor.rowcount

            self.conn.commit()

            total_deleted = checkin_deleted + user_deleted

            if total_deleted > 0:
                return {
                    "code": 200,
                    "data": {
                        "deleted_count": total_deleted,
                        "user_records": user_deleted,
                        "checkin_records": checkin_deleted,
                    },
                    "message": f"删除用户成功，删除了{total_deleted}条记录（用户信息:{user_deleted}条，签到记录:{checkin_deleted}条）",
                }
            else:
                return {"code": 404, "data": None, "message": "用户不存在，无需删除"}
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def reset_user_type_choice(self, group_id, user_id):
        """重置用户的类型选择，允许重新选择阳光或雨露"""
        try:
            # 获取用户当前信息
            user_info = self.get_user_info(group_id, user_id)
            if user_info["code"] != 200 or not user_info["data"]:
                return {"code": 404, "data": None, "message": "用户不存在，无需重置"}

            user_data = user_info["data"][0]
            current_type = user_data[3]  # type字段
            current_type_name = "阳光" if current_type == 0 else "雨露"
            current_count = user_data[4]  # count字段

            # 删除用户的所有数据
            delete_result = self.delete_user(group_id, user_id)

            if delete_result["code"] == 200:
                return {
                    "code": 200,
                    "data": {
                        "previous_type": current_type,
                        "previous_type_name": current_type_name,
                        "previous_count": current_count,
                        "deleted_records": delete_result["data"]["deleted_count"],
                    },
                    "message": f"🔄 重置成功！\n"
                    f"📝 已清除您之前的{current_type_name}类型选择\n"
                    f"💎 之前拥有：{current_count}个{current_type_name}\n"
                    f"🆕 现在可以重新选择阳光或雨露类型\n"
                    f"✨ 请发送「选择 阳光」或「选择 雨露」来重新选择",
                }
            else:
                return delete_result

        except Exception as e:
            return {"code": 500, "data": None, "message": f"重置失败: {str(e)}"}

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
            type_name = "阳光" if user_type == 0 else "雨露"

            # 检查今日是否已签到
            self.cursor.execute(
                """
                SELECT checkin_date, reward_amount, consecutive_days, bonus_amount, created_at 
                FROM checkin_records
                WHERE group_id = ? AND user_id = ? AND checkin_date = ? AND type = ?
            """,
                (group_id, user_id, current_date, user_type),
            )

            existing_checkin = self.cursor.fetchone()
            if existing_checkin:
                (
                    checkin_date,
                    reward_amount,
                    consecutive_days,
                    bonus_amount,
                    checkin_time,
                ) = existing_checkin
                total_reward = reward_amount + bonus_amount
                return {
                    "code": 409,
                    "data": {
                        "checkin_date": checkin_date,
                        "checkin_time": checkin_time,
                        "reward_amount": reward_amount,
                        "bonus_amount": bonus_amount,
                        "total_reward": total_reward,
                        "consecutive_days": consecutive_days,
                        "type_name": type_name,
                    },
                    "message": f"⚠️ 今日已签到完成！\n"
                    f"📅 签到日期：{checkin_date}\n"
                    f"⏰ 签到时间：{checkin_time}\n"
                    f"🎁 基础奖励：{reward_amount}个{type_name}\n"
                    f"🔥 连续奖励：{bonus_amount}个{type_name}\n"
                    f"💎 总计获得：{total_reward}个{type_name}\n"
                    f"📈 连续签到：{consecutive_days}天\n"
                    f"⏰ 请明天再来签到吧！",
                }

            # 获取用户信息
            user_info = self.get_user_info(group_id, user_id, user_type)
            if user_info["code"] != 200:
                return {
                    "code": 404,
                    "data": None,
                    "message": f"❌ 用户不存在！\n"
                    f"📝 请先发送「选择 {type_name}」来选择您的类型\n"
                    f"✨ 阳光类型：发送「选择 阳光」\n"
                    f"💧 雨露类型：发送「选择 雨露」",
                }

            user_data = user_info["data"][0]
            last_checkin_date = user_data[6]  # last_checkin_date字段
            consecutive_days = user_data[5]  # consecutive_days字段
            current_count = user_data[4]  # count字段

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
            new_total_count = current_count + total_reward

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

            # 生成连续签到奖励说明
            bonus_info = ""
            if bonus_reward > 0:
                bonus_info = f"🔥 连续奖励：{bonus_reward}个{type_name}\n"

            # 生成下次奖励预告
            next_bonus = self._calculate_consecutive_bonus(consecutive_days + 1)
            next_bonus_info = ""
            if next_bonus > bonus_reward:
                days_needed = self._get_next_bonus_days(consecutive_days + 1)
                if days_needed > 0:
                    next_bonus_info = f"🎯 连续签到{days_needed}天可获得{next_bonus}个{type_name}奖励！\n"

            return {
                "code": 200,
                "data": {
                    "checkin_date": current_date,
                    "checkin_time": current_time,
                    "base_reward": base_reward,
                    "bonus_reward": bonus_reward,
                    "total_reward": total_reward,
                    "consecutive_days": consecutive_days,
                    "new_total": new_total_count,
                    "type_name": type_name,
                    "previous_count": current_count,
                },
                "message": f"🎉 签到成功！\n"
                f"📅 签到日期：{current_date}\n"
                f"⏰ 签到时间：{current_time}\n"
                f"🎁 基础奖励：{base_reward}个{type_name}\n"
                f"{bonus_info}"
                f"💎 总计获得：{total_reward}个{type_name}\n"
                f"📊 拥有总数：{new_total_count}个{type_name}（+{total_reward}）\n"
                f"📈 连续签到：{consecutive_days}天\n"
                f"{next_bonus_info}"
                f"✨ 明天记得继续签到哦！",
            }

        except Exception as e:
            return {
                "code": 500,
                "data": None,
                "message": f"❌ 签到失败: {str(e)}\n⚠️ 请稍后重试或联系管理员",
            }

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

    def _get_next_bonus_days(self, current_days):
        """获取下一个奖励里程碑需要的天数"""
        if current_days < 3:
            return 3
        elif current_days < 7:
            return 7
        elif current_days < 15:
            return 15
        elif current_days < 30:
            return 30
        else:
            return 0  # 已达到最高奖励

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
        print("=" * 60)
        print("测试 SunAndRain 数据管理器 - 用户只能选择一种类型")
        print("=" * 60)

        # 测试添加用户（阳光类型）
        print("\n1. 测试选择阳光类型:")
        result1 = dm.add_user(123456, 987654, 0)
        print("选择阳光:", result1["message"])

        # 测试重复选择同一类型
        print("\n2. 测试重复选择阳光:")
        result1_duplicate = dm.add_user(123456, 987654, 0)
        print("重复选择阳光:", result1_duplicate["message"])

        # 测试选择不同类型（应该被拒绝）
        print("\n3. 测试切换到雨露类型（应该失败）:")
        result1_switch = dm.add_user(123456, 987654, 1)
        print("尝试切换到雨露:", result1_switch["message"])

        # 测试新用户选择雨露类型
        print("\n4. 测试新用户选择雨露类型:")
        result1_rain = dm.add_user(123456, 111111, 1)
        print("新用户选择雨露:", result1_rain["message"])

        # 测试新用户尝试切换类型（应该被拒绝）
        print("\n5. 测试新用户切换到阳光类型（应该失败）:")
        result1_rain_switch = dm.add_user(123456, 111111, 0)
        print("尝试切换到阳光:", result1_rain_switch["message"])

        # 测试签到功能（阳光）
        print("\n6. 测试阳光用户签到:")
        result2 = dm.daily_checkin(123456, 987654, 0)
        print("阳光签到:", result2["message"])

        # 测试签到功能（雨露）
        print("\n7. 测试雨露用户签到:")
        result2_rain = dm.daily_checkin(123456, 111111, 1)
        print("雨露签到:", result2_rain["message"])

        # 测试重复签到
        print("\n8. 测试重复签到:")
        result3 = dm.daily_checkin(123456, 987654, 0)
        print("重复签到:", result3["message"])

        # 获取签到统计
        print("\n9. 获取签到统计:")
        result4 = dm.get_user_checkin_stats(123456, 987654, 0)
        print("阳光用户签到统计:", result4)

        # 获取签到历史
        print("\n10. 获取签到历史:")
        result5 = dm.get_checkin_history(123456, 987654, 0)
        print("阳光用户签到历史:", result5)

        # 获取连续签到排行榜
        print("\n11. 获取连续签到排行榜:")
        result6 = dm.get_consecutive_ranking(123456, 0)
        print("阳光排行榜:", result6)

        result6_rain = dm.get_consecutive_ranking(123456, 1)
        print("雨露排行榜:", result6_rain)

        # 测试重置用户类型选择功能
        print("\n12. 测试重置用户类型选择:")
        reset_result = dm.reset_user_type_choice(123456, 987654)
        print("重置用户类型:", reset_result["message"])

        # 测试重置后重新选择
        print("\n13. 测试重置后重新选择雨露:")
        reselect_result = dm.add_user(123456, 987654, 1)
        print("重置后选择雨露:", reselect_result["message"])

        # 验证重新选择后的签到
        print("\n14. 测试重新选择后的签到:")
        new_checkin_result = dm.daily_checkin(123456, 987654, 1)
        print("重新选择后签到:", new_checkin_result["message"])

        # 测试发言奖励功能
        print("\n15. 测试发言奖励功能:")
        for i in range(5):
            reward_amount = random.randint(1, 5)
            update_result = dm.update_user_count(123456, 987654, 1, reward_amount)
            if update_result["code"] == 200:
                print(
                    f"发言{i+1}: 获得{reward_amount}个雨露，当前总数：{update_result['data']['count']}"
                )

        print("\n" + "=" * 60)
        print("测试完成 - 验证了用户只能选择一种类型的逻辑、重置功能及发言奖励")
        print("=" * 60)

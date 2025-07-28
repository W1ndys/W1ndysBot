import os
from datetime import datetime
from ... import MODULE_NAME
import random

from .database_base import DatabaseBase
from .user_checkin_handler import UserCheckinHandler
from .checkin_records_handler import CheckinRecordsHandler


class DataManager:
    """主数据管理器类，整合所有处理器"""

    def __init__(self, year=None):
        # 设置年份
        self.year = year if year is not None else datetime.now().year

        # 初始化各个处理器
        self.user_handler = UserCheckinHandler(self.year)
        self.records_handler = CheckinRecordsHandler(self.year)

        # 为了保持兼容性，保留一些基本属性
        self.data_dir = self.user_handler.data_dir
        self.db_path = self.user_handler.db_path
        self.conn = self.user_handler.conn
        self.cursor = self.user_handler.cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 关闭所有处理器的连接
        try:
            self.user_handler.__exit__(exc_type, exc_val, exc_tb)
        except:
            pass
        try:
            self.records_handler.__exit__(exc_type, exc_val, exc_tb)
        except:
            pass

    # ===== 用户基本信息相关方法 =====
    def add_user(self, group_id, user_id, user_type=0):
        """添加新用户记录 - 用户只能选择阳光或雨露中的一个"""
        return self.user_handler.add_user(group_id, user_id, user_type)

    def get_user_info(self, group_id, user_id, user_type=None):
        """获取用户信息"""
        return self.user_handler.get_user_info(group_id, user_id, user_type)

    def update_user_count(self, group_id, user_id, user_type, increment=1):
        """更新用户的数值"""
        return self.user_handler.update_user_count(
            group_id, user_id, user_type, increment
        )

    def get_user_count(self, group_id, user_id, user_type):
        """获取用户特定类型的数值"""
        return self.user_handler.get_user_count(group_id, user_id, user_type)

    def get_group_ranking(self, group_id, user_type, limit=10):
        """获取群组内指定类型的排行榜"""
        return self.user_handler.get_group_ranking(group_id, user_type, limit)

    def get_all_group_users(self, group_id):
        """获取群组内所有用户的信息"""
        return self.user_handler.get_all_group_users(group_id)

    def delete_user(self, group_id, user_id):
        """删除用户的所有记录"""
        try:
            # 先删除签到记录
            records_result = self.records_handler.delete_user_records(group_id, user_id)
            checkin_deleted = (
                records_result["data"]["checkin_records"]
                if records_result["code"] == 200
                else 0
            )

            # 再删除用户信息
            user_result = self.user_handler.delete_user(group_id, user_id)
            user_deleted = (
                user_result["data"]["user_records"] if user_result["code"] == 200 else 0
            )

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
            current_type_name = DatabaseBase.get_type_name(current_type)
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
            # 重置签到记录
            records_result = self.records_handler.reset_group_records(group_id)
            records_deleted = (
                records_result["data"]["deleted_count"]
                if records_result["code"] == 200
                else 0
            )

            # 重置用户数据
            user_result = self.user_handler.reset_group_data(group_id)
            user_deleted = (
                user_result["data"]["deleted_count"]
                if user_result["code"] == 200
                else 0
            )

            total_deleted = records_deleted + user_deleted

            return {
                "code": 200,
                "data": {"deleted_count": total_deleted},
                "message": f"重置群组数据成功，删除了{total_deleted}条记录",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_total_stats(self, group_id):
        """获取群组的统计信息"""
        return self.user_handler.get_total_stats(group_id)

    # ===== 签到相关方法 =====
    def daily_checkin(self, group_id, user_id, user_type, base_reward=None):
        """每日签到功能，包含连续签到奖励"""
        try:
            current_time = self.user_handler.get_current_time()
            current_date = self.user_handler.get_current_date()
            type_name = DatabaseBase.get_type_name(user_type)

            # 检查今日是否已签到
            already_checked = False
            checkin_date = None
            checkin_time = None
            reward_amount = 0
            bonus_amount = 0
            consecutive_days_today = 0

            try:
                checkin_check = self.records_handler.check_today_checkin(
                    group_id, user_id, current_date, user_type
                )

                if isinstance(checkin_check, dict) and checkin_check.get(
                    "already_checked", False
                ):
                    already_checked = True
                    checkin_data = checkin_check.get("checkin_data")
                    if (
                        checkin_data
                        and isinstance(checkin_data, (list, tuple))
                        and len(checkin_data) >= 5
                    ):
                        checkin_date = checkin_data[0]
                        reward_amount = checkin_data[1]
                        consecutive_days_today = checkin_data[2]
                        bonus_amount = checkin_data[3]
                        checkin_time = checkin_data[4]
            except Exception:
                # 如果检查签到状态失败，假设今天没有签到
                already_checked = False

            if already_checked:
                total_reward = reward_amount + bonus_amount
                return {
                    "code": 409,
                    "data": {
                        "checkin_date": checkin_date,
                        "checkin_time": checkin_time,
                        "reward_amount": reward_amount,
                        "bonus_amount": bonus_amount,
                        "total_reward": total_reward,
                        "consecutive_days": consecutive_days_today,
                        "type_name": type_name,
                    },
                    "message": f"⚠️ 今日已签到完成！\n"
                    f"📅 签到日期：{checkin_date}\n"
                    f"⏰ 签到时间：{checkin_time}\n"
                    f"🎁 基础奖励：{reward_amount}个{type_name}\n"
                    f"🔥 连续奖励：{bonus_amount}个{type_name}\n"
                    f"💎 总计获得：{total_reward}个{type_name}\n"
                    f"📈 连续签到：{consecutive_days_today}天\n"
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
            consecutive_days = self._calculate_consecutive_days(
                last_checkin_date, current_date, consecutive_days
            )

            # 计算基础奖励
            if base_reward is None:
                base_reward = random.randint(5, 15)

            # 计算连续签到奖励
            bonus_reward = CheckinRecordsHandler.calculate_consecutive_bonus(
                consecutive_days
            )
            total_reward = base_reward + bonus_reward
            new_total_count = current_count + total_reward

            # 更新用户基本信息
            update_success = self.user_handler.update_checkin_info(
                group_id,
                user_id,
                user_type,
                total_reward,
                consecutive_days,
                current_date,
                current_time,
            )
            if not update_success:
                raise Exception("更新用户签到信息失败")

            # 记录签到历史
            record_success = self.records_handler.add_checkin_record(
                group_id,
                user_id,
                current_date,
                user_type,
                base_reward,
                consecutive_days,
                bonus_reward,
                current_time,
            )
            if not record_success:
                raise Exception("添加签到记录失败")

            # 生成连续签到奖励说明
            bonus_info = ""
            if bonus_reward > 0:
                bonus_info = f"🔥 连续奖励：{bonus_reward}个{type_name}\n"

            # 生成下次奖励预告
            next_bonus = CheckinRecordsHandler.calculate_consecutive_bonus(
                consecutive_days + 1
            )
            next_bonus_info = ""
            if next_bonus > bonus_reward:
                days_needed = CheckinRecordsHandler.get_next_bonus_days(
                    consecutive_days + 1
                )
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

    def _calculate_consecutive_days(
        self, last_checkin_date, current_date, consecutive_days
    ):
        """计算连续签到天数"""
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

        return consecutive_days

    # ===== 签到统计和历史相关方法 =====
    def get_user_checkin_stats(self, group_id, user_id, user_type=None):
        """获取用户签到统计信息"""
        return self.user_handler.get_user_checkin_stats(group_id, user_id, user_type)

    def get_checkin_history(self, group_id, user_id, user_type, days=7):
        """获取用户签到历史记录"""
        return self.records_handler.get_checkin_history(
            group_id, user_id, user_type, days
        )

    def get_consecutive_ranking(self, group_id, user_type, limit=10):
        """获取连续签到天数排行榜"""
        return self.user_handler.get_consecutive_ranking(group_id, user_type, limit)

    # ===== 年份和统计相关方法 =====
    def get_available_years(self):
        """获取所有可用的年份数据库"""
        try:
            available_years = []
            for filename in os.listdir(self.data_dir):
                if filename.startswith("sar_") and filename.endswith(".db"):
                    year_str = filename[4:-3]  # 去掉 "sar_" 和 ".db"
                    try:
                        year = int(year_str)
                        available_years.append(year)
                    except ValueError:
                        continue

            available_years.sort(reverse=True)  # 按年份倒序排列
            return {
                "code": 200,
                "data": available_years,
                "message": f"获取可用年份成功，共{len(available_years)}个年份",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"获取可用年份失败: {str(e)}"}

    def get_yearly_summary(self, group_id):
        """获取当前年份的群组总结信息"""
        try:
            # 获取总体统计
            stats_result = self.get_total_stats(group_id)
            if stats_result["code"] != 200:
                return stats_result

            # 获取活跃用户数量 - 通过用户处理器获取
            active_users_query = """
                SELECT COUNT(DISTINCT user_id) as active_users
                FROM user_checkin 
                WHERE group_id = ?
            """
            active_users_result = self.user_handler.execute_query(
                active_users_query, (group_id,)
            )
            active_users = active_users_result[0][0] if active_users_result else 0

            # 获取总签到次数 - 通过记录处理器获取
            total_checkins = self.records_handler.get_total_checkins_count(group_id)

            return {
                "code": 200,
                "data": {
                    "year": self.year,
                    "group_id": group_id,
                    "active_users": active_users,
                    "total_checkins": total_checkins,
                    "type_stats": stats_result["data"],
                },
                "message": f"获取{self.year}年群组总结成功",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"获取年度总结失败: {str(e)}"}

    # ===== 静态方法 =====
    @staticmethod
    def create_for_year(year):
        """为指定年份创建数据管理器实例"""
        return DataManager(year=year)

    @staticmethod
    def get_user_cross_year_stats(group_id, user_id):
        """获取用户跨年度统计信息"""
        try:
            data_dir = os.path.join("data", MODULE_NAME)
            if not os.path.exists(data_dir):
                return {"code": 404, "data": None, "message": "数据目录不存在"}

            yearly_stats = []
            total_stats = {
                "total_count": 0,
                "total_checkin_days": 0,
                "years_participated": 0,
            }

            # 遍历所有年份的数据库
            for filename in os.listdir(data_dir):
                if filename.startswith("sar_") and filename.endswith(".db"):
                    year_str = filename[4:-3]
                    try:
                        year = int(year_str)
                        with DataManager(year) as dm:
                            user_info = dm.get_user_info(group_id, user_id)
                            if user_info["code"] == 200 and user_info["data"]:
                                user_data = user_info["data"][0]
                                type_name = DatabaseBase.get_type_name(user_data[3])
                                count = user_data[4]
                                total_checkin_days = user_data[7]

                                yearly_stats.append(
                                    {
                                        "year": year,
                                        "type_name": type_name,
                                        "count": count,
                                        "total_checkin_days": total_checkin_days,
                                    }
                                )

                                total_stats["total_count"] += count
                                total_stats["total_checkin_days"] += total_checkin_days
                                total_stats["years_participated"] += 1
                    except (ValueError, Exception):
                        continue

            yearly_stats.sort(key=lambda x: x["year"], reverse=True)

            return {
                "code": 200,
                "data": {"yearly_stats": yearly_stats, "total_stats": total_stats},
                "message": f"获取跨年度统计成功，参与了{len(yearly_stats)}个年份",
            }
        except Exception as e:
            return {
                "code": 500,
                "data": None,
                "message": f"获取跨年度统计失败: {str(e)}",
            }


if __name__ == "__main__":
    # 使用with语句确保数据库连接正确关闭
    with DataManager() as dm:
        print("=" * 70)
        print(f"测试 SunAndRain 数据管理器 - {dm.year}年数据库")
        print(f"数据库文件：{os.path.basename(dm.db_path)}")
        print("=" * 70)

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

        # 测试年份管理功能
        print("\n16. 测试年份管理功能:")
        years_result = dm.get_available_years()
        print("可用年份:", years_result["data"])

        # 测试年度总结
        print("\n17. 测试年度总结:")
        summary_result = dm.get_yearly_summary(123456)
        if summary_result["code"] == 200:
            summary = summary_result["data"]
            print(f"{summary['year']}年群组总结:")
            print(f"  活跃用户: {summary['active_users']}人")
            print(f"  总签到: {summary['total_checkins']}次")
            print(f"  类型统计: {summary['type_stats']}")

        # 测试跨年度统计
        print("\n18. 测试跨年度统计:")
        cross_year_result = DataManager.get_user_cross_year_stats(123456, 987654)
        if cross_year_result["code"] == 200:
            print("跨年度统计:", cross_year_result["message"])
            print("总统计:", cross_year_result["data"]["total_stats"])

        # 测试创建历史年份数据库
        print("\n19. 测试创建历史年份数据库:")
        last_year = dm.year - 1
        print(f"创建{last_year}年数据库测试...")
        with DataManager(last_year) as dm_last_year:
            print(
                f"  {last_year}年数据库文件: {os.path.basename(dm_last_year.db_path)}"
            )
            # 添加一些历史数据
            result = dm_last_year.add_user(123456, 987654, 0)
            if result["code"] == 200:
                print(f"  {last_year}年用户添加成功")

        print("\n" + "=" * 70)
        print("测试完成 - 验证了用户逻辑、重置功能、发言奖励及年份数据库管理")
        print(f"✅ 数据按年份分离，便于历史数据管理和年度统计")
        print("=" * 70)

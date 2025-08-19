import os
from datetime import datetime
from ... import MODULE_NAME, CHECKIN_BASE_REWARD_MIN, CHECKIN_BASE_REWARD_MAX
import random

from .database_base import DatabaseBase
from .user_checkin_handler import UserCheckinHandler
from .checkin_records_handler import CheckinRecordsHandler
from .invite_data_handler import InviteDataHandler
from .daily_speech_handler import DailySpeechHandler
from .lottery_limit_handler import LotteryLimitHandler


class DataManager:
    """主数据管理器类，整合所有处理器"""

    def __init__(self, year=None):
        # 设置年份
        self.year = year if year is not None else datetime.now().year

        # 初始化各个处理器
        self.user_handler = UserCheckinHandler(self.year)
        self.records_handler = CheckinRecordsHandler(self.year)
        self.invite_handler = InviteDataHandler(self.year)
        self.speech_handler = DailySpeechHandler(self.year)
        self.lottery_limit_handler = LotteryLimitHandler(self.year)

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
        try:
            self.invite_handler.__exit__(exc_type, exc_val, exc_tb)
        except:
            pass
        try:
            self.speech_handler.__exit__(exc_type, exc_val, exc_tb)
        except:
            pass
        try:
            self.lottery_limit_handler.__exit__(exc_type, exc_val, exc_tb)
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

    def get_global_ranking(self, user_type, limit=10):
        """获取全服指定类型的排行榜"""
        return self.user_handler.get_global_ranking(user_type, limit)

    def get_all_group_users(self, group_id):
        """获取群组内所有用户的信息"""
        return self.user_handler.get_all_group_users(group_id)

    def delete_user(self, group_id, user_id):
        """删除用户的所有记录"""
        try:
            # 先删除邀请记录
            invite_result = self.invite_handler.delete_user_invite_records(
                group_id, user_id
            )
            invite_deleted = (
                invite_result["data"]["deleted_count"]
                if invite_result["code"] == 200
                else 0
            )

            # 删除签到记录
            records_result = self.records_handler.delete_user_records(group_id, user_id)
            checkin_deleted = (
                records_result["data"]["checkin_records"]
                if records_result["code"] == 200
                else 0
            )

            # 删除发言统计记录
            speech_result = self.speech_handler.delete_user_speech_records(
                group_id, user_id
            )
            speech_deleted = (
                speech_result["data"]["deleted_count"]
                if speech_result["code"] == 200
                else 0
            )

            # 删除抽奖限制记录
            lottery_result = self.lottery_limit_handler.delete_user_lottery_records(
                group_id, user_id
            )
            lottery_deleted = (
                lottery_result["data"]["deleted_count"]
                if lottery_result["code"] == 200
                else 0
            )

            # 最后删除用户信息
            user_result = self.user_handler.delete_user(group_id, user_id)
            user_deleted = (
                user_result["data"]["user_records"] if user_result["code"] == 200 else 0
            )

            total_deleted = (
                invite_deleted
                + checkin_deleted
                + speech_deleted
                + lottery_deleted
                + user_deleted
            )

            if total_deleted > 0:
                return {
                    "code": 200,
                    "data": {
                        "deleted_count": total_deleted,
                        "user_records": user_deleted,
                        "checkin_records": checkin_deleted,
                        "invite_records": invite_deleted,
                        "speech_records": speech_deleted,
                        "lottery_records": lottery_deleted,
                    },
                    "message": f"删除用户成功，删除了{total_deleted}条记录（用户信息:{user_deleted}条，签到记录:{checkin_deleted}条，邀请记录:{invite_deleted}条，发言记录:{speech_deleted}条，抽奖记录:{lottery_deleted}条）",
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
            # 重置邀请记录
            invite_result = self.invite_handler.delete_group_invite_records(group_id)
            invite_deleted = (
                invite_result["data"]["deleted_count"]
                if invite_result["code"] == 200
                else 0
            )

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

            total_deleted = invite_deleted + records_deleted + user_deleted

            return {
                "code": 200,
                "data": {"deleted_count": total_deleted},
                "message": f"重置群组数据成功，删除了{total_deleted}条记录（邀请记录:{invite_deleted}条，签到记录:{records_deleted}条，用户数据:{user_deleted}条）",
            }
        except Exception as e:
            return {"code": 500, "data": None, "message": f"数据库错误: {str(e)}"}

    def get_total_stats(self, group_id):
        """获取群组的统计信息"""
        return self.user_handler.get_total_stats(group_id)

    # ===== 每日发言奖励相关方法 =====
    def check_daily_speech_limit(
        self, group_id, user_id, user_type, reward_amount, daily_limit
    ):
        """检查是否超过每日发言奖励上限"""
        return self.speech_handler.check_daily_reward_limit(
            group_id, user_id, user_type, reward_amount, daily_limit
        )

    def add_speech_reward_record(self, group_id, user_id, user_type, reward_amount):
        """添加发言奖励记录"""
        return self.speech_handler.add_speech_reward(
            group_id, user_id, user_type, reward_amount
        )

    def get_daily_speech_stats(self, group_id, user_id, user_type, date=None):
        """获取用户指定日期的发言统计"""
        return self.speech_handler.get_daily_speech_stats(
            group_id, user_id, user_type, date
        )

    def get_user_speech_history(self, group_id, user_id, user_type, days=7):
        """获取用户最近几天的发言统计历史"""
        return self.speech_handler.get_user_speech_history(
            group_id, user_id, user_type, days
        )

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
                base_reward = random.randint(
                    CHECKIN_BASE_REWARD_MIN, CHECKIN_BASE_REWARD_MAX
                )

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

    # ===== 邀请相关方法 =====
    def add_invite_record(self, group_id, operator_id, user_id, invite_time=None):
        """添加邀请记录"""
        return self.invite_handler.add_invite_record(
            group_id, operator_id, user_id, invite_time
        )

    def process_invite_reward(
        self, group_id, operator_id, user_id, reward_amount, invite_time=None
    ):
        """处理邀请入群：添加邀请记录并奖励操作者指定数量的数值"""
        try:
            # 1. 首先检查操作者是否已经选择了类型
            operator_info = self.get_user_info(group_id, operator_id)
            if operator_info["code"] != 200 or not operator_info["data"]:
                return {
                    "code": 404,
                    "data": None,
                    "message": f"❌ 邀请者不存在！",
                }

            operator_data = operator_info["data"][0]
            operator_type = operator_data[3]  # type字段
            type_name = DatabaseBase.get_type_name(operator_type)
            current_count = operator_data[4]  # count字段

            # 2. 添加邀请记录
            invite_result = self.add_invite_record(
                group_id, operator_id, user_id, invite_time
            )
            if invite_result["code"] != 200:
                return {
                    "code": 500,
                    "data": None,
                    "message": f"❌ 添加邀请记录失败：{invite_result['message']}",
                }

            # 3. 奖励操作者指定数量的数值
            reward_result = self.update_user_count(
                group_id, operator_id, operator_type, reward_amount
            )
            if reward_result["code"] != 200:
                # 如果奖励失败，尝试删除刚才添加的邀请记录
                try:
                    record_id = invite_result["data"]["id"]
                    self.delete_invite_record(record_id)
                except:
                    pass  # 删除失败也不影响主要逻辑

                return {
                    "code": 500,
                    "data": None,
                    "message": f"❌ 奖励发放失败：{reward_result['message']}",
                }

            new_total_count = reward_result["data"]["count"]
            invite_record_id = invite_result["data"]["id"]

            return {
                "code": 200,
                "data": {
                    "invite_record_id": invite_record_id,
                    "operator_id": operator_id,
                    "invited_user_id": user_id,
                    "operator_type": operator_type,
                    "type_name": type_name,
                    "reward_amount": reward_amount,
                    "previous_count": current_count,
                    "new_total_count": new_total_count,
                    "invite_time": invite_result["data"]["invite_time"],
                },
                "message": f"🎉 邀请成功！\n"
                f"👤 邀请者：{operator_id}\n"
                f"🆕 新成员：{user_id}\n"
                f"⏰ 邀请时间：{invite_result['data']['invite_time']}\n"
                f"🎁 邀请奖励：{reward_amount}个{type_name}\n"
                f"📊 当前拥有：{new_total_count}个{type_name}（+{reward_amount}）\n",
            }

        except Exception as e:
            return {
                "code": 500,
                "data": None,
                "message": f"❌ 处理邀请奖励失败: {str(e)}\n⚠️ 请稍后重试或联系管理员",
            }

    def get_invite_records_by_group(self, group_id, limit=50, offset=0):
        """获取群组的邀请记录"""
        return self.invite_handler.get_invite_records_by_group(group_id, limit, offset)

    def get_invite_records_by_operator(self, group_id, operator_id, limit=50):
        """获取特定操作者的邀请记录"""
        return self.invite_handler.get_invite_records_by_operator(
            group_id, operator_id, limit
        )

    def get_invite_records_by_user(self, group_id, user_id, limit=50):
        """获取特定用户被邀请的记录"""
        return self.invite_handler.get_invite_records_by_user(group_id, user_id, limit)

    def get_operator_invite_stats(self, group_id, operator_id):
        """获取操作者的邀请统计信息"""
        return self.invite_handler.get_operator_invite_stats(group_id, operator_id)

    def get_group_invite_stats(self, group_id):
        """获取群组邀请统计信息"""
        return self.invite_handler.get_group_invite_stats(group_id)

    def get_top_inviters(self, group_id, limit=10):
        """获取群组内邀请次数最多的用户排行榜"""
        return self.invite_handler.get_top_inviters(group_id, limit)

    def delete_invite_record(self, record_id):
        """删除指定的邀请记录"""
        return self.invite_handler.delete_invite_record(record_id)

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

            # 获取邀请统计 - 通过邀请处理器获取
            invite_stats_result = self.get_group_invite_stats(group_id)
            invite_stats = (
                invite_stats_result["data"]
                if invite_stats_result["code"] == 200
                else {}
            )

            return {
                "code": 200,
                "data": {
                    "year": self.year,
                    "group_id": group_id,
                    "active_users": active_users,
                    "total_checkins": total_checkins,
                    "type_stats": stats_result["data"],
                    "invite_stats": invite_stats,
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

    # ===== 抽奖限制相关方法 =====
    def check_lottery_cooldown(self, group_id, user_id, user_type, cooldown_minutes=1):
        """检查用户抽奖冷却时间"""
        return self.lottery_limit_handler.check_lottery_cooldown(
            group_id, user_id, user_type, cooldown_minutes
        )

    def update_lottery_time(self, group_id, user_id, user_type, lottery_time=None):
        """更新用户抽奖时间"""
        return self.lottery_limit_handler.update_lottery_time(
            group_id, user_id, user_type, lottery_time
        )

    def get_user_lottery_history(self, group_id, user_id, user_type=None, limit=10):
        """获取用户抽奖历史记录"""
        return self.lottery_limit_handler.get_user_lottery_history(
            group_id, user_id, user_type, limit
        )

    def clean_old_lottery_records(self, days_to_keep=7):
        """清理旧的抽奖记录"""
        return self.lottery_limit_handler.clean_old_records(days_to_keep)

    def delete_user_lottery_records(self, group_id, user_id):
        """删除指定用户的所有抽奖限制记录"""
        return self.lottery_limit_handler.delete_user_lottery_records(group_id, user_id)

    def get_group_lottery_stats(self, group_id, hours=24):
        """获取群组内指定时间段的抽奖统计"""
        return self.lottery_limit_handler.get_group_lottery_stats(group_id, hours)

    # ===== 每日抽奖次数限制相关方法 =====
    def check_daily_lottery_limit(self, group_id, user_id, user_type, daily_limit):
        """检查今日抽奖次数是否未超限"""
        return self.lottery_limit_handler.check_daily_lottery_limit(
            group_id, user_id, user_type, daily_limit
        )

    def increment_daily_lottery_count(self, group_id, user_id, user_type):
        """抽奖成功后将今日抽奖次数+1"""
        return self.lottery_limit_handler.increment_daily_lottery_count(
            group_id, user_id, user_type
        )

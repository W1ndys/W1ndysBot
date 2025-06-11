"""
群组管理模块
"""

import logger
from . import MODULE_NAME, GROUP_RECALL_COMMAND
from api.group import set_group_ban, set_group_kick, set_group_whole_ban
from api.message import send_group_msg, delete_msg
from api.generate import generate_text_message, generate_at_message
import re
import random
from .data_manager import DataManager


class GroupManagerHandle:
    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.group_id = msg.get("group_id", "")
        self.user_id = msg.get("user_id", "")
        self.role = msg.get("role", "")
        self.raw_message = msg.get("raw_message", "")
        self.message_id = msg.get("message_id", "")

    async def handle_mute(self):
        """
        处理群组禁言
        支持以下格式：
            {command}[CQ:at,qq={user_id}] [CQ:at,qq={user_id}] ... 禁言时间(分钟)  # 多个at
            {command} {user_id} {user_id} ... 禁言时间(分钟)  # 多个QQ号
            {command}[CQ:at,qq={user_id}] {user_id} ... 禁言时间(分钟)  # at和QQ号混用
        """
        try:
            # 匹配所有 at 格式
            at_pattern = r"\[CQ:at,qq=(\d+)\]"
            at_matches = re.finditer(at_pattern, self.raw_message)
            target_user_ids = [match.group(1) for match in at_matches]

            # 处理QQ号格式
            message_parts = self.raw_message.split()
            # 去掉命令部分,剩下的应该是QQ号和时间
            parts = [part for part in message_parts[1:] if part.isdigit()]

            # 如果最后一个数字小于1000,认为是时间参数
            if parts and int(parts[-1]) < 1000:
                mute_time = int(parts[-1])
                # 移除时间参数,剩下的都是QQ号
                parts = parts[:-1]
            else:
                mute_time = 5  # 默认5分钟

            # 添加QQ号格式的目标
            target_user_ids.extend(parts)

            # 批量执行禁言操作
            for target_user_id in target_user_ids:
                await set_group_ban(
                    self.websocket,
                    self.group_id,
                    target_user_id,
                    mute_time * 60,
                )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]禁言操作失败: {e}")

    async def _update_mute_record(self, user_id, duration):
        """
        更新禁言记录并通报记录

        参数:
            user_id: QQ号
            duration: 禁言时长(秒)
        """
        try:
            with DataManager() as dm:
                result = dm.update_mute_record(self.group_id, user_id, duration)
                (
                    is_new_record,
                    break_personal_record,
                    break_group_record,
                    old_duration,
                ) = result

                # 如果打破记录，发送通报消息
                if break_personal_record:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_at_message(user_id),
                            generate_text_message(
                                f"恭喜 {user_id} 打破个人禁言记录！\n"
                                f"旧记录：{old_duration} 秒\n"
                                f"新记录：{duration} 秒"
                            ),
                        ],
                        note="del_msg=60",
                    )

                if break_group_record:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_at_message(user_id),
                            generate_text_message(
                                f"恭喜用户 {user_id} 打破本群今日禁言最高记录！\n"
                                f"时长：{duration} 秒"
                            ),
                        ],
                        note="del_msg=60",
                    )

                # 获取并显示群内今日禁言排行榜
                top_user = dm.get_group_today_top_mute_user(self.group_id)
                if top_user:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_at_message(top_user[0]),
                            generate_text_message(
                                f"本群今日禁言之王：{top_user[0]}\n"
                                f"禁言时长：{top_user[1]} 秒"
                            ),
                        ],
                        note="del_msg=60",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]更新禁言记录失败: {e}")

    async def handle_unmute(self):
        """
        处理群组解禁
        支持以下格式：
            {command}[CQ:at,qq={user_id}] [CQ:at,qq={user_id}] ...  # 多个at
            {command} {user_id} {user_id} ...  # 多个QQ号
            {command}[CQ:at,qq={user_id}] {user_id} ...  # at和QQ号混用
        """
        try:
            # 匹配所有 at 格式
            at_pattern = r"\[CQ:at,qq=(\d+)\]"
            at_matches = re.finditer(at_pattern, self.raw_message)
            target_user_ids = [match.group(1) for match in at_matches]

            # 处理QQ号格式
            message_parts = self.raw_message.split()
            # 去掉命令和at部分,剩下的应该都是QQ号
            qq_numbers = [part for part in message_parts[1:] if part.isdigit()]
            target_user_ids.extend(qq_numbers)

            # 批量执行解禁操作
            for target_user_id in target_user_ids:
                await set_group_ban(self.websocket, self.group_id, target_user_id, 0)

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]解禁操作失败: {e}")

    async def handle_kick(self):
        """
        处理群组踢出
        支持以下格式：
            {command}[CQ:at,qq={user_id}] [CQ:at,qq={user_id}] ...  # 多个at
            {command} {user_id} {user_id} ...  # 多个QQ号
            {command}[CQ:at,qq={user_id}] {user_id} ...  # at和QQ号混用
        """
        try:
            # 匹配所有 at 格式
            at_pattern = r"\[CQ:at,qq=(\d+)\]"
            at_matches = re.finditer(at_pattern, self.raw_message)
            target_user_ids = [match.group(1) for match in at_matches]

            # 处理QQ号格式
            message_parts = self.raw_message.split()
            # 去掉命令和at部分,剩下的应该都是QQ号
            qq_numbers = [part for part in message_parts[1:] if part.isdigit()]
            target_user_ids.extend(qq_numbers)

            # 批量执行踢出操作
            for target_user_id in target_user_ids:
                await set_group_kick(
                    self.websocket, self.group_id, target_user_id, False
                )
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_text_message(f"已踢出用户 {target_user_id}"),
                    ],
                    note="del_msg=30",
                )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]踢出操作失败: {e}")

    async def handle_all_mute(self):
        """
        处理群组全员禁言
        """
        try:
            await set_group_whole_ban(self.websocket, self.group_id, True)
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]全员禁言操作失败: {e}")

    async def handle_all_unmute(self):
        """
        处理群组全员解禁
        """
        try:
            await set_group_whole_ban(self.websocket, self.group_id, False)
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]全员解禁操作失败: {e}")

    async def handle_recall(self):
        """
        处理群组撤回
        格式：[CQ:reply,id={message_id}] 任意内容 {command}
        """
        try:
            # 匹配撤回格式
            pattern = rf"\[CQ:reply,id=(\d+)\].*{GROUP_RECALL_COMMAND}"
            match = re.search(pattern, self.raw_message)
            if match:
                message_id = match.group(1)

            # 执行撤回操作
            await delete_msg(self.websocket, message_id)

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]撤回操作失败: {e}")

    async def handle_ban_me(self):
        """
        处理群组封禁自己
        """
        try:
            ban_duration = random.randint(60, 600)  # 随机60-600秒(1-10分钟)
            await set_group_ban(
                self.websocket, self.group_id, self.user_id, ban_duration
            )
            # 更新禁言记录
            await self._update_mute_record(self.user_id, ban_duration)

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]封禁自己操作失败: {e}")

    async def handle_mute_rank(self):
        """
        处理禁言排行榜查询
        """
        try:
            with DataManager() as dm:
                # 获取群内今日禁言排行榜
                top_user = dm.get_group_today_top_mute_user(self.group_id)

                # 获取用户自己的今日禁言时长
                user_duration = dm.get_user_today_mute_duration(
                    self.group_id, self.user_id
                )

                # 获取全局禁言记录
                global_top = dm.get_global_top_mute_user()

                # 组装消息
                message = "【禁言排行榜】\n"

                if top_user:
                    message += f"本群今日禁言之王：{top_user[0]}\n"
                    message += f"禁言时长：{top_user[1] // 60} 分钟\n\n"
                else:
                    message += "本群今日暂无禁言记录\n\n"

                if user_duration > 0:
                    message += f"您今日的禁言时长：{user_duration // 60} 分钟\n\n"
                else:
                    message += "您今日尚未被禁言\n\n"

                if global_top:
                    message += f"全服务器禁言记录保持者：\n"
                    message += f"群号：{global_top[0]}\n"
                    message += f"用户：{global_top[1]}\n"
                    message += f"日期：{global_top[2]}\n"
                    message += f"时长：{global_top[3] // 60} 分钟"
                else:
                    message += "全服务器暂无禁言记录"

                # 发送消息
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [generate_text_message(message)],
                    note="del_msg=60",
                )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]查询禁言排行榜失败: {e}")

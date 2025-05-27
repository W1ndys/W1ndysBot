"""
群组管理模块
"""

import logger
from . import MODULE_NAME, GROUP_RECALL_COMMAND
from api.group import set_group_ban, set_group_kick, set_group_whole_ban
from api.message import send_group_msg, delete_msg
from api.generate import generate_reply_message, generate_text_message
import re


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

            if not target_user_ids:
                raise ValueError(
                    "格式错误，请使用 '@用户 时间' 或 'QQ号 时间' 的格式，支持多个用户"
                )

            # 检查所有QQ号是否有效
            for user_id in target_user_ids:
                if not user_id.isdigit():
                    raise ValueError(f"无效的QQ号: {user_id}")

            # 批量执行禁言操作
            for target_user_id in target_user_ids:
                await set_group_ban(
                    self.websocket,
                    self.group_id,
                    target_user_id,
                    mute_time * 60,
                )

        except Exception as e:
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(f"禁言操作失败: {str(e)}"),
                ],
            )
            logger.error(f"[{MODULE_NAME}]禁言操作失败: {e}")

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

            if not target_user_ids:
                raise ValueError(
                    "格式错误，请使用 '@用户' 或 'QQ号' 的格式，支持多个用户"
                )

            # 检查所有QQ号是否有效
            for user_id in target_user_ids:
                if not user_id.isdigit():
                    raise ValueError(f"无效的QQ号: {user_id}")

            # 批量执行解禁操作
            for target_user_id in target_user_ids:
                await set_group_ban(self.websocket, self.group_id, target_user_id, 0)

        except Exception as e:
            await self.send_error_message(f"解禁操作失败: {str(e)}")
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

            if not target_user_ids:
                raise ValueError(
                    "格式错误，请使用 '@用户' 或 'QQ号' 的格式，支持多个用户"
                )

            # 批量执行踢出操作
            for target_user_id in target_user_ids:
                await set_group_kick(
                    self.websocket, self.group_id, target_user_id, False
                )

            # 发送成功消息
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(
                        f"已成功踢出用户：{'、'.join(target_user_ids)}"
                    ),
                ],
                note="del_msg=10",
            )

        except Exception as e:
            await self.send_error_message(f"踢出操作失败: {str(e)}")
            logger.error(f"[{MODULE_NAME}]踢出操作失败: {e}")

    async def handle_all_mute(self):
        """
        处理群组全员禁言
        """
        try:
            await set_group_whole_ban(self.websocket, self.group_id, True)
        except Exception as e:
            await self.send_error_message(f"全员禁言操作失败: {str(e)}")
            logger.error(f"[{MODULE_NAME}]全员禁言操作失败: {e}")

    async def handle_all_unmute(self):
        """
        处理群组全员解禁
        """
        try:
            await set_group_whole_ban(self.websocket, self.group_id, False)
        except Exception as e:
            await self.send_error_message(f"全员解禁操作失败: {str(e)}")
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
            else:
                raise ValueError("未找到消息ID")

            # 提取 message_id
            message_id = re.search(r"\[CQ:reply,id=(\d+)\]", self.raw_message)
            if message_id:
                message_id = message_id.group(1)
            else:
                raise ValueError("未找到消息ID")

            # 执行撤回操作
            await delete_msg(self.websocket, message_id)

        except Exception as e:
            await self.send_error_message(f"撤回操作失败: {str(e)}")
            logger.error(f"[{MODULE_NAME}]撤回操作失败: {e}")

    async def send_error_message(self, error_text):
        """
        发送错误消息
        """
        reply_message = generate_reply_message(self.message_id)
        text_message = generate_text_message(f"[{MODULE_NAME}]错误: {error_text}")
        await send_group_msg(
            self.websocket,
            self.group_id,
            [reply_message, text_message],
        )

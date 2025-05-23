"""
群组管理模块
"""

import logger
from . import MODULE_NAME
from api.group import set_group_ban
from api.message import send_group_msg
from api.generate import generate_reply_message, generate_text_message
import re


class GroupManager:
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
        两种格式：
            {command}[CQ:at,qq={user_id}] 禁言时间(分钟)
            {command} {user_id} 禁言时间(分钟)
        """
        try:
            # 使用正则提取被禁言用户和禁言时间

            # 提取 at 消息中的 QQ 号
            at_pattern = r"\[CQ:at,qq=(\d+)\]"
            at_match = re.search(at_pattern, self.raw_message)

            # 提取禁言时间
            time_pattern = r"(\d+)"
            time_matches = re.findall(time_pattern, self.raw_message)

            if at_match:
                # 使用 at 方式
                target_user_id = at_match.group(1)
                # 如果有多个数字，第一个是QQ号，第二个才是时间
                if len(time_matches) > 1:
                    mute_time = int(time_matches[1])
                else:
                    mute_time = 5  # 默认5分钟
            else:
                # 使用 QQ号 方式
                message_parts = self.raw_message.split()
                if len(message_parts) >= 2:
                    # 去掉命令部分，第一个参数应该是QQ号
                    target_user_id = message_parts[1]
                    if not target_user_id.isdigit():
                        raise ValueError("无效的QQ号")

                    # 检查是否有时间参数
                    if len(message_parts) >= 3 and message_parts[2].isdigit():
                        mute_time = int(message_parts[2])
                    else:
                        mute_time = 5  # 默认5分钟
                else:
                    raise ValueError(
                        "格式错误，请使用 '@用户 时间' 或 'QQ号 时间' 的格式"
                    )

            # 执行禁言操作
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
        两种格式：
            {command}[CQ:at,qq={user_id}]
            {command} {user_id}
        """
        try:
            # 实现解禁逻辑
            # 匹配 at 格式
            at_pattern = r"\[CQ:at,qq=(\d+)\]"
            at_match = re.search(at_pattern, self.raw_message)

            if at_match:
                # 使用 at 方式
                target_user_id = at_match.group(1)
            else:
                # 使用 QQ号 方式
                message_parts = self.raw_message.split()
                if len(message_parts) >= 2:
                    # 去掉命令部分，第一个参数应该是QQ号
                    target_user_id = message_parts[1]
                    if not target_user_id.isdigit():
                        raise ValueError("无效的QQ号")
                else:
                    raise ValueError("格式错误，请使用 '@用户' 或 'QQ号' 的格式")

            # 执行解禁操作（禁言时间设为0表示解除禁言）
            await set_group_ban(self.websocket, self.group_id, target_user_id, 0)

        except Exception as e:
            await self.send_error_message(f"解禁操作失败: {str(e)}")
            logger.error(f"[{MODULE_NAME}]解禁操作失败: {e}")

    async def handle_kick(self):
        """
        处理群组踢出
        """
        try:
            # 实现踢出逻辑
            pass
        except Exception as e:
            await self.send_error_message(f"踢出操作失败: {str(e)}")
            logger.error(f"[{MODULE_NAME}]踢出操作失败: {e}")

    async def handle_all_mute(self):
        """
        处理群组全员禁言
        """
        try:
            # 实现全员禁言逻辑
            pass
        except Exception as e:
            await self.send_error_message(f"全员禁言操作失败: {str(e)}")
            logger.error(f"[{MODULE_NAME}]全员禁言操作失败: {e}")

    async def handle_all_unmute(self):
        """
        处理群组全员解禁
        """
        try:
            # 实现全员解禁逻辑
            pass
        except Exception as e:
            await self.send_error_message(f"全员解禁操作失败: {str(e)}")
            logger.error(f"[{MODULE_NAME}]全员解禁操作失败: {e}")

    async def handle_recall(self):
        """
        处理群组撤回
        """
        try:
            # 实现撤回逻辑
            pass
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

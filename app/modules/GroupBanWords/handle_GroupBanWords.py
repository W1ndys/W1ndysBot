from datetime import datetime
from . import (
    MODULE_NAME,
    ADD_BAN_WORD_COMMAND,
    DELETE_BAN_WORD_COMMAND,
    BAN_WORD_WEIGHT_MAX,
    BAN_WORD_DURATION,
)
from .data_manager_words import DataManager
from logger import logger
from core.auth import is_group_admin
from api.message import send_group_msg, delete_msg
from api.generate import (
    generate_text_message,
    generate_reply_message,
    generate_at_message,
)
from api.group import set_group_ban


class GroupBanWordsHandler:
    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.sub_type = msg.get("sub_type", "")  # 子类型，只有normal
        self.group_id = str(msg.get("group_id", ""))  # 群号
        self.message_id = str(msg.get("message_id", ""))  # 消息ID
        self.user_id = str(msg.get("user_id", ""))  # 发送者QQ号
        self.message = msg.get("message", {})  # 消息段数组
        self.raw_message = msg.get("raw_message", "")  # 原始消息
        self.sender = msg.get("sender", {})  # 发送者信息
        self.nickname = self.sender.get("nickname", "")  # 昵称
        self.card = self.sender.get("card", "")  # 群名片
        self.role = self.sender.get("role", "")  # 群身份
        self.data_manager = DataManager(self.group_id)

    async def add_ban_word(self):
        try:
            # 检测是否为管理员
            if not is_group_admin(self.role):
                return
            # 过滤命令
            ban_word = self.raw_message.lstrip(ADD_BAN_WORD_COMMAND).strip()
            # 获取违禁词和权重
            ban_word, weight = ban_word.split(" ")
            # 添加违禁词
            is_success = self.data_manager.add_word(ban_word, weight)
            if not is_success:
                return
            # 发送成功消息
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(f"添加违禁词成功: {ban_word} 权重: {weight}"),
                ],
                note="del_msg=10",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]添加违禁词失败: {e}")

    async def delete_ban_word(self):
        try:
            # 检测是否为管理员
            if not is_group_admin(self.role):
                return
            # 过滤命令
            ban_word = self.raw_message.lstrip(DELETE_BAN_WORD_COMMAND).strip()
            # 删除违禁词
            is_success = self.data_manager.delete_word(ban_word)
            if not is_success:
                return
            # 发送成功消息
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(f"删除违禁词成功: {ban_word}"),
                ],
                note="del_msg=10",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]删除违禁词失败: {e}")

    async def calc_message_weight(self):
        try:
            weight = self.data_manager.calc_message_weight(self.raw_message)
            if weight > BAN_WORD_WEIGHT_MAX:
                return True
            return False
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]计算违禁词权重失败: {e}")
            return 0

    async def handle(self):
        try:

            # 添加违禁词
            if self.raw_message.startswith(ADD_BAN_WORD_COMMAND):
                await self.add_ban_word()
                return
            # 删除违禁词
            if self.raw_message.startswith(DELETE_BAN_WORD_COMMAND):
                await self.delete_ban_word()
                return

            # 检测违禁词
            if await self.calc_message_weight():
                # 返回True，表示违规
                await set_group_ban(
                    self.websocket,
                    self.group_id,
                    self.user_id,
                    BAN_WORD_DURATION,
                )
                # 设置用户状态
                self.data_manager.set_user_status(self.user_id, "ban")
                # 撤回消息
                await delete_msg(self.websocket, self.message_id)
                # 发送消息
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_at_message(self.user_id),
                        generate_text_message("请勿发送违禁消息，如误封请联系管理员"),
                    ],
                    note="del_msg=20",
                )
                return
            else:
                # 检测用户状态
                user_status = self.data_manager.get_user_status(self.user_id)
                if user_status == "ban":
                    # 撤回消息
                    await delete_msg(self.websocket, self.message_id)
                    return
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理违禁词失败: {e}")

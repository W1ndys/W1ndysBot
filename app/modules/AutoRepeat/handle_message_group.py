from . import MODULE_NAME, SWITCH_NAME, MENU_COMMAND
import logger
from core.switchs import is_group_switch_on, handle_module_group_switch
from core.auth import is_system_owner
from api.message import send_group_msg_with_cq
from datetime import datetime
from core.menu_manager import MenuManager
import random


class GroupMessageHandler:
    """群消息处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
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

        self.repeat_probability = 0.1  # 随机概率，百分之10

    async def handle(self):
        """
        处理群消息
        """
        try:
            if self.raw_message.lower() == SWITCH_NAME.lower():
                # 鉴权
                if not is_system_owner(self.user_id):
                    logger.error(f"[{MODULE_NAME}]{self.user_id}无权限切换群聊开关")
                    return
                await handle_module_group_switch(
                    MODULE_NAME,
                    self.websocket,
                    self.group_id,
                    self.message_id,
                )
                return

            # 处理菜单命令（无视开关状态）
            if self.raw_message.lower() == (SWITCH_NAME + MENU_COMMAND).lower():
                menu_text = MenuManager.get_module_commands_text(MODULE_NAME)
                await send_group_msg_with_cq(
                    self.websocket,
                    self.group_id,
                    self.raw_message,
                )
                return

            # 如果没开启群聊开关，则不处理
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

            # 忽略的字符数组单独摘出来
            ignore_words = [
                "[CQ:video,file=",
                "[CQ:json,data=",
            ]

            # 如果消息中包含下面这些字符，则不处理
            if any(word in self.raw_message for word in ignore_words):
                return

            # 随机复读消息内容
            if random.random() < self.repeat_probability:
                await send_group_msg_with_cq(
                    self.websocket, self.group_id, self.raw_message, note="del_msg=120"
                )
                logger.info(
                    f"[{MODULE_NAME}]群聊复读: {self.group_id} {self.nickname}({self.user_id})"
                )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

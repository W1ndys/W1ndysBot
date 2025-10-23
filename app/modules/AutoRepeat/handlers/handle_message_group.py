from .. import MODULE_NAME, SWITCH_NAME
from core.menu_manager import MENU_COMMAND
from logger import logger
from core.switchs import is_group_switch_on, handle_module_group_switch
from utils.auth import is_group_admin, is_system_admin
from api.message import send_group_msg_with_cq, group_poke
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
        self.poke_probability = 0.1  # 随机概率，百分之10
        self.max_message_length = 25  # 最大消息长度，超过此长度不进行随机复读

    async def handle(self):
        """
        处理群消息
        """
        try:
            if self.raw_message.lower() == SWITCH_NAME.lower():
                # 鉴权
                if not is_group_admin(self.role) and not is_system_admin(self.user_id):
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
            if self.raw_message.lower() == f"{SWITCH_NAME}{MENU_COMMAND}".lower():
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

            # 随机戳一戳上一个说话的人
            if random.random() < self.poke_probability:
                await group_poke(self.websocket, self.group_id, self.user_id)
                logger.info(
                    f"[{MODULE_NAME}]群聊戳一戳: {self.group_id} {self.nickname}({self.user_id})"
                )

            # 忽略的字符数组单独摘出来
            ignore_words = [
                "[CQ:video,file=",
                "[CQ:json,data=",
                "[CQ:file,file=",
            ]

            # 如果消息中包含下面这些字符，则不处理
            if any(word in self.raw_message for word in ignore_words):
                return

            # 检查消息长度，超过最大长度则不处理
            if len(self.raw_message) > self.max_message_length:
                return

            # 随机复读消息内容
            if random.random() < self.repeat_probability:
                # 检查是否为纯文本消息
                is_pure_text = (
                    all(segment.get("type") == "text" for segment in self.message)
                    if isinstance(self.message, list)
                    else False
                )

                repeat_message = self.raw_message

                # 如果是纯文本且随机到50%概率，则打乱顺序
                if is_pure_text and random.random() < 0.5:
                    # 将文本转换为字符列表并打乱
                    chars = list(self.raw_message)
                    random.shuffle(chars)
                    repeat_message = "".join(chars)
                    logger.info(
                        f"[{MODULE_NAME}]群聊打乱复读: {self.group_id} {self.nickname}({self.user_id})"
                    )
                else:
                    logger.info(
                        f"[{MODULE_NAME}]群聊原样复读: {self.group_id} {self.nickname}({self.user_id})"
                    )

                await send_group_msg_with_cq(
                    self.websocket, self.group_id, repeat_message
                )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

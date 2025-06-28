from . import MODULE_NAME, SWITCH_NAME, UNBAN_WORD_COMMAND, KICK_BAN_WORD_COMMAND
from core.menu_manager import MENU_COMMAND
import logger
from core.switchs import is_private_switch_on, handle_module_private_switch
from api.message import send_private_msg
from utils.generate import generate_text_message, generate_reply_message
from datetime import datetime
from .data_manager_words import DataManager
from core.auth import is_system_admin
from core.menu_manager import MenuManager
from .handle_GroupBanWords import GroupBanWordsHandler


class PrivateMessageHandler:
    """私聊消息处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.sub_type = msg.get("sub_type", "")  # 子类型,friend/group
        self.user_id = str(msg.get("user_id", ""))  # 发送者QQ号
        self.message_id = str(msg.get("message_id", ""))  # 消息ID
        self.message = msg.get("message", {})  # 消息段数组
        self.raw_message = msg.get("raw_message", "")  # 原始消息
        self.sender = msg.get("sender", {})  # 发送者信息
        self.nickname = self.sender.get("nickname", "")  # 昵称

    async def handle(self):
        """
        处理私聊消息
        """
        try:
            if self.raw_message.lower() == SWITCH_NAME.lower():
                # 鉴权
                if not is_system_admin(self.user_id):
                    logger.error(f"[{MODULE_NAME}]{self.user_id}无权限切换私聊开关")
                    return
                await handle_module_private_switch(
                    MODULE_NAME,
                    self.websocket,
                    self.user_id,
                    self.message_id,
                )
                return

            # 处理菜单命令（无视开关状态）
            if self.raw_message.lower() == f"{SWITCH_NAME}{MENU_COMMAND}".lower():
                menu_text = MenuManager.get_module_commands_text(MODULE_NAME)
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(menu_text),
                    ],
                    note="del_msg=30",
                )
                return

            # 如果没开启私聊开关，则不处理
            if not is_private_switch_on(MODULE_NAME):
                return

            # 实例化GroupBanWords
            group_ban_words = GroupBanWordsHandler(self.websocket, self.msg)
            # 处理管理员解封 踢出
            if self.raw_message.lower().startswith(UNBAN_WORD_COMMAND.lower()):
                await group_ban_words.handle_unban_word()
            elif self.raw_message.lower().startswith(KICK_BAN_WORD_COMMAND.lower()):
                await group_ban_words.handle_kick_ban_word()

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理私聊消息失败: {e}")

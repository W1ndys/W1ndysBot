from . import MODULE_NAME, SWITCH_NAME, MENU_COMMAND, COMMANDS
import logger
from core.switchs import is_private_switch_on, toggle_private_switch
from api.message import send_private_msg
from api.generate import generate_reply_message, generate_text_message
from datetime import datetime
from .data_manager import DataManager


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

    async def handle_module_switch(self):
        """
        处理模块开关命令
        """
        try:
            switch_status = toggle_private_switch(MODULE_NAME)
            switch_status = "开启" if switch_status else "关闭"
            reply_message = generate_reply_message(self.message_id)
            text_message = generate_text_message(
                f"[{MODULE_NAME}]私聊开关已切换为【{switch_status}】"
            )
            await send_private_msg(
                self.websocket,
                self.user_id,
                [reply_message, text_message],
                note="del_msg=10",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理模块开关命令失败: {e}")

    async def handle_menu(self):
        """
        处理菜单命令
        """
        try:
            reply_message = generate_reply_message(self.message_id)
            menu_text = f"[{MODULE_NAME}]可用命令列表：\n"
            for cmd, desc in COMMANDS.items():
                menu_text += f"- {cmd}: {desc}\n"
            text_message = generate_text_message(menu_text)
            await send_private_msg(
                self.websocket,
                self.user_id,
                [reply_message, text_message],
                note="del_msg=30",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理菜单命令失败: {e}")

    async def handle(self):
        """
        处理私聊消息
        """
        try:
            if self.raw_message.lower() == SWITCH_NAME.lower():
                await self.handle_module_switch()
                return

            # 处理菜单命令（无视开关状态）
            if self.raw_message.lower() == (SWITCH_NAME + MENU_COMMAND).lower():
                await self.handle_menu()
                return

            # 如果没开启私聊开关，则不处理
            if not is_private_switch_on(MODULE_NAME):
                return

            # 新增：根据sub_type判断消息类型
            if self.sub_type == "friend":
                # 处理好友私聊消息
                with DataManager() as dm:
                    # 这里可以进行数据库操作，如：dm.cursor.execute(...)
                    pass
            elif self.sub_type == "group":
                # 处理临时会话消息（如群临时会话）
                with DataManager() as dm:
                    # 这里可以进行数据库操作，如：dm.cursor.execute(...)
                    pass
            else:
                # 其他类型的私聊消息
                logger.info(
                    f"[{MODULE_NAME}]收到未知sub_type的私聊消息: {self.sub_type}"
                )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理私聊消息失败: {e}")

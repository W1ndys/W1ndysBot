from .. import MODULE_NAME, SWITCH_NAME
from core.menu_manager import MENU_COMMAND
import logger
from utils.auth import is_system_admin
from core.switchs import is_private_switch_on, handle_module_private_switch
from api.message import send_private_msg
from utils.generate import generate_reply_message, generate_text_message
from datetime import datetime
from core.menu_manager import MenuManager
from .message_processor import MessageProcessor


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
        self.group_id = str(msg.get("group_id", ""))  # 群号

    async def handle(self):
        """
        处理私聊消息
        """
        try:
            # 处理模块开关命令
            if await self._handle_switch_command():
                return

            # 处理菜单命令（无视开关状态）
            if await self._handle_menu_command():
                return

            # 如果没开启私聊开关，则不处理
            if not is_private_switch_on(MODULE_NAME):
                return

            # 根据用户权限处理不同类型的消息
            if is_system_admin(self.user_id):
                await self._handle_admin_messages()
            else:
                await self._handle_user_messages()

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理私聊消息失败: {e}")

    async def _handle_switch_command(self):
        """处理模块开关命令"""
        if self.raw_message.lower() == SWITCH_NAME.lower():
            # 鉴权
            if not is_system_admin(self.user_id):
                return False
            await handle_module_private_switch(
                MODULE_NAME,
                self.websocket,
                self.user_id,
                self.message_id,
            )
            return True
        return False

    async def _handle_menu_command(self):
        """处理菜单命令"""
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
            return True
        return False

    async def _handle_admin_messages(self):
        """处理管理员消息"""
        try:
            processor = MessageProcessor(
                self.websocket,
                self.user_id,
                self.message_id,
                self.raw_message,
                self.message,
                self.formatted_time,
                self.nickname,
                self.group_id,
            )

            # 处理测试消息
            if await processor.handle_test_message():
                return

            # 处理好友请求和群请求
            if await processor.handle_request_approval():
                return

            # 处理自动同意好友验证
            if await processor.handle_auto_agree_friend_verify():
                return

            # 处理owner回复转发消息
            if await processor.handle_forward_message_to_owner_reply():
                return
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理管理员消息失败: {e}")

    async def _handle_user_messages(self):
        """处理普通用户消息"""
        try:
            processor = MessageProcessor(
                self.websocket,
                self.user_id,
                self.message_id,
                self.raw_message,
                self.message,
                self.formatted_time,
                self.nickname,
                self.group_id,
            )

            # 转发消息给owner
            await processor.forward_message_to_owner()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理普通用户消息失败: {e}")

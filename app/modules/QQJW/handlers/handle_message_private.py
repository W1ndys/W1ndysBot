from .. import (
    MODULE_NAME,
    SWITCH_NAME,
    ADD_ENABLE_GROUP,
    REMOVE_ENABLE_GROUP,
)
from core.menu_manager import MENU_COMMAND
import logger
from core.switchs import is_private_switch_on, handle_module_private_switch
from api.message import send_private_msg
from utils.generate import generate_text_message, generate_reply_message
from datetime import datetime
from core.menu_manager import MenuManager
from utils.auth import is_system_admin


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

    async def _handle_switch_command(self):
        """
        处理开关命令
        """
        if self.raw_message.lower() == SWITCH_NAME.lower():
            # 鉴权
            if not is_system_admin(self.user_id):
                logger.error(f"[{MODULE_NAME}]{self.user_id}无权限切换私聊开关")
                return True
            await handle_module_private_switch(
                MODULE_NAME,
                self.websocket,
                self.user_id,
                self.message_id,
            )
            return True
        return False

    async def _handle_menu_command(self):
        """
        处理菜单命令（无视开关状态）
        """
        if self.raw_message.lower() == f"{SWITCH_NAME}{MENU_COMMAND}".lower():
            menu_text = MenuManager.get_module_commands_text(MODULE_NAME)
            await send_private_msg(
                self.websocket,
                self.user_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(menu_text),
                ],
            )
            return True
        return False

    async def handle(self):
        """
        处理私聊消息
        """
        try:
            # 处理开关命令
            if await self._handle_switch_command():
                return

            # 处理菜单命令（无视开关状态）
            if await self._handle_menu_command():
                return

            # 如果没开启私聊开关，则不处理
            if not is_private_switch_on(MODULE_NAME):
                return

            # 处理管理员命令
            if is_system_admin(self.user_id):
                if await self._handle_admin_commands():
                    return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理私聊消息失败: {e}")

    async def _handle_admin_commands(self):
        """
        处理管理员相关命令
        """
        try:
            # 处理启用群命令
            if self.raw_message.startswith(ADD_ENABLE_GROUP):
                await self._handle_add_enable_group()
                return True

            # 处理禁用群命令
            if self.raw_message.startswith(REMOVE_ENABLE_GROUP):
                await self._handle_remove_enable_group()
                return True

            return False
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理管理员命令失败: {e}")
            await send_private_msg(
                self.websocket,
                self.user_id,
                generate_text_message(f"处理管理员命令失败: {e}"),
            )
            return False

    async def _handle_add_enable_group(self):
        """
        处理添加启用群命令
        """
        try:
            # 解析群号
            command_parts = self.raw_message.split()
            if len(command_parts) < 2:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    generate_text_message(f"格式错误！请使用：{ADD_ENABLE_GROUP} 群号"),
                )
                return

            group_id = command_parts[1].strip()

            # 添加启用群
            from ..utils.data_manager import DataManager

            with DataManager() as data_manager:
                result = data_manager.add_enable_group(group_id)

            if result["success"]:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    generate_text_message(f"启用群 {group_id} 添加成功"),
                )
                logger.info(
                    f"[{MODULE_NAME}]管理员{self.user_id}添加启用群{group_id}成功"
                )
            else:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    generate_text_message(
                        f"启用群 {group_id} 添加失败: {result['message']}"
                    ),
                )
                logger.error(
                    f"[{MODULE_NAME}]管理员{self.user_id}添加启用群{group_id}失败: {result['message']}"
                )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理添加启用群命令失败: {e}")
            await send_private_msg(
                self.websocket,
                self.user_id,
                generate_text_message(f"添加启用群失败: {e}"),
            )

    async def _handle_remove_enable_group(self):
        """
        处理禁用启用群命令
        """
        try:
            # 解析群号
            command_parts = self.raw_message.split()
            if len(command_parts) < 2:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    generate_text_message(
                        f"格式错误！请使用：{REMOVE_ENABLE_GROUP} 群号"
                    ),
                )
                return

            group_id = command_parts[1].strip()

            # 禁用启用群
            from ..utils.data_manager import DataManager

            with DataManager() as data_manager:
                result = data_manager.disable_enable_group(group_id)

            if result["success"]:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    generate_text_message(f"启用群 {group_id} 禁用成功"),
                )
                logger.info(
                    f"[{MODULE_NAME}]管理员{self.user_id}禁用启用群{group_id}成功"
                )
            else:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    generate_text_message(
                        f"启用群 {group_id} 禁用失败: {result['message']}"
                    ),
                )
                logger.error(
                    f"[{MODULE_NAME}]管理员{self.user_id}禁用启用群{group_id}失败: {result['message']}"
                )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理禁用启用群命令失败: {e}")
            await send_private_msg(
                self.websocket,
                self.user_id,
                generate_text_message(f"禁用启用群失败: {e}"),
            )

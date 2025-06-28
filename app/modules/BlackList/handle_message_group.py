from . import (
    MODULE_NAME,
    BLACKLIST_ADD_COMMAND,
    BLACKLIST_REMOVE_COMMAND,
    BLACKLIST_LIST_COMMAND,
    BLACKLIST_CLEAR_COMMAND,
    GLOBAL_BLACKLIST_ADD_COMMAND,
    GLOBAL_BLACKLIST_REMOVE_COMMAND,
    GLOBAL_BLACKLIST_LIST_COMMAND,
    GLOBAL_BLACKLIST_CLEAR_COMMAND,
    SWITCH_NAME,
)
import logger
from core.menu_manager import MENU_COMMAND
from core.auth import is_group_admin, is_system_admin
from core.switchs import is_group_switch_on, handle_module_group_switch
from api.message import send_group_msg, delete_msg
from api.generate import generate_text_message, generate_reply_message
from api.group import set_group_kick
from datetime import datetime
from .handle_blacklist import BlackListHandle
from .data_manager import BlackListDataManager
from core.menu_manager import MenuManager


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

    async def handle(self):
        """
        处理群消息
        """
        try:
            if self.raw_message.lower() == SWITCH_NAME.lower():
                # 鉴权
                if not is_group_admin(self.role) and not is_system_admin(self.user_id):
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
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(menu_text),
                    ],
                    note="del_msg=30",
                )
                return

            # 如果没开启群聊开关，则不处理
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

            # 首先检查发言用户是否在黑名单中，如果在则进行处理
            if await self.check_blacklisted_user():
                return

            # 处理全局黑名单命令（只有系统管理员可用）
            if is_system_admin(self.user_id):
                blacklist_handler = BlackListHandle(self.websocket, self.msg)

                if self.raw_message.startswith(GLOBAL_BLACKLIST_ADD_COMMAND):
                    await blacklist_handler.add_global_blacklist()
                    return
                elif self.raw_message.startswith(GLOBAL_BLACKLIST_REMOVE_COMMAND):
                    await blacklist_handler.remove_global_blacklist()
                    return
                elif self.raw_message.startswith(GLOBAL_BLACKLIST_LIST_COMMAND):
                    await blacklist_handler.list_global_blacklist()
                    return
                elif self.raw_message.startswith(GLOBAL_BLACKLIST_CLEAR_COMMAND):
                    await blacklist_handler.clear_global_blacklist()
                    return

            # 鉴权，只有管理员才能使用群黑名单
            if not is_group_admin(self.role) and not is_system_admin(self.user_id):
                return

            # 初始化实例
            blacklist_handler = BlackListHandle(self.websocket, self.msg)

            # 解析消息
            if self.raw_message.startswith(BLACKLIST_ADD_COMMAND):
                await blacklist_handler.add_blacklist()
            elif self.raw_message.startswith(BLACKLIST_REMOVE_COMMAND):
                await blacklist_handler.remove_blacklist()
            elif self.raw_message.startswith(BLACKLIST_LIST_COMMAND):
                await blacklist_handler.list_blacklist()
            elif self.raw_message.startswith(BLACKLIST_CLEAR_COMMAND):
                await blacklist_handler.clear_blacklist()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

    async def check_blacklisted_user(self):
        """
        检查用户是否在黑名单中（包括全局黑名单），如果在则撤回消息、发出警告并踢出群聊
        :return: 如果是黑名单用户则返回True，否则返回False
        """
        try:
            with BlackListDataManager() as data_manager:
                if data_manager.is_user_blacklisted(self.group_id, self.user_id):
                    # 如果用户在黑名单中，先撤回消息
                    await delete_msg(self.websocket, self.message_id)

                    # 判断是全局黑名单还是群黑名单
                    is_global = data_manager.is_in_global_blacklist(self.user_id)
                    blacklist_type = "全局黑名单" if is_global else "群黑名单"

                    # 发送警告消息
                    warning_msg = generate_text_message(
                        f"检测到{blacklist_type}用户 {self.user_id} 在群内发言，将自动撤回消息并将其踢出"
                    )
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [warning_msg],
                        note="del_msg=30",
                    )

                    # 踢出用户并拉黑，拒绝后续加群请求
                    await set_group_kick(
                        self.websocket, self.group_id, self.user_id, True
                    )
                    logger.info(
                        f"[{MODULE_NAME}]已踢出{blacklist_type}用户 {self.user_id} 并拒绝后续加群请求"
                    )
                    return True
            return False
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]检查黑名单用户失败: {e}")
            return False

from .. import (
    MODULE_NAME,
    GROUP_BAN_COMMAND,
    GROUP_UNBAN_COMMAND,
    GROUP_KICK_COMMAND,
    GROUP_ALL_BAN_COMMAND,
    GROUP_ALL_UNBAN_COMMAND,
    GROUP_RECALL_COMMAND,
    SWITCH_NAME,
    GROUP_BAN_ME_COMMAND,
    GROUP_BAN_RANK_COMMAND,
    SCAN_INACTIVE_USER_COMMAND,
    GROUP_TOGGLE_AUTO_APPROVE_COMMAND,
)
from logger import logger
from core.menu_manager import MENU_COMMAND
from core.switchs import is_group_switch_on, handle_module_group_switch
from api.message import send_group_msg
from utils.generate import generate_text_message, generate_reply_message
from datetime import datetime
from utils.auth import is_group_admin, is_system_admin
from .GroupManagerHandle import GroupManagerHandle
from core.menu_manager import MenuManager
import re


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

            # 初始化群组管理器
            group_manager_handle = GroupManagerHandle(self.websocket, self.msg)

            # 处理管理员特殊关键字操作
            if is_group_admin(self.role):
                await group_manager_handle.handle_admin_keyword_actions()

            # 处理禁言排行榜命令 - 所有用户都可使用
            if self.raw_message.startswith(GROUP_BAN_RANK_COMMAND):
                await group_manager_handle.handle_mute_rank()
                return

            # 处理群消息
            if self.raw_message.startswith(GROUP_BAN_ME_COMMAND):
                await group_manager_handle.handle_ban_me()
            else:
                # 如果不是群管理或系统管理，则不处理其他命令
                if not is_group_admin(self.role) and not is_system_admin(self.user_id):
                    return

                if self.raw_message.startswith(GROUP_ALL_BAN_COMMAND):
                    await group_manager_handle.handle_all_mute()
                elif self.raw_message.startswith(GROUP_ALL_UNBAN_COMMAND):
                    await group_manager_handle.handle_all_unmute()
                elif self.raw_message.startswith(GROUP_BAN_COMMAND):
                    await group_manager_handle.handle_mute()
                elif self.raw_message.startswith(GROUP_UNBAN_COMMAND):
                    await group_manager_handle.handle_unmute()
                elif self.raw_message.startswith(GROUP_KICK_COMMAND):
                    await group_manager_handle.handle_kick()
                elif GROUP_RECALL_COMMAND in self.raw_message:
                    await group_manager_handle.handle_recall()
                elif re.match(r"^撤回\s+\d+", self.raw_message):
                    await group_manager_handle.handle_recall_by_count()
                elif self.raw_message.startswith(SCAN_INACTIVE_USER_COMMAND):
                    await group_manager_handle.handle_scan_inactive_user()
                elif self.raw_message.startswith(GROUP_TOGGLE_AUTO_APPROVE_COMMAND):
                    await group_manager_handle.handle_toggle_auto_approve()

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

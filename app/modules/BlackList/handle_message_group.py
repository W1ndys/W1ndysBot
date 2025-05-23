from . import (
    MODULE_NAME,
    BLACKLIST_ADD_COMMAND,
    BLACKLIST_REMOVE_COMMAND,
    BLACKLIST_LIST_COMMAND,
    BLACKLIST_CLEAR_COMMAND,
)
import logger
from core.auth import is_system_owner, is_group_admin
from core.switchs import is_group_switch_on, toggle_group_switch
from api.message import send_group_msg, delete_msg
from api.generate import generate_reply_message, generate_text_message
from api.group import set_group_kick
from datetime import datetime
from .handle_blacklist import BlackListHandle
from .data_manager import BlackListDataManager


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
        self.data_manager = BlackListDataManager()

    async def handle_module_switch(self):
        """
        处理模块开关命令
        """
        try:
            switch_status = toggle_group_switch(self.group_id, MODULE_NAME)
            switch_status = "开启" if switch_status else "关闭"
            reply_message = generate_reply_message(self.message_id)
            text_message = generate_text_message(
                f"[{MODULE_NAME}]群聊开关已切换为【{switch_status}】"
            )
            await send_group_msg(
                self.websocket,
                self.group_id,
                [reply_message, text_message],
                note="del_msg_10",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理模块开关命令失败: {e}")

    async def handle(self):
        """
        处理群消息
        """
        try:
            if self.raw_message.lower() == MODULE_NAME.lower():
                await self.handle_module_switch()
                return

            # 如果没开启群聊开关，则不处理
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

            # 首先检查发言用户是否在黑名单中，如果在则进行处理
            if await self.check_blacklisted_user():
                return

            # 鉴权，只有管理员才能使用
            if not is_group_admin(self.role) and not is_system_owner(self.user_id):
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
        检查用户是否在黑名单中，如果在则撤回消息、发出警告并踢出群聊
        :return: 如果是黑名单用户则返回True，否则返回False
        """
        try:
            if self.data_manager.is_in_blacklist(self.group_id, self.user_id):
                # 如果用户在黑名单中，先撤回消息
                await delete_msg(self.websocket, self.message_id)

                # 发送警告消息
                warning_msg = generate_text_message(
                    f"检测到黑名单用户 {self.user_id} 在群内发言，将自动撤回消息并将其踢出"
                )
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [warning_msg],
                    note="del_msg_30",
                )

                # 踢出用户并拉黑，拒绝后续加群请求
                await set_group_kick(self.websocket, self.group_id, self.user_id, True)
                logger.info(
                    f"[{MODULE_NAME}]已踢出黑名单用户 {self.user_id} 并拒绝后续加群请求"
                )
                return True
            return False
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]检查黑名单用户失败: {e}")
            return False

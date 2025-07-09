from .. import MODULE_NAME, SWITCH_NAME, TEST_COMMAND
from core.menu_manager import MENU_COMMAND
import logger
from core.switchs import is_group_switch_on, handle_module_group_switch
from api.message import send_group_msg, send_forward_msg
from utils.generate import (
    generate_reply_message,
    generate_text_message,
    generate_node_message,
)
from datetime import datetime
from utils.auth import is_system_admin
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
                if not is_system_admin(self.user_id):
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

            # 测试消息
            if self.raw_message.lower() in [TEST_COMMAND.lower()]:
                reply_message = generate_reply_message(self.message_id)
                text_message = generate_text_message(f"[{MODULE_NAME}]测试成功")
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [reply_message, text_message],
                    note="del_msg=10",
                )

                await send_forward_msg(
                    self.websocket,
                    group_id=self.group_id,
                    message=[
                        generate_node_message(
                            user_id=f"{self.user_id}",
                            nickname=f"{self.nickname}",
                            content=[generate_text_message("这是一条echo的测试消息")],
                        )
                    ],
                    news="这是一条echo消息",
                    prompt="这是一条echo消息",
                    summary="这是一条echo消息",
                    source="这是一条echo消息",
                    note="del_msg=120",
                )
                return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

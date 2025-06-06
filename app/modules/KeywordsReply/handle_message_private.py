from . import MODULE_NAME, SWITCH_NAME
import logger
from core.switchs import is_private_switch_on, handle_module_private_switch
from datetime import datetime
from .data_manager import DataManager
from core.auth import is_system_owner


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
                if not is_system_owner(self.user_id):
                    return
                await handle_module_private_switch(
                    MODULE_NAME,
                    self.websocket,
                    self.user_id,
                    self.message_id,
                )
                return

            # 如果没开启私聊开关，则不处理
            if not is_private_switch_on(MODULE_NAME):
                return

            # 示例：使用DataManager进行数据库操作
            with DataManager(self.user_id) as dm:
                # 这里可以进行数据库操作，如：dm.cursor.execute(...)
                pass

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理私聊消息失败: {e}")

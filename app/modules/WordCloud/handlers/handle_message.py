from .. import MODULE_NAME
from .handle_message_group import GroupMessageHandler
from .handle_message_private import PrivateMessageHandler


class MessageHandler:
    """消息处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.message_type = msg.get("message_type", "")

    async def handle(self):
        if self.message_type == "group":
            group_handler = GroupMessageHandler(self.websocket, self.msg)
            await group_handler.handle()
        elif self.message_type == "private":
            private_handler = PrivateMessageHandler(self.websocket, self.msg)
            await private_handler.handle()

from . import MODULE_NAME
from .handle_forward_message import ForwardMessageHandler
from .handle_group_msg_history import GetGroupMsgHistoryHandler
import logger


class ResponseHandler:
    """响应处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.echo = msg.get("echo", "")

    async def handle(self):
        try:
            # 检查是否是该模块请求解析的转发消息
            if self.echo.startswith("get_forward_msg-") and MODULE_NAME in self.echo:
                logger.info(f"[{MODULE_NAME}]收到转发消息解析请求")
                # 实例化ForwardMessageHandler
                forward_message_handler = ForwardMessageHandler(
                    self.websocket, self.msg
                )
                # 处理转发消息
                await forward_message_handler.handle_forward_message()
            elif (
                self.echo.startswith("get_group_msg_history-")
                and MODULE_NAME in self.echo
            ):
                logger.info(f"[{MODULE_NAME}]收到获取群历史消息请求")
                # 实例化GetGroupMsgHistoryHandler
                get_group_msg_history_handler = GetGroupMsgHistoryHandler(
                    self.websocket, self.msg
                )
                # 处理获取群历史消息
                await get_group_msg_history_handler.handle_get_group_msg_history()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理响应失败: {e}")

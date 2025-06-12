from . import MODULE_NAME
from .handle_forward_message import ForwardMessageHandler
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
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理响应失败: {e}")

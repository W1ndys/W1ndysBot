from . import MODULE_NAME
import logger


class ResponseHandler:
    """响应处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.echo = msg.get("echo", {})

    async def handle(self):
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理响应失败: {e}")

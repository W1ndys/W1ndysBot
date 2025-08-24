from .. import MODULE_NAME
import logger
from api.group import set_group_todo
import re


class ResponseHandler:
    """响应处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.echo = msg.get("echo", {})

    async def handle(self):
        try:
            # 检测echo里是否包含“设为代办”
            if self.echo.startswith("send_group_msg") and "设为代办" in self.echo:
                # 在数据体提取消息id，调用设置代办接口
                message_id = self.data.get("message_id")
                # 在echo正则提取群号
                group_id = re.search(r"group_id=(\d+)", self.echo)
                if message_id and group_id:
                    await set_group_todo(self.websocket, group_id.group(1), message_id)
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理响应失败: {e}")

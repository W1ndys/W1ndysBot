from . import MODULE_NAME, NOTE_CONDITION
import logger
from .data_manager import DataManager
import re


class ResponseHandler:
    """响应处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.echo = msg.get("echo", "")

    async def handle(self):
        try:
            with DataManager() as dm:
                if NOTE_CONDITION in self.echo:
                    # 存储message_id
                    # 获取group_id和user_id
                    # echo=f"send_group_msg-{NOTE_CONDITION}-group_id={self.group_id}-user_id={self.user_id}",
                    group_id_match = re.search(r"group_id=(\d+)", self.echo)
                    user_id_match = re.search(r"user_id=(\d+)", self.echo)
                    if group_id_match:
                        group_id = group_id_match.group(1)
                    else:
                        group_id = ""
                    if user_id_match:
                        user_id = user_id_match.group(1)
                    else:
                        user_id = ""
                    dm.add_message_id(group_id, user_id, self.data.get("message_id"))
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理响应失败: {e}")

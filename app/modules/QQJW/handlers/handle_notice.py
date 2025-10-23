from .. import MODULE_NAME
from logger import logger
from datetime import datetime
from .handle_notice_group import GroupNoticeHandler


class NoticeHandler:
    """
    通知处理器
    websocket: 连接对象
    msg: 通知消息
    相关文档: https://napneko.github.io/develop/event#notice-%E4%BA%8B%E4%BB%B6
    """

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.notice_type = msg.get("notice_type", "")
        self.sub_type = msg.get("sub_type", "")
        self.user_id = str(msg.get("user_id", ""))
        self.group_id = str(msg.get("group_id", ""))
        self.operator_id = str(msg.get("operator_id", ""))

    async def handle(self):
        """
        处理通知
        """
        try:
            # 只处理群组相关通知
            if self.notice_type.startswith("group_"):
                group_handler = GroupNoticeHandler(self.websocket, self.msg)
                await group_handler.handle_group_notice()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理通知失败: {e}")

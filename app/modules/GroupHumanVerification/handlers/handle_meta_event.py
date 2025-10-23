from .. import MODULE_NAME
from logger import logger
from datetime import datetime
from .handle_GroupHumanVerification import GroupHumanVerificationHandler


class MetaEventHandler:
    """
    元事件处理器/定时任务处理器
    元事件可利用心跳来实现定时任务
    """

    _last_scan_hour = None  # 类变量，所有实例共享

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.post_type = msg.get("post_type", "")
        self.meta_event_type = msg.get("meta_event_type", "")

    async def handle(self):
        try:
            # 必要时可以这里可以引入群聊开关和私聊开关检测

            if self.post_type == "meta_event":
                if self.meta_event_type == "lifecycle":
                    await self.handle_lifecycle()
                elif self.meta_event_type == "heartbeat":
                    await self.handle_heartbeat()
                else:
                    logger.error(
                        f"[{MODULE_NAME}]收到未知元事件类型: {self.meta_event_type}"
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理元事件失败: {e}")

    async def handle_lifecycle(self):
        """
        处理生命周期
        """
        try:
            if self.meta_event_type == "connect":
                pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理生命周期失败: {e}")

    async def handle_heartbeat(self):
        """
        处理心跳 - 仅在白天（如8:00-22:00）每小时整点提醒未验证用户，夜间不提醒
        """
        try:
            # 获取当前时间
            now = datetime.now()
            hour = now.hour
            minute = now.minute
            # 仅在白天8:00-22:00之间的整点进行提醒
            if 8 <= hour < 22 and minute == 0:
                # 调用基于时间间隔的扫描
                handler = GroupHumanVerificationHandler(self.websocket, self.msg)
                await handler.handle_scan_verification_by_time()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理心跳失败: {e}")

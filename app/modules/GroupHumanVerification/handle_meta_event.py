from . import MODULE_NAME
import logger
from datetime import datetime
from .handle_GroupHumanVerification import GroupHumanVerificationHandler


class MetaEventHandler:
    """
    元事件处理器/定时任务处理器
    元事件可利用心跳来实现定时任务
    """

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
        处理心跳
        """
        try:
            # 获取当前小时和分钟
            now = datetime.now()
            hour = now.hour
            minute = now.minute
            # 设定的扫描小时
            scan_hours = [0, 8, 12, 16, 20]
            # 只在整点的前2分钟内触发，且只触发一次（通过类变量记录上次触发小时）
            if not hasattr(self, "_last_scan_hour"):
                self._last_scan_hour = None
            if hour in scan_hours and minute < 2 and self._last_scan_hour != hour:
                self._last_scan_hour = hour
                # 调用自动扫描
                handler = GroupHumanVerificationHandler(self.websocket, self.msg)
                await handler.handle_scan_verification()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理心跳失败: {e}")

import asyncio
from . import MODULE_NAME
from logger import logger
from datetime import datetime
from .handle_GroupRandomMsg import send_group_random_msg
from core.switchs import get_all_enabled_groups


class MetaEventHandler:
    """
    元事件处理器/定时任务处理器
    元事件可利用心跳来实现定时任务
    """

    # 类变量：记录最近一次执行时间
    last_execution_time = None

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
            current_time = datetime.now()

            # 检查是否需要执行（每分钟执行一次）
            if (
                MetaEventHandler.last_execution_time is None
                or (current_time - MetaEventHandler.last_execution_time).total_seconds()
                >= 60
            ):

                logger.info(f"[{MODULE_NAME}]开始执行群随机消息发送任务")
                MetaEventHandler.last_execution_time = current_time

                for group_id in get_all_enabled_groups(MODULE_NAME):
                    await send_group_random_msg(self.websocket, group_id)
                    await asyncio.sleep(1)

                logger.info(f"[{MODULE_NAME}]群随机消息发送任务执行完成")

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理心跳失败: {e}")

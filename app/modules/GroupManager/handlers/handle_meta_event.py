from .. import MODULE_NAME
import logger
from datetime import datetime
from api.group import set_group_whole_ban
from .data_manager import DataManager
from api.message import send_group_msg
from utils.generate import generate_text_message


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
        处理心跳，检测宵禁时间并自动执行全员禁言操作
        """
        try:
            # 不发送宵禁通知的群号列表
            no_notification_groups = [
                "531850420",
                "1058578539",
                "273882385",
                "491480719",
                "497554955",
                "695107331",
                "788612679",
                "916115517",
            ]

            # 获取当前时间（使用HH:MM格式确保与数据库中存储的时间格式一致）
            current_time = datetime.now()
            current_time_str = current_time.strftime("%H:%M")  # 强制使用两位数小时格式
            current_datetime_str = current_time.strftime("%Y-%m-%d %H:%M")

            # 获取所有已启用宵禁的群
            with DataManager() as dm:
                enabled_groups = dm.get_all_enabled_curfew_groups()

                for group_id, start_time, end_time in enabled_groups:
                    action = dm.should_trigger_curfew_action(group_id, current_time_str)

                    if action in ["start", "end"]:
                        # 检查是否已经在当前分钟执行过该操作
                        last_trigger = dm.get_last_curfew_trigger_time(group_id)

                        # 如果上次触发时间与当前时间相同（同一分钟），则跳过
                        if last_trigger == current_datetime_str:
                            continue

                        # 更新触发时间记录
                        dm.update_curfew_trigger_time(group_id, current_datetime_str)

                        if action == "start":
                            # 宵禁开始
                            logger.info(
                                f"[{MODULE_NAME}]群 {group_id} 宵禁开始({start_time})，执行全员禁言"
                            )
                            await set_group_whole_ban(self.websocket, group_id, True)

                        elif action == "end":
                            # 宵禁结束
                            logger.info(
                                f"[{MODULE_NAME}]群 {group_id} 宵禁结束({end_time})，解除全员禁言"
                            )
                            await set_group_whole_ban(self.websocket, group_id, False)

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理心跳宵禁检测失败: {e}")

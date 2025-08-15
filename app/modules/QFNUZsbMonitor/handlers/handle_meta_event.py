from .. import MODULE_NAME, DATA_DIR
import logger
from datetime import datetime
import json
import os
from ..core.get_lqcx_param import GetLqcx
from core.switchs import get_all_enabled_groups
from api.message import send_group_msg


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

    def _read_status(self, status_file: str) -> dict:
        """读取状态文件"""
        if os.path.exists(status_file):
            try:
                with open(status_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content:
                        return json.loads(content)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning(
                    f"[{MODULE_NAME}] 状态文件为空或格式错误，将重新初始化。"
                )
        return {}

    def _update_status_file(self, status_file: str, new_status: dict):
        """用新状态覆盖旧状态文件"""
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(new_status, f, ensure_ascii=False, indent=4)

    def _compare_statuses(self, old_status: dict, new_status: dict) -> list[str]:
        """比较新旧状态并返回变化列表"""
        old_provinces = old_status.get("provinces", {})
        new_provinces = new_status.get("provinces", {})
        change_messages = []

        for province, categories in new_provinces.items():
            for category, details in categories.items():
                new_status_text = details.get("status_text")
                old_details = old_provinces.get(province, {}).get(category, {})
                old_status_text = old_details.get("status_text")

                if new_status_text is not None and new_status_text != old_status_text:
                    change_info = f"{province}，{category}，有新状态：{new_status_text}"
                    logger.info(f"[{MODULE_NAME}] 检测到变化: {change_info}")
                    change_messages.append(change_info)
        return change_messages

    async def _notify_groups(
        self, change_messages: list[str], enabled_groups: list[str]
    ):
        """向启用的群组发送通知"""
        if not change_messages:
            logger.info(f"[{MODULE_NAME}] 招生状态无变化。")
            return

        logger.info(
            f"[{MODULE_NAME}] 共检测到 {len(change_messages)} 条招生状态变化，准备推送。"
        )

        message_to_send = "曲阜师范大学招生状态有新变化！\n" + "\n".join(
            change_messages
        )
        for group_id in enabled_groups:
            await send_group_msg(
                self.websocket,
                group_id,
                message_to_send,
            )
            logger.info(f"[{MODULE_NAME}] 推送消息到群聊: {group_id}")

    async def handle_heartbeat(self):
        """
        处理心跳
        """
        try:
            # 新增：仅在7月到9月之间进行检测
            from datetime import datetime

            now = datetime.now()
            if now.month < 7 or now.month > 9:
                logger.debug(f"[{MODULE_NAME}] 当前不在7月至9月，跳过招生状态检测。")
                return

            enabled_groups = get_all_enabled_groups(MODULE_NAME)
            if not enabled_groups:
                logger.debug(f"[{MODULE_NAME}] 没有启用的群聊，跳过招生状态检测。")
                return

            status_file = os.path.join(DATA_DIR, "status.json")

            client = GetLqcx()
            new_status = client.get_formatted_zsstate()

            if not new_status or not new_status.get("provinces"):
                logger.warning(f"[{MODULE_NAME}] 获取到的招生状态为空或格式不正确")
                return

            old_status = self._read_status(status_file)

            if not old_status:
                logger.info(f"[{MODULE_NAME}] 本地状态文件不存在或为空，正在初始化...")
                self._update_status_file(status_file, new_status)
                logger.info(f"[{MODULE_NAME}] 初始化状态完成。")
                return

            change_messages = self._compare_statuses(old_status, new_status)

            await self._notify_groups(change_messages, enabled_groups)

            self._update_status_file(status_file, new_status)

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理心跳失败: {e}")

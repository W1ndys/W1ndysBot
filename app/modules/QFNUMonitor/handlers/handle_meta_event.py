"""
QFNUMonitor 元事件处理器
实现心跳定时检查公告功能
"""

from .. import MODULE_NAME
from logger import logger
from datetime import datetime
from ..core.QFNUClient import QFNUClient
from ..core.SiliconFlowAPI import SiliconFlowAPI
from .data_manager import DataManager
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
        处理心跳 - 定时检查公告
        """
        try:
            # 获取所有启用的群聊
            enabled_groups = get_all_enabled_groups(MODULE_NAME)
            if not enabled_groups:
                logger.debug(f"[{MODULE_NAME}] 没有启用的群聊，跳过公告检测")
                return

            logger.debug(
                f"[{MODULE_NAME}] 开始检测公告，启用群聊数: {len(enabled_groups)}"
            )

            async with QFNUClient() as client:
                # 获取公告列表
                announcements = await client.get_announcements(max_count=10)

                if not announcements:
                    logger.warning(f"[{MODULE_NAME}] 未获取到任何公告")
                    return

                # 检测新公告
                data_manager = DataManager()
                new_announcements = []

                for ann in announcements:
                    if not data_manager.is_notified(ann.id):
                        new_announcements.append(ann)

                if not new_announcements:
                    logger.debug(f"[{MODULE_NAME}] 没有新公告")
                    data_manager.close()
                    return

                logger.info(
                    f"[{MODULE_NAME}] 检测到 {len(new_announcements)} 条新公告，准备推送"
                )

                # 初始化摘要生成器
                summary_api = SiliconFlowAPI()

                # 处理每条新公告
                for ann in new_announcements:
                    # 尝试生成摘要
                    summary = ""
                    if summary_api.is_available():
                        # 获取公告详情内容
                        content = await client.get_announcement_content(ann.url)
                        if content:
                            summary = await summary_api.generate_summary(content)

                    # 构建推送消息
                    message = self._build_notification_message(ann, summary)

                    # 推送到所有启用的群聊
                    for group_id in enabled_groups:
                        try:
                            await send_group_msg(self.websocket, group_id, message)
                            logger.info(
                                f"[{MODULE_NAME}] 推送公告到群 {group_id}: {ann.title}"
                            )
                        except Exception as e:
                            logger.error(
                                f"[{MODULE_NAME}] 推送公告到群 {group_id} 失败: {e}"
                            )

                    # 记录已通知
                    data_manager.add_notified(
                        ann.id, ann.title, ann.url, ann.date, summary or ann.summary
                    )

                data_manager.close()

        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 处理心跳失败: {e}")

    def _build_notification_message(self, ann, summary: str = "") -> str:
        """
        构建公告通知消息

        Args:
            ann: 公告对象
            summary: AI 生成的摘要

        Returns:
            格式化的通知消息
        """
        lines = [
            "📢 曲阜师范大学教务处新公告",
            "",
            f"📌 {ann.title}",
            f"📅 发布日期: {ann.date}",
        ]

        # 添加摘要
        if summary:
            lines.extend(["", "📝 智能摘要:", summary])
        elif ann.summary:
            # 截取原始摘要
            original_summary = ann.summary
            if len(original_summary) > 150:
                original_summary = original_summary[:150] + "..."
            lines.extend(["", "📝 摘要:", original_summary])

        lines.extend(["", f"🔗 详情链接: {ann.url}"])

        return "\n".join(lines)

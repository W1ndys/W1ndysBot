from .. import MODULE_NAME
import logger
from datetime import datetime
from core.switchs import is_private_switch_on


class FriendNoticeHandler:
    """
    好友通知处理器
    """

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.notice_type = msg.get("notice_type")
        self.sub_type = msg.get("sub_type")
        self.user_id = str(msg.get("user_id"))

    async def handle_friend_notice(self):
        """
        处理好友通知
        """
        try:
            # 如果没开启私聊开关，则不处理
            if not is_private_switch_on(MODULE_NAME):
                return

            if self.notice_type == "friend_add":
                await self.handle_friend_add()
            elif self.notice_type == "friend_recall":
                await self.handle_friend_recall()
            elif self.notice_type == "offline_file":
                await self.handle_offline_file()
            elif self.notice_type == "client_status":
                await self.handle_client_status()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理好友通知失败: {e}")

    # 好友相关通知处理
    async def handle_friend_add(self):
        """
        处理好友添加通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理好友添加通知失败: {e}")

    async def handle_friend_recall(self):
        """
        处理好友撤回通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理好友撤回通知失败: {e}")

    async def handle_offline_file(self):
        """
        处理接收到离线文件通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理接收到离线文件通知失败: {e}")

    async def handle_client_status(self):
        """
        处理其他客户端在线状态变更通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理其他客户端在线状态变更通知失败: {e}")

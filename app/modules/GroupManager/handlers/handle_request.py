from .. import MODULE_NAME
import logger
from datetime import datetime
from .data_manager import DataManager
from api.group import set_group_add_request


class RequestHandler:
    """请求处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.request_type = msg.get("request_type", "")
        self.user_id = self.msg.get("user_id", "")
        self.comment = self.msg.get("comment", "")
        self.flag = self.msg.get("flag", "")
        self.group_id = self.msg.get("group_id", "")

    async def handle_friend(self):
        """
        处理好友请求
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理好友请求失败: {e}")

    async def handle_group(self):
        """
        处理群请求
        """
        try:
            self.sub_type = self.msg.get("sub_type", "")
            if self.sub_type == "invite":
                await self.handle_group_invite()
            elif self.sub_type == "add":
                await self.handle_group_add()
            else:
                logger.error(f"[{MODULE_NAME}]收到未知群请求类型: {self.sub_type}")
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群请求失败: {e}")

    async def handle_group_invite(self):
        """
        处理邀请登录号入群请求
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理邀请登录号入群请求失败: {e}")

    async def handle_group_add(self):
        """
        处理加群请求
        """
        try:
            # 检查是否开启自动同意入群
            with DataManager() as dm:
                is_auto_approve_enabled = dm.get_auto_approve_status(self.group_id)

                if is_auto_approve_enabled:
                    # 自动同意入群请求
                    await set_group_add_request(self.websocket, self.flag, True)
                    logger.info(
                        f"[{MODULE_NAME}]自动同意用户 {self.user_id} 加入群 {self.group_id}"
                    )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理加群请求失败: {e}")

    async def handle(self):
        try:

            if self.request_type == "friend":
                # 必要时可以这里可以引入好友请求开关检测
                await self.handle_friend()
            elif self.request_type == "group":
                # 必要时可以这里可以引入群聊请求开关检测
                await self.handle_group()
            else:
                logger.error(f"[{MODULE_NAME}]收到未知请求类型: {self.request_type}")
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理请求失败: {e}")

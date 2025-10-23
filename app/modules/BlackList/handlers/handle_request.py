from .. import MODULE_NAME
from logger import logger
from datetime import datetime
from core.switchs import is_group_switch_on
from .data_manager import BlackListDataManager
from api.user import set_group_add_request


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
            # 如果没开启群聊开关，则不处理
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

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
            with BlackListDataManager() as data_manager:
                if data_manager.is_user_blacklisted(self.group_id, self.user_id):
                    # 判断是全局黑名单还是群黑名单
                    is_global = data_manager.is_in_global_blacklist(self.user_id)
                    blacklist_type = "全局黑名单" if is_global else "群黑名单"
                    reason = f"您在{blacklist_type}中，无法加入群聊"

                    await set_group_add_request(
                        self.websocket, self.flag, False, reason
                    )
                    logger.info(
                        f"[{MODULE_NAME}]拒绝{blacklist_type}用户 {self.user_id} 加入群 {self.group_id}"
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

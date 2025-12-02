from .. import MODULE_NAME
from logger import logger
from datetime import datetime
from .handle_notice_friend import FriendNoticeHandler
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
            if self.notice_type.startswith("friend_"):
                friend_handler = FriendNoticeHandler(self.websocket, self.msg)
                await friend_handler.handle_friend_notice()
            elif self.notice_type.startswith("group_"):
                group_handler = GroupNoticeHandler(self.websocket, self.msg)
                await group_handler.handle_group_notice()
            elif self.notice_type == "notify":
                await self.handle_notify_notice()
            elif self.notice_type == "essence":
                await self.handle_essence_notice()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理通知失败: {e}")

    async def handle_notify_notice(self):
        """
        处理通知事件
        """
        try:
            if self.sub_type == "poke":
                await self.handle_notify_poke()
            elif self.sub_type == "input_status":
                await self.handle_notify_input_status()
            elif self.sub_type == "title":
                await self.handle_notify_title()
            elif self.sub_type == "profile_like":
                await self.handle_notify_profile_like()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理通知事件失败: {e}")

    async def handle_essence_notice(self):
        """
        处理精华消息通知
        """
        try:
            if self.sub_type == "add":
                await self.handle_essence_add()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理精华消息通知失败: {e}")

    # 通知事件处理
    async def handle_notify_poke(self):
        """
        处理戳一戳通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理戳一戳通知失败: {e}")

    async def handle_notify_input_status(self):
        """
        处理输入状态更新通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理输入状态更新通知失败: {e}")

    async def handle_notify_title(self):
        """
        处理群成员头衔变更通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群成员头衔变更通知失败: {e}")

    async def handle_notify_profile_like(self):
        """
        处理点赞通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理点赞通知失败: {e}")

    # 精华消息处理
    async def handle_essence_add(self):
        """
        处理群聊设精 - 增加通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊设精 - 增加通知失败: {e}")

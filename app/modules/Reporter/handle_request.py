from . import MODULE_NAME
import logger
from utils.generate import generate_text_message
from api.message import send_private_msg
from config import OWNER_ID
from datetime import datetime


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

    async def handle_friend(self):
        """
        处理好友请求
        """
        try:
            text_message = generate_text_message(
                f"收到好友请求\n"
                f"user_id={self.user_id}\n"
                f"request_type={self.request_type}\n"
                f"comment={self.comment}\n"
                f"flag={self.flag}\n"
                f"time={self.time}\n"
                f"可以通过引用本消息【同意/拒绝】来处理请求\n"
            )
            await send_private_msg(self.websocket, OWNER_ID, [text_message])
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
            text_message = generate_text_message(
                f"收到邀请登录号入群请求\n"
                f"user_id={self.user_id}\n"
                f"request_type={self.request_type}\n"
                f"comment={self.comment}\n"
                f"flag={self.flag}\n"
                f"可以通过引用本消息【同意/拒绝】来处理请求\n"
            )
            await send_private_msg(self.websocket, OWNER_ID, [text_message])
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理邀请登录号入群请求失败: {e}")

    async def handle_group_add(self):
        """
        处理加群请求
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理加群请求失败: {e}")

    async def handle(self):
        if self.request_type == "friend":
            await self.handle_friend()
        elif self.request_type == "group":
            await self.handle_group()
        else:
            logger.error(f"[{MODULE_NAME}]收到未知请求类型: {self.request_type}")

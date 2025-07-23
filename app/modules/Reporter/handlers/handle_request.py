import os
import json
import asyncio
import random
from .. import MODULE_NAME, DATA_DIR
import logger
from utils.generate import generate_text_message
from api.message import send_private_msg
from config import OWNER_ID
from datetime import datetime
from api.user import set_friend_add_request


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

    def is_auto_agree_friend_verify(self):
        """
        判断是否开启自动同意好友验证
        """
        SWITCH_FILE = os.path.join(DATA_DIR, "auto_agree_friend_verify.json")
        if not os.path.exists(SWITCH_FILE):
            with open(SWITCH_FILE, "w") as f:
                json.dump({}, f)
        with open(SWITCH_FILE, "r") as f:
            switch = json.load(f)
        return switch.get(MODULE_NAME, False)

    async def handle_friend(self):
        """
        处理好友请求
        """
        try:
            # 如果开启自动同意好友验证，则自动同意
            if self.is_auto_agree_friend_verify():
                # 随机延迟1-5秒
                await asyncio.sleep(random.randint(1, 5))
                await set_friend_add_request(
                    self.websocket,
                    self.flag,
                    True,
                )
                await send_private_msg(
                    self.websocket,
                    OWNER_ID,
                    [
                        generate_text_message(
                            f"自动同意好友请求\n"
                            f"user_id={self.user_id}\n"
                            f"request_type={self.request_type}\n"
                            f"comment={self.comment}\n"
                            f"flag={self.flag}\n"
                        ),
                    ],
                )
                return

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

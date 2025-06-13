from datetime import datetime
from . import (
    MODULE_NAME,
)
from .data_manager_words import DataManager
from .ban_words_utils import check_and_handle_ban_words
from logger import logger


class ForwardMessageHandler:
    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.messages = self.data.get("messages", [])
        self.echo = msg.get("echo", "")
        self.group_id = None  # 转发消息发送者群号
        self.user_id = None  # 转发消息发送者QQ号
        self.message_id = None  # 转发消息ID
        self.data_manager = None  # 初始化为None，解析完参数后再实例化
        self.raw_message = ""
        self.formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def handle_forward_message(self):
        """处理转发消息"""
        try:
            # 解析echo内的参数
            parts = self.echo.split("-")
            for part in parts[2:]:  # 跳过 'get_forward_msg' 和 MODULE_NAME
                if "=" in part:
                    key, value = part.split("=")
                    if key == "group_id":
                        self.group_id = value
                    elif key == "user_id":
                        self.user_id = value
                    elif key == "message_id":
                        self.message_id = value

            # 解析完参数后初始化data_manager
            if self.group_id:
                self.data_manager = DataManager(group_id=self.group_id)

            logger.info(
                f"[{MODULE_NAME}]收到转发消息解析响应: 群号: {self.group_id}, 发送者QQ号: {self.user_id}, 消息ID: {self.message_id}"
            )
            # 拼接message里的所有raw_message
            raw_message = ""
            for item in self.messages:
                raw_message += item.get("raw_message", "")
            self.raw_message = raw_message
            logger.info(f"[{MODULE_NAME}]拼接后的所有原始消息内容: {raw_message}")

            # 使用提取的通用函数检测和处理违禁词
            if self.group_id and self.user_id and self.message_id and self.data_manager:
                return await check_and_handle_ban_words(
                    self.websocket,
                    self.group_id,
                    self.user_id,
                    self.message_id,
                    self.raw_message,
                    self.formatted_time,
                )
            return False
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理转发消息失败: {e}")
            return False

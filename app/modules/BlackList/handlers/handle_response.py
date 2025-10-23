from .. import MODULE_NAME, PRIVATE_BLACKLIST_ADD_COMMAND
from .data_manager import BlackListDataManager
from api.message import send_private_msg
from config import OWNER_ID
from utils.generate import generate_text_message
from logger import logger
import re


class ResponseHandler:
    """响应处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.echo = msg.get("echo", {})

    async def handle(self):
        try:
            # 检查是否是获取消息的响应
            if self.echo.startswith("get_msg-") and MODULE_NAME in self.echo:
                await self.handle_get_msg_response()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理响应失败: {e}")

    async def handle_get_msg_response(self):
        """
        处理获取消息响应
        """
        try:
            # 正则匹配action
            pattern = r"action=(.*)"
            match = re.search(pattern, self.echo)
            if not match:
                logger.error(f"[{MODULE_NAME}]从echo中提取action失败: {self.echo}")
                return
            action = match.group(1)
            if action == PRIVATE_BLACKLIST_ADD_COMMAND:
                await self.handle_private_blacklist_add_response()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理获取消息响应失败: {e}")

    async def handle_private_blacklist_add_response(self):
        """
        处理私聊拉黑响应
        """
        try:
            raw_message = self.data.get("raw_message", "")
            # 在原始消息里提取user_id
            pattern = r"user_id=(\d+)"
            matches = re.findall(pattern, raw_message)
            if not matches:
                logger.error(
                    f"[{MODULE_NAME}]从原始消息里提取user_id失败: {raw_message}"
                )
                return False
            for user_id in matches:
                logger.info(f"[{MODULE_NAME}]提取到user_id: {user_id}")
                # 添加全局黑名单
                with BlackListDataManager() as data_manager:
                    data_manager.add_global_blacklist(user_id)
                await send_private_msg(
                    self.websocket,
                    OWNER_ID,
                    [
                        generate_text_message(
                            f"[{MODULE_NAME}]已将用户{', '.join(matches)}拉入全局黑名单"
                        )
                    ],
                )
            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理私聊拉黑响应失败: {e}")

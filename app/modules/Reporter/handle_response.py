from . import MODULE_NAME
import logger
import re
from api.user import set_friend_add_request, set_group_add_request
from api.message import send_private_msg
from utils.generate import generate_text_message


class ResponseHandler:
    """响应处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.echo = msg.get("echo", {})

    async def handle(self):
        try:
            # 处理获取消息详情的响应
            if isinstance(self.echo, str) and self.echo.startswith(
                f"{MODULE_NAME}-request_handler"
            ):
                await self._handle_request_response()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理响应失败: {e}")

    async def _handle_request_response(self):
        """处理请求响应"""
        try:
            # 解析echo字段: MODULE_NAME-request_handler-action-user_id=xxx
            echo_pattern = rf"{MODULE_NAME}-request_handler-(同意|拒绝)-user_id=(\d+)"
            match = re.match(echo_pattern, self.echo)

            if not match:
                logger.error(f"[{MODULE_NAME}]无法解析echo字段: {self.echo}")
                return

            action = match.group(1)
            user_id = match.group(2)

            # 获取原始消息内容
            message_data = self.data
            raw_message = message_data.get("raw_message", "")

            logger.info(f"[{MODULE_NAME}]获取到原始消息: {raw_message}")

            # 从原始消息中提取flag
            flag = None
            request_type = None

            # 正则提取请求类型和flag
            request_type_pattern = r"request_type=(friend|group)"
            flag_pattern = r"flag=(\d+)"
            request_type_match = re.search(request_type_pattern, raw_message)
            flag_match = re.search(flag_pattern, raw_message)
            if request_type_match:
                request_type = request_type_match.group(1)
            if flag_match:
                flag = flag_match.group(1)

            logger.info(f"[{MODULE_NAME}]提取到flag: {flag}, 请求类型: {request_type}")

            # 执行相应操作
            approve = action == "同意"

            if request_type == "friend":
                await set_friend_add_request(self.websocket, flag, approve)
                action_text = "同意好友请求" if approve else "拒绝好友请求"
            else:  # group
                await set_group_add_request(self.websocket, flag, approve, reason="")
                action_text = (
                    "同意邀请登录号入群请求" if approve else "拒绝邀请登录号入群请求"
                )

            logger.info(f"[{MODULE_NAME}]已执行: {action_text}, flag: {flag}")

            # 发送确认消息给用户
            await send_private_msg(
                self.websocket,
                user_id,
                [generate_text_message(f"已{action_text}")],
            )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理请求响应失败: {e}")

from .. import MODULE_NAME, FORWARD_MESSAGE_TO_OWNER
from logger import logger
import re
from api.user import set_friend_add_request, set_group_add_request
from api.message import send_private_msg
from utils.generate import generate_text_message
from .data_manager import DataManager


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
            if (
                isinstance(self.echo, str)
                and self.echo.startswith("get_msg-")
                and MODULE_NAME in self.echo
            ):
                await self._handle_request_response()

            # 处理转发消息给owner的响应
            if isinstance(self.echo, str) and self.echo.startswith(
                f"send_private_msg-{MODULE_NAME}-{FORWARD_MESSAGE_TO_OWNER}"
            ):
                await self._handle_forward_message_to_owner()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理响应失败: {e}")

    async def _handle_request_response(self):
        """处理请求响应"""
        try:
            # 获取原始消息内容
            message_data = self.data
            raw_message = message_data.get("raw_message", "")

            # 正则提取信息
            request_type_pattern = r"request_type=(friend|group)"
            flag_pattern = r"flag=(\d+)"
            action_pattern = r"action=([^-\s]+)"
            operate_user_id_pattern = r"operate_user_id=(\d+)"

            # 在原始消息执行正则匹配
            request_type_match = re.search(request_type_pattern, raw_message)
            flag_match = re.search(flag_pattern, raw_message)

            # 在echo正则
            action_match = re.search(action_pattern, self.echo)
            operate_user_id_match = re.search(operate_user_id_pattern, self.echo)

            # 提取匹配结果
            if operate_user_id_match:
                operate_user_id = operate_user_id_match.group(1)
            if action_match:
                action = action_match.group(1)
            if request_type_match:
                request_type = request_type_match.group(1)
            if flag_match:
                flag = flag_match.group(1)

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

            # 发送确认消息给用户
            await send_private_msg(
                self.websocket,
                operate_user_id,
                [
                    generate_text_message(
                        f"已{action_text}请求\n"
                        f"相关参数：request_type={request_type}\n"
                        f"flag={flag}\n"
                        f"action={action}\n"
                        f"operate_user_id={operate_user_id}"
                    )
                ],
            )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理请求响应失败: {e}")

    async def _handle_forward_message_to_owner(self):
        """处理转发消息给owner的响应"""
        try:
            # 获取转发消息id
            forwarded_message_id = self.data.get("message_id", "")

            # 正则提取发送者id和原始消息id
            user_id_pattern = r"user_id=(\d+)"
            original_message_id_pattern = r"original_message_id=(\d+)"

            # 在echo字段执行正则匹配
            user_id_match = re.search(user_id_pattern, self.echo)
            original_message_id_match = re.search(
                original_message_id_pattern, self.echo
            )

            # 提取匹配结果
            user_id = user_id_match.group(1) if user_id_match else None
            original_message_id = (
                original_message_id_match.group(1)
                if original_message_id_match
                else None
            )

            # 检查必要参数
            if not (user_id and original_message_id and forwarded_message_id):
                logger.error(
                    f"[{MODULE_NAME}]参数缺失，无法更新消息映射关系。user_id: {user_id}, original_message_id: {original_message_id}, forwarded_message_id: {forwarded_message_id}"
                )
                return

            # 更新消息映射关系
            with DataManager() as data_manager:
                update_result = data_manager.update_forwarded_message_id(
                    original_message_id, forwarded_message_id
                )
                if update_result:
                    logger.info(
                        f"[{MODULE_NAME}]已成功更新消息映射关系：发送者ID={user_id}, 原始消息ID={original_message_id}, 转发消息ID={forwarded_message_id}"
                    )
                else:
                    logger.warning(
                        f"[{MODULE_NAME}]未能更新消息映射关系，可能原始消息ID不存在：{original_message_id}"
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理转发消息给owner的响应失败: {e}")

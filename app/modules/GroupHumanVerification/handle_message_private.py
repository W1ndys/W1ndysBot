from . import (
    MODULE_NAME,
    SWITCH_NAME,
    APPROVE_VERIFICATION,
    REJECT_VERIFICATION,
    SCAN_VERIFICATION,
)
import logger
from core.switchs import is_private_switch_on, toggle_private_switch
from api.message import send_private_msg
from api.generate import (
    generate_reply_message,
    generate_text_message,
)
from datetime import datetime
from config import OWNER_ID
from .GroupHumanVerification import GroupHumanVerificationHandler


class PrivateMessageHandler:
    """私聊消息处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.sub_type = msg.get("sub_type", "")  # 子类型,friend/group
        self.user_id = str(msg.get("user_id", ""))  # 发送者QQ号
        self.message_id = str(msg.get("message_id", ""))  # 消息ID
        self.message = msg.get("message", {})  # 消息段数组
        self.raw_message = msg.get("raw_message", "")  # 原始消息
        self.sender = msg.get("sender", {})  # 发送者信息
        self.nickname = self.sender.get("nickname", "")  # 昵称

    async def handle_module_switch(self):
        """
        处理模块开关命令
        """
        try:
            switch_status = toggle_private_switch(MODULE_NAME)
            switch_status = "开启" if switch_status else "关闭"
            reply_message = generate_reply_message(self.message_id)
            text_message = generate_text_message(
                f"[{MODULE_NAME}]私聊开关已切换为【{switch_status}】 🔄"
            )
            await send_private_msg(
                self.websocket,
                self.user_id,
                [reply_message, text_message],
                note="del_msg=10",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理模块开关命令失败: {e}")

    async def handle(self):
        """
        处理私聊消息
        """
        try:
            if self.raw_message.lower() == SWITCH_NAME.lower():
                await self.handle_module_switch()
                return

            # 如果没开启私聊开关，则不处理
            if not is_private_switch_on(MODULE_NAME):
                return

            # 如果不是好友类型，则不处理
            if self.sub_type != "friend":
                return

            # 如果是默认的加好友打招呼消息，则不处理
            if self.raw_message == "请求添加你为好友":
                return

            # 初始化入群验证处理器
            group_human_verification_handler = GroupHumanVerificationHandler(
                self.websocket, self.user_id, self.raw_message
            )
            # 如果是管理员，判断是否是批准信息
            if self.user_id == OWNER_ID:
                if self.raw_message.startswith(APPROVE_VERIFICATION):
                    await group_human_verification_handler.handle_approve_request()
                elif self.raw_message.startswith(REJECT_VERIFICATION):
                    await group_human_verification_handler.handle_reject_request()
                elif self.raw_message.startswith(SCAN_VERIFICATION):
                    await group_human_verification_handler.handle_scan_request()
            # 如果是普通用户，判断是否是用户发送的验证码
            else:
                await group_human_verification_handler.handle_verification_code()

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理私聊消息失败: {e}")

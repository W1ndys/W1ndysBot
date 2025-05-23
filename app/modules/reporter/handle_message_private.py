from . import MODULE_NAME
import logger
from core.auth import is_system_owner
from core.switchs import is_private_switch_on, toggle_private_switch
from config import OWNER_ID
from api.message import send_private_msg
from api.user import set_friend_add_request, set_group_add_request
from api.generate import generate_reply_message, generate_text_message
import re
from datetime import datetime


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

    async def handle(self):
        """
        处理私聊消息
        """
        try:
            if self.raw_message.lower() == MODULE_NAME.lower():
                switch_status = toggle_private_switch(MODULE_NAME)
                switch_status = "开启" if switch_status else "关闭"
                reply_message = generate_reply_message(self.message_id)
                text_message = generate_text_message(
                    f"[{MODULE_NAME}]私聊开关已切换为【{switch_status}】"
                )
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [reply_message, text_message],
                )
                return

            # 如果没开启私聊开关，则不处理
            if not is_private_switch_on(MODULE_NAME):
                return

            # 鉴权
            if is_system_owner(self.user_id):

                # 处理测试消息
                if self.raw_message.lower() in ["测试", "test"]:
                    reply_message = generate_reply_message(self.message_id)
                    text_message = generate_text_message(f"[{MODULE_NAME}]测试成功")
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [reply_message, text_message],
                        note="del_msg_3",
                    )
                    return

                # 处理好友请求
                # 格式: 同意/拒绝好友请求+请求ID
                if re.match(r"^(同意|拒绝)好友请求\s*\d+$", self.raw_message):
                    # 提取行为和请求ID
                    parts = self.raw_message.split(" ")
                    action = parts[0]
                    flag = parts[1]
                    logger.info(f"[{MODULE_NAME}]处理好友请求: {action} {flag}")
                    # 处理好友请求
                    approve = action == "同意好友请求"
                    await set_friend_add_request(self.websocket, flag, approve)
                    reply_message = generate_reply_message(self.message_id)
                    text_message = generate_text_message(f"[{MODULE_NAME}]已{action}")
                    await send_private_msg(
                        self.websocket, self.user_id, [reply_message, text_message]
                    )
                    return
                # 处理群请求
                # 格式: 同意/拒绝邀请登录号入群请求+请求ID
                if re.match(r"^(同意|拒绝)邀请登录号入群请求\s*\d+$", self.raw_message):
                    # 提取行为和请求ID
                    parts = self.raw_message.split(" ")
                    action = parts[0]
                    flag = parts[1]
                    logger.info(f"[{MODULE_NAME}]处理群请求: {action} {flag}")
                    # 处理群请求
                    approve = action == "同意群请求"
                    await set_group_add_request(
                        self.websocket, flag, approve, reason=""
                    )
                    reply_message = generate_reply_message(self.message_id)
                    text_message = generate_text_message(f"[{MODULE_NAME}]已{action}")
                    await send_private_msg(
                        self.websocket, self.user_id, [reply_message, text_message]
                    )
                    return
            # 普通消息转发给owner
            else:
                message = f"[{MODULE_NAME}]收到私聊消息\n"
                message += f"用户ID: {self.user_id}\n"
                message += f"消息内容: {self.raw_message}\n"
                message += f"发送时间: {self.formatted_time}"
                message = generate_text_message(message)
                await send_private_msg(
                    self.websocket,
                    OWNER_ID,
                    [message],
                )
                return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理私聊消息失败: {e}")

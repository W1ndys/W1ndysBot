from .. import MODULE_NAME, SWITCH_NAME
from core.menu_manager import MENU_COMMAND
import logger
from core.auth import is_system_admin
from core.switchs import is_private_switch_on, handle_module_private_switch
from config import OWNER_ID
from api.message import send_private_msg, send_private_msg_with_cq, get_msg
from api.user import set_friend_add_request, set_group_add_request
from utils.generate import generate_reply_message, generate_text_message
import re
from datetime import datetime
from core.menu_manager import MenuManager
import asyncio


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
        self.group_id = str(msg.get("group_id", ""))  # 群号

    async def handle(self):
        """
        处理私聊消息
        """
        try:
            if self.raw_message.lower() == SWITCH_NAME.lower():
                # 鉴权
                if not is_system_admin(self.user_id):
                    return
                await handle_module_private_switch(
                    MODULE_NAME,
                    self.websocket,
                    self.user_id,
                    self.message_id,
                )
                return

            # 处理菜单命令（无视开关状态）
            if self.raw_message.lower() == f"{SWITCH_NAME}{MENU_COMMAND}".lower():
                menu_text = MenuManager.get_module_commands_text(MODULE_NAME)
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(menu_text),
                    ],
                    note="del_msg=30",
                )
                return

            # 如果没开启私聊开关，则不处理
            if not is_private_switch_on(MODULE_NAME):
                return

            # 鉴权
            if is_system_admin(self.user_id):

                # 处理测试消息
                if self.raw_message.lower() in ["测试", "test"]:
                    reply_message = generate_reply_message(self.message_id)
                    text_message = generate_text_message(f"测试成功")
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        [reply_message, text_message],
                        note="del_msg=10",
                    )
                    return

                # 处理好友请求和群请求
                # 格式: [CQ:reply,id=消息ID]同意/拒绝
                if re.match(r"^\[CQ:reply,id=\d+\](同意|拒绝)$", self.raw_message):
                    # 提取回复消息ID和行为
                    match = re.match(
                        r"^\[CQ:reply,id=(\d+)\](同意|拒绝)$", self.raw_message
                    )
                    if match:
                        reply_msg_id = match.group(1)
                        action = match.group(2)

                        logger.info(
                            f"[{MODULE_NAME}]检测到请求处理: {action}, 回复消息ID: {reply_msg_id}"
                        )

                        # 发送获取消息详情的API请求
                        note = f"{MODULE_NAME}-action={action}-operate_user_id={self.user_id}"
                        await get_msg(self.websocket, reply_msg_id, note)
                        return

            # 普通消息转发给owner
            else:
                # 定义需要忽略的消息正则表达式
                ignore_patterns = [
                    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",  # UUID
                    r".*com\.tencent\.qun\.invite.*",  # 邀请加群的CQ码
                ]

                # 检查消息是否包含任何忽略模式
                if any(
                    re.search(pattern, self.raw_message) for pattern in ignore_patterns
                ):
                    return

                await send_private_msg(
                    self.websocket,
                    OWNER_ID,
                    [
                        generate_text_message(
                            f"用户ID🆔：{self.user_id}\n"
                            f"发送时间：{self.formatted_time}\n"
                            f"昵称：{self.nickname}\n"
                            f"来源群号：{self.group_id if self.group_id else '无'}\n"
                            f"消息内容见下条消息"
                        )
                    ],
                )
                await asyncio.sleep(0.4)
                await send_private_msg_with_cq(
                    self.websocket, OWNER_ID, self.raw_message
                )
                return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理私聊消息失败: {e}")

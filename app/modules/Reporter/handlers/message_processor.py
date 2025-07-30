import re
import os
import json
import asyncio
import logger
from .. import MODULE_NAME, AUTO_AGREE_FRIEND_VERIFY, DATA_DIR, FORWARD_MESSAGE_TO_OWNER
from config import OWNER_ID
from api.message import send_private_msg, send_private_msg_with_cq, get_msg
from utils.generate import generate_reply_message, generate_text_message
from .data_manager import DataManager


class MessageProcessor:
    """消息处理核心逻辑"""

    # 类变量，用于记录上次发送消息的用户
    _last_user_id = None

    def __init__(
        self,
        websocket,
        user_id,
        message_id,
        raw_message,
        message,
        formatted_time,
        nickname,
        group_id,
    ):
        self.websocket = websocket
        self.user_id = user_id
        self.message_id = message_id
        self.raw_message = raw_message
        self.message = message
        self.formatted_time = formatted_time
        self.nickname = nickname
        self.group_id = group_id

    async def handle_test_message(self):
        """处理测试消息"""
        if self.raw_message.lower() in ["测试", "test"]:
            reply_message = generate_reply_message(self.message_id)
            text_message = generate_text_message("测试成功")
            await send_private_msg(
                self.websocket,
                self.user_id,
                [reply_message, text_message],
                note="del_msg=10",
            )
            return True
        return False

    async def handle_request_approval(self):
        """处理好友请求和群请求"""
        # 格式: [CQ:reply,id=消息ID]同意/拒绝
        if re.match(r"^\[CQ:reply,id=\d+\](同意|拒绝)$", self.raw_message):
            # 提取回复消息ID和行为
            match = re.match(r"^\[CQ:reply,id=(\d+)\](同意|拒绝)$", self.raw_message)
            if match:
                reply_msg_id = match.group(1)
                action = match.group(2)

                logger.info(
                    f"[{MODULE_NAME}]检测到请求处理: {action}, 回复消息ID: {reply_msg_id}"
                )

                # 发送获取消息详情的API请求
                note = f"{MODULE_NAME}-action={action}-operate_user_id={self.user_id}"
                await get_msg(self.websocket, reply_msg_id, note)
                return True
        return False

    async def handle_forward_message_to_owner_reply(self):
        """处理owner回复转发消息"""
        if self.raw_message.startswith(f"[CQ:reply,id="):
            # 提取被回复消息ID（即数据库里的转发消息id）和回复内容
            # 回复CQ码后面的内容全是需要转发回去的内容，正则提取
            reply_content = re.search(
                r"\[CQ:reply,id=(\d+)\](.*)", self.raw_message, re.DOTALL
            )
            if reply_content:
                forwarded_message_id = reply_content.group(1)
                reply_content = reply_content.group(2)

                # 根据转发消息id获取原始消息内容
                with DataManager() as data_manager:
                    original_message_id = data_manager.get_original_message_id(
                        forwarded_message_id
                    )
                    original_sender_id = data_manager.get_original_sender_id(
                        forwarded_message_id
                    )

                    # 构造回复消息
                    reply_message = f"[CQ:reply,id={original_message_id}]"
                    message = f"{reply_message}{reply_content}"
                    if original_message_id:
                        await send_private_msg_with_cq(
                            self.websocket, original_sender_id, message
                        )
                        logger.success(
                            f"[{MODULE_NAME}]已回复原始消息：发送者ID={original_sender_id}, 原始消息ID={original_message_id}, 回复内容={reply_content}"
                        )
            return True
        return False

    async def handle_auto_agree_friend_verify(self):
        """处理自动同意好友验证"""
        if self.raw_message.lower() == AUTO_AGREE_FRIEND_VERIFY:
            SWITCH_FILE = os.path.join(DATA_DIR, "auto_agree_friend_verify.json")
            if not os.path.exists(SWITCH_FILE):
                with open(SWITCH_FILE, "w") as f:
                    json.dump({}, f)
            with open(SWITCH_FILE, "r") as f:
                switch = json.load(f)
            switch[MODULE_NAME] = not switch.get(MODULE_NAME, False)
            with open(SWITCH_FILE, "w") as f:
                json.dump(switch, f)
            await send_private_msg(
                self.websocket,
                self.user_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(
                        f"自动同意好友验证已{'开启' if switch[MODULE_NAME] else '关闭'}"
                    ),
                ],
            )
            return True
        return False

    def should_ignore_message(self):
        """检查消息是否应该被忽略"""
        # 定义需要忽略的消息正则表达式
        ignore_patterns = [
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",  # UUID
            r".*com\.tencent\.qun\.invite.*",  # 邀请加群的CQ码
            r"教务.*",
            "请求添加你为好友",
            ".*menu",
            r"^我是.*",  # 新增"我是"开头的消息
            r"^&#91;自动回复&#93;.*",  # 新增以"&#91;自动回复&#93;"开头的消息
            "我们已成功添加为好友，现在可以开始聊天啦～",
            r"我已阅读并同意Easy-QFNUJW用户协议",
        ]

        # 检查消息是否包含任何忽略模式
        if any(re.search(pattern, self.raw_message) for pattern in ignore_patterns):
            return True

        # 空消息不处理
        if not self.raw_message.strip():
            return True

        return False

    async def forward_message_to_owner(self):
        """转发消息给owner"""
        if self.should_ignore_message():
            return False

        # 检查是否与上次发送消息的用户相同
        should_send_user_info = MessageProcessor._last_user_id != self.user_id

        if should_send_user_info:
            # 发送用户信息
            await send_private_msg(
                self.websocket,
                OWNER_ID,
                [
                    generate_text_message(
                        f"用户ID🆔：{self.user_id}\n"
                        f"发送时间：{self.formatted_time}\n"
                        f"昵称：{self.nickname}\n"
                        f"来源：{f'群{self.group_id}' if self.group_id else '好友'}消息\n"
                        f"消息内容见下条消息"
                    )
                ],
            )
            await asyncio.sleep(0.4)

        # 发送消息内容
        await send_private_msg(
            self.websocket,
            OWNER_ID,
            self.message,
            note=f"{MODULE_NAME}-{FORWARD_MESSAGE_TO_OWNER}-user_id={self.user_id}-original_message_id={self.message_id}",
        )

        # 存储消息映射关系（发送者ID, 原始消息ID）
        with DataManager() as data_manager:
            data_manager.add_original_message(
                self.user_id, self.message_id, self.raw_message
            )
            logger.success(
                f"[{MODULE_NAME}]已存储上报消息映射：发送者ID={self.user_id}, 原始消息ID={self.message_id}"
            )

        # 更新上次发送消息的用户ID
        MessageProcessor._last_user_id = self.user_id

        return True

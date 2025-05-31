from . import (
    MODULE_NAME,
    BAN_TIME,
    MAX_ATTEMPTS,
    MAX_WARNINGS,
    APPROVE_VERIFICATION,
    REJECT_VERIFICATION,
)
import logger
from datetime import datetime
from core.switchs import is_group_switch_on
from api.group import set_group_ban
from api.message import send_group_msg, send_private_msg
from api.generate import generate_text_message, generate_at_message
import random
from .data_manager import DataManager
from config import OWNER_ID
import asyncio


class GroupNoticeHandler:
    """
    群组通知处理器
    """

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.notice_type = msg.get("notice_type")
        self.sub_type = msg.get("sub_type")
        self.user_id = str(msg.get("user_id"))
        self.group_id = str(msg.get("group_id"))
        self.operator_id = str(msg.get("operator_id"))

    async def handle_group_notice(self):
        """
        处理群聊通知
        """
        try:
            # 如果没开启群聊开关，则不处理
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

            if self.notice_type == "group_decrease":
                await self.handle_group_decrease()
            elif self.notice_type == "group_increase":
                await self.handle_group_increase()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊通知失败: {e}")

    async def handle_group_decrease(self):
        """
        处理群聊成员减少通知
        """
        try:
            if self.sub_type == "leave":
                await self.handle_group_decrease_leave()
            elif self.sub_type == "kick":
                await self.handle_group_decrease_kick()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊成员减少通知失败: {e}")

    async def handle_group_decrease_leave(self):
        """
        处理群聊成员减少 - 主动退群通知
        """
        try:
            # 更新数据库
            with DataManager() as dm:
                dm.update_verify_status(self.user_id, self.group_id, "主动退群")
            # 群内通知
            await send_group_msg(
                self.websocket,
                self.group_id,
                [generate_text_message(f"({self.user_id})退群了。👋")],
                note="del_msg=60",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊成员减少 - 主动退群通知失败: {e}")

    async def handle_group_decrease_kick(self):
        """
        处理群聊成员减少 - 成员被踢通知
        """
        try:
            # 群内通知
            await send_group_msg(
                self.websocket,
                self.group_id,
                [generate_text_message(f"({self.user_id})已被踢出群聊。❌")],
                note="del_msg=60",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊成员减少 - 成员被踢通知失败: {e}")

    async def handle_group_increase(self):
        """
        处理群聊成员增加通知
        """
        try:
            logger.info(
                f"[{MODULE_NAME}]群聊 {self.group_id} 用户 {self.user_id} 增加成员，将进行入群验证"
            )
            # 禁言用户
            await set_group_ban(self.websocket, self.group_id, self.user_id, BAN_TIME)

            # 生成一个6-15位的唯一数字ID，并确保在数据库中唯一，理论上重复的可能性非常小
            for _ in range(10):  # 最多尝试10次
                timestamp = int(datetime.now().timestamp())  # 秒级时间戳
                random_suffix = random.randint(1000, 9999)  # 4位随机数
                full_id = f"{timestamp}{random_suffix}"
                unique_id = full_id[-random.randint(6, 15) :]  # 随机取6-15位
                with DataManager() as dm:
                    if not dm.check_unique_id_exists(unique_id):
                        break
            else:
                logger.error(
                    f"[{MODULE_NAME}]群聊 {self.group_id} 用户 {self.user_id} 生成唯一ID失败，存在重复"
                )
                unique_id = None

            # 存入数据库
            with DataManager() as dm:
                dm.insert_data(
                    self.group_id,
                    self.user_id,
                    unique_id,
                    "未验证",
                    self.time,
                    MAX_ATTEMPTS,
                    MAX_WARNINGS,
                )

            # 发送入群验证消息
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_at_message(self.user_id),
                    generate_text_message(
                        f" ({self.user_id})欢迎加入群聊，请【先加我为好友(自动同意)】(否则无效），然后【私聊我发送验证码】进行验证。\n"
                        f"你的验证码是：【{unique_id}】🎉"
                    ),
                ],
                note="del_msg=30",
            )

            logger.info(
                f"[{MODULE_NAME}]向群聊 {self.group_id} 用户 {self.user_id} 发送入群验证消息"
            )

            # 向管理员上报，包含群号、用户ID、验证码、时间
            await send_private_msg(
                self.websocket,
                OWNER_ID,
                [
                    generate_text_message(
                        f"有新的入群验证请求\n"
                        f"群号：{self.group_id}\n"
                        f"用户ID：{self.user_id}\n"
                        f"验证码唯一ID：{unique_id}\n"
                        f"时间：{self.formatted_time} 🕒\n"
                    ),
                    generate_text_message(
                        f"你可以发送【{APPROVE_VERIFICATION}/{REJECT_VERIFICATION}+{self.group_id}+{self.user_id}】来处理该请求 🛠️"
                    ),
                ],
            )

            # 暂停0.5秒
            await asyncio.sleep(0.5)

            # 向管理员发送处理文本，便于复制
            await send_private_msg(
                self.websocket,
                OWNER_ID,
                [
                    generate_text_message(
                        f"{APPROVE_VERIFICATION} {self.group_id} {self.user_id} ✅"
                    )
                ],
            )
            await send_private_msg(
                self.websocket,
                OWNER_ID,
                [
                    generate_text_message(
                        f"{REJECT_VERIFICATION} {self.group_id} {self.user_id} ❌"
                    )
                ],
            )

            return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊成员增加通知失败: {e}")

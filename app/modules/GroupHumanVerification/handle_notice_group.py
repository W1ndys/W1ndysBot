from . import (
    MODULE_NAME,
    BAN_TIME,
    STATUS_UNVERIFIED,
    STATUS_REJECTED,
    STATUS_LEFT,
    STATUS_UNMUTED,
    STATUS_KICKED,
    NOTE_CONDITION,
    WARNING_COUNT,
)
import uuid
import logger
from datetime import datetime
from core.switchs import is_group_switch_on
from api.group import set_group_ban
from api.message import send_group_msg, delete_msg
from utils.generate import generate_at_message, generate_text_message
from .data_manager import DataManager


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
        self.self_id = str(msg.get("self_id"))
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

            if self.notice_type == "group_admin":
                await self.handle_group_admin()
            elif self.notice_type == "group_ban":
                await self.handle_group_ban()
            elif self.notice_type == "group_card":
                await self.handle_group_card()
            elif self.notice_type == "group_decrease":
                await self.handle_group_decrease()
            elif self.notice_type == "group_increase":
                await self.handle_group_increase()
            elif self.notice_type == "group_recall":
                await self.handle_group_recall()
            elif self.notice_type == "group_upload":
                await self.handle_group_upload()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊通知失败: {e}")

    # 群聊相关通知处理
    async def handle_group_admin(self):
        """
        处理群聊管理员变动通知
        """
        try:
            if self.sub_type == "set":
                await self.handle_group_admin_set()
            elif self.sub_type == "unset":
                await self.handle_group_admin_unset()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊管理员变动通知失败: {e}")

    async def handle_group_admin_set(self):
        """
        处理群聊管理员增加通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊管理员增加通知失败: {e}")

    async def handle_group_admin_unset(self):
        """
        处理群聊管理员减少通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊管理员减少通知失败: {e}")

    async def handle_group_ban(self):
        """
        处理群聊禁言通知
        """
        try:
            if self.sub_type == "ban":
                await self.handle_group_ban_ban()
            elif self.sub_type == "lift_ban":
                await self.handle_group_ban_lift_ban()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊禁言通知失败: {e}")

    async def handle_group_ban_ban(self):
        """
        处理群聊禁言 - 禁言通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊禁言 - 禁言通知失败: {e}")

    async def handle_group_ban_lift_ban(self):
        """
        处理群聊禁言 - 取消禁言通知
        """
        try:
            # 只有操作者不是机器人（即为其他管理员）时，才处理
            if self.operator_id != self.self_id:
                with DataManager() as dm:
                    data = dm.get_data(self.group_id, self.user_id)
                    if data and data["status"] == STATUS_UNVERIFIED:
                        dm.update_status(
                            self.group_id,
                            self.user_id,
                            f"{STATUS_UNMUTED}（{self.operator_id}）",
                        )
                        msg_at = generate_at_message(self.user_id)
                        msg_text = generate_text_message(
                            f"({self.user_id})已被管理员解除禁言，自动视为验证通过。"
                        )

                        if data["message_id"]:
                            await delete_msg(self.websocket, data["message_id"])

                        await send_group_msg(
                            self.websocket,
                            self.group_id,
                            [msg_at, msg_text],
                            note="del_msg=120",
                        )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊禁言 - 取消禁言通知失败: {e}")

    async def handle_group_card(self):
        """
        处理群成员名片更新通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群成员名片更新通知失败: {e}")

    async def handle_group_decrease(self):
        """
        处理群聊成员减少通知
        """
        try:
            if self.sub_type == "leave":
                await self.handle_group_decrease_leave()
            elif self.sub_type == "kick":
                await self.handle_group_decrease_kick()
            elif self.sub_type == "kick_me":
                await self.handle_group_decrease_kick_me()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊成员减少通知失败: {e}")

    async def handle_group_decrease_leave(self):
        """
        处理群聊成员减少 - 主动退群通知
        """
        try:
            with DataManager() as dm:
                data = dm.get_data(self.group_id, self.user_id)
                msg_at = generate_at_message(self.user_id)
                # 存在未验证状态时，更新状态并播报
                if data and data["status"] == STATUS_UNVERIFIED:
                    dm.update_status(self.group_id, self.user_id, STATUS_LEFT)
                    msg_text = generate_text_message(
                        f"({self.user_id})退群了（待验证状态，已标记为离开）"
                    )
                    if data["message_id"]:
                        await delete_msg(self.websocket, data["message_id"])
                else:
                    # 没有状态或不是未验证，直接播报
                    msg_text = generate_text_message(f"({self.user_id})退群了")
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [msg_at, msg_text],
                    note="del_msg=120",
                )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊成员减少 - 主动退群通知失败: {e}")

    async def handle_group_decrease_kick(self):
        """
        处理群聊成员减少 - 成员被踢通知
        """
        try:
            # 无论是被机器人还是其他管理员踢出，都进行处理
            with DataManager() as dm:
                data = dm.get_data(self.group_id, self.user_id)
                msg_at = generate_at_message(self.user_id)
                if data:
                    if data["status"] == STATUS_UNVERIFIED:
                        dm.update_status(self.group_id, self.user_id, STATUS_REJECTED)
                        msg_text = generate_text_message(
                            f"({self.user_id})被管理员踢了(待验证状态，已标记为已拒绝)"
                        )
                        if data["message_id"]:
                            await delete_msg(self.websocket, data["message_id"])
                    else:
                        dm.update_status(self.group_id, self.user_id, STATUS_KICKED)
                        msg_text = generate_text_message(
                            f"({self.user_id})被管理员踢了(非待验证状态，已标记为已踢出)"
                        )
                else:
                    msg_text = generate_text_message(f"({self.user_id})被管理员踢了")

                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [msg_at, msg_text],
                    note="del_msg=30",
                )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊成员减少 - 成员被踢通知失败: {e}")

    async def handle_group_decrease_kick_me(self):
        """
        处理群聊成员减少 - 登录号被踢通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊成员减少 - 登录号被踢通知失败: {e}")

    async def handle_group_increase(self):
        """
        处理群聊成员增加通知
        """
        try:
            # 禁言
            await set_group_ban(self.websocket, self.group_id, self.user_id, BAN_TIME)

            # 生成唯一验证码
            code = str(uuid.uuid4())

            with DataManager() as dm:
                dm.add_data(
                    self.group_id,
                    self.user_id,
                    code,
                    STATUS_UNVERIFIED,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )

            # 群内通知
            msg_at = generate_at_message(self.user_id)
            msg_text = generate_text_message(
                f"({self.user_id}) 欢迎加入群聊！请先私聊我验证码完成人机验证以确保您是真人，你的验证码是下方的UUID字符串，{WARNING_COUNT}不验证将踢出群聊。\n\n"
                f"你可以直接复制此消息全部内容发送给机器人进行验证，无需单独复制验证码，直接临时会话私聊我即可，无需加好友。\n\n"
                f"{code}"
            )
            await send_group_msg(
                self.websocket,
                self.group_id,
                [msg_at, msg_text],
                note=f"{NOTE_CONDITION}-group_id={self.group_id}-user_id={self.user_id}-del_msg=14400",  # 14400=4小时
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊成员增加通知失败: {e}")

    async def handle_group_recall(self):
        """
        处理群聊消息撤回通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊消息撤回通知失败: {e}")

    async def handle_group_upload(self):
        """
        处理群聊文件上传通知
        """
        try:
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊文件上传通知失败: {e}")

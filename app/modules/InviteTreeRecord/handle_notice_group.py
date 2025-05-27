from . import MODULE_NAME
import logger
from core.switchs import is_group_switch_on
from .data_manager import InviteLinkRecordDataManager
from config import OWNER_ID
from api.generate import generate_text_message
from api.message import send_private_msg


class GroupNoticeHandler:
    """
    群组通知处理器
    """

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time")
        self.formatted_time = msg.get("formatted_time")
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
            pass
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
            pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊成员减少 - 主动退群通知失败: {e}")

    async def handle_group_decrease_kick(self):
        """
        处理群聊成员减少 - 成员被踢通知
        """
        try:
            pass
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
            if self.sub_type == "approve":
                await self.handle_group_increase_approve()
            elif self.sub_type == "invite":
                await self.handle_group_increase_invite()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊成员增加通知失败: {e}")

    async def handle_group_increase_approve(self):
        """
        处理群聊成员增加 - 管理员已同意入群通知
        """
        try:
            pass
        except Exception as e:
            logger.error(
                f"[{MODULE_NAME}]处理群聊成员增加 - 管理员已同意入群通知失败: {e}"
            )

    async def handle_group_increase_invite(self):
        """
        处理群聊成员增加 - 管理员邀请入群通知
        """
        try:
            # 检测群开关
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

            # 添加邀请树接记录
            invite_link_record = InviteLinkRecordDataManager(self.websocket, self.msg)
            if invite_link_record.add_invite_link_record():
                # 通知管理员
                await send_private_msg(
                    self.websocket,
                    OWNER_ID,
                    [
                        generate_text_message(
                            f"邀请入群记录通知\n\n"
                            f"邀请者：{self.operator_id}\n"
                            f"被邀请者：{self.user_id}\n"
                            f"群号：{self.group_id}\n"
                            f"邀请时间：{self.formatted_time}\n"
                        )
                    ],
                )
        except Exception as e:
            logger.error(
                f"[{MODULE_NAME}]处理群聊成员增加 - 管理员邀请入群通知失败: {e}"
            )

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

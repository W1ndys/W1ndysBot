from .. import MODULE_NAME
from logger import logger
from datetime import datetime
from core.switchs import is_group_switch_on
from .data_manager import BlackListDataManager
from api.group import set_group_kick
from api.message import send_group_msg, send_private_msg
from utils.generate import generate_text_message, generate_at_message
from config import OWNER_ID


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

            if self.notice_type == "group_increase":
                await self.handle_group_increase()

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊通知失败: {e}")

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
            # 检查新入群用户是否在黑名单中
            await self.check_and_kick_blacklisted_user()
        except Exception as e:
            logger.error(
                f"[{MODULE_NAME}]处理群聊成员增加 - 管理员已同意入群通知失败: {e}"
            )

    async def handle_group_increase_invite(self):
        """
        处理群聊成员增加 - 管理员邀请入群通知
        """
        try:
            # 检查新入群用户是否在黑名单中，如果是则踢出被邀请人和邀请人
            await self.check_and_kick_blacklisted_user_and_inviter()
        except Exception as e:
            logger.error(
                f"[{MODULE_NAME}]处理群聊成员增加 - 管理员邀请入群通知失败: {e}"
            )

    async def check_and_kick_blacklisted_user(self):
        """
        检查用户是否在黑名单中（包括全局黑名单），如果在则踢出并发送警告
        """
        try:
            with BlackListDataManager() as data_manager:
                if data_manager.is_user_blacklisted(self.group_id, self.user_id):
                    # 判断是全局黑名单还是群黑名单
                    is_global = data_manager.is_in_global_blacklist(self.user_id)
                    blacklist_type = "全局黑名单" if is_global else "群黑名单"

                    # 发送警告消息
                    warning_at = generate_at_message(self.user_id)
                    warning_msg = generate_text_message(
                        f"({self.user_id})检测到你是{blacklist_type}用户，将自动将其踢出"
                    )
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [warning_at, warning_msg],
                        note="del_msg=30",
                    )

                    # 踢出用户并拉黑
                    await set_group_kick(
                        self.websocket, self.group_id, self.user_id, True
                    )
                    logger.info(
                        f"[{MODULE_NAME}]已踢出{blacklist_type}用户 {self.user_id} 并拒绝后续加群请求"
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]检查并踢出黑名单用户失败: {e}")

    async def check_and_kick_blacklisted_user_and_inviter(self):
        """
        检查被邀请用户是否在黑名单中（包括全局黑名单），如果在则踢出被邀请人和邀请人，并将邀请人拉黑上报owner
        """
        try:
            with BlackListDataManager() as data_manager:
                if data_manager.is_user_blacklisted(self.group_id, self.user_id):
                    # 判断是全局黑名单还是群黑名单
                    is_global = data_manager.is_in_global_blacklist(self.user_id)
                    blacklist_type = "全局黑名单" if is_global else "群黑名单"

                    # 发送警告消息
                    warning_at_invited = generate_at_message(self.user_id)
                    warning_at_inviter = generate_at_message(self.operator_id)
                    warning_msg = generate_text_message(
                        f"检测到被邀请用户({self.user_id})是{blacklist_type}用户，将踢出被邀请人和邀请人，并将邀请人拉黑"
                    )
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [warning_at_invited, warning_at_inviter, warning_msg],
                    )

                    # 踢出被邀请用户
                    await set_group_kick(
                        self.websocket, self.group_id, self.user_id, True
                    )

                    # 踢出邀请人
                    await set_group_kick(
                        self.websocket, self.group_id, self.operator_id, False
                    )

                    # 将邀请人添加到群黑名单
                    inviter_added = data_manager.add_blacklist(
                        self.group_id, self.operator_id
                    )

                    # 上报给owner
                    if OWNER_ID:
                        report_msg = generate_text_message(
                            f"[{MODULE_NAME}]黑名单邀请警告\n"
                            f"时间: {self.formatted_time}\n"
                            f"群ID: {self.group_id}\n"
                            f"被邀请用户: {self.user_id}({blacklist_type})\n"
                            f"邀请人: {self.operator_id}\n"
                            f"操作: 已踢出双方，邀请人{'已加入黑名单' if inviter_added else '已在黑名单中'}"
                        )
                        await send_private_msg(self.websocket, OWNER_ID, [report_msg])

                    logger.info(
                        f"[{MODULE_NAME}]已踢出{blacklist_type}用户 {self.user_id} 和邀请人 {self.operator_id}，邀请人{'已加入' if inviter_added else '已在'}黑名单"
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]检查并踢出黑名单用户和邀请人失败: {e}")

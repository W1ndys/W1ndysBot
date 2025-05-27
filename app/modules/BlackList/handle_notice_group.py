from . import MODULE_NAME
import logger
from core.switchs import is_group_switch_on
from .data_manager import BlackListDataManager
from api.group import set_group_kick
from api.message import send_group_msg
from api.generate import generate_text_message


class GroupNoticeHandler:
    """
    群组通知处理器
    """

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.websocket = msg.get("websocket")
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
            # 检查新入群用户是否在黑名单中
            await self.check_and_kick_blacklisted_user()
        except Exception as e:
            logger.error(
                f"[{MODULE_NAME}]处理群聊成员增加 - 管理员邀请入群通知失败: {e}"
            )

    async def check_and_kick_blacklisted_user(self):
        """
        检查用户是否在黑名单中，如果在则踢出并发送警告
        """
        try:
            with BlackListDataManager() as data_manager:
                if data_manager.is_in_blacklist(self.group_id, self.user_id):
                    # 发送警告消息
                    warning_msg = generate_text_message(
                        f"检测到黑名单用户 {self.user_id} 进入了群聊，将自动将其踢出"
                    )
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [warning_msg],
                        note="del_msg=30",
                    )

                    # 踢出用户并拉黑
                    await set_group_kick(
                        self.websocket, self.group_id, self.user_id, True
                    )
                    logger.info(
                        f"[{MODULE_NAME}]已踢出黑名单用户 {self.user_id} 并拒绝后续加群请求"
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]检查并踢出黑名单用户失败: {e}")

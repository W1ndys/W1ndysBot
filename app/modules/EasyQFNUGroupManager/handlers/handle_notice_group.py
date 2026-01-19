from .. import MODULE_NAME
from logger import logger
from datetime import datetime
from core.switchs import is_group_switch_on
from api.message import send_group_msg
from utils.generate import generate_at_message, generate_text_message
from .data_manager import DataManager


def get_welcome_message(is_verified: bool = False) -> str:
    """
    生成欢迎消息，自动填入用户QQ号和验证状态

    Args:
        is_verified: 是否已验证

    Returns:
        str: 格式化后的欢迎消息
    """
    verification_status = "✅ 已验证" if is_verified else "❌ 未验证"

    return f"""欢迎加入本群，当前验证状态：{verification_status}

请在问卷地址：https://my.feishu.cn/share/base/form/shrcnfW82NCyVqSXoyzI3QA0z7c 提交能证明在校学生身份的证明（智慧曲园、教务系统截图、学信网等，需带有截图日期、姓名、学号）

经审核通过后解除状态，未经验证的用户将会在入群固定时间后自动踢出

若管理员未审核，被踢出后重新进群即可，相关内容都在群公告

禁止在公开社交平台发布本群相关信息，发现则立即解散群聊关闭服务"""


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
            # 用户退群时删除验证记录
            with DataManager() as dm:
                dm.remove_user(self.user_id, self.group_id)

            # 发送退群播报消息
            await send_group_msg(
                self.websocket,
                self.group_id,
                [generate_text_message(f"{self.user_id} 退群了")],
            )
            logger.info(
                f"[{MODULE_NAME}]成员 {self.user_id} 退出群 {self.group_id}，已发送退群通知"
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群聊成员减少 - 主动退群通知失败: {e}")

    async def handle_group_decrease_kick(self):
        """
        处理群聊成员减少 - 成员被踢通知
        """
        try:
            # 用户被踢时删除验证记录
            with DataManager() as dm:
                dm.remove_user(self.user_id, self.group_id)
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
            await self._handle_new_member()
        except Exception as e:
            logger.error(
                f"[{MODULE_NAME}]处理群聊成员增加 - 管理员已同意入群通知失败: {e}"
            )

    async def handle_group_increase_invite(self):
        """
        处理群聊成员增加 - 管理员邀请入群通知
        """
        try:
            await self._handle_new_member()
        except Exception as e:
            logger.error(
                f"[{MODULE_NAME}]处理群聊成员增加 - 管理员邀请入群通知失败: {e}"
            )

    async def _handle_new_member(self):
        """
        处理新成员入群的公共逻辑
        1. 记录用户入群信息到数据库
        2. 发送欢迎消息并艾特用户
        """
        try:
            # 记录用户入群信息并检查验证状态
            with DataManager() as dm:
                dm.add_user(self.user_id, self.group_id, self.time)
                # 获取用户验证状态
                is_verified = dm.is_user_verified(self.user_id, self.group_id)

            # 发送欢迎消息，艾特新用户
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_at_message(self.user_id),
                    generate_text_message(f"({self.user_id})\n"),
                    generate_text_message(get_welcome_message(is_verified)),
                ],
            )
            logger.info(
                f"[{MODULE_NAME}]新成员 {self.user_id} 入群 {self.group_id}，已发送欢迎消息（验证状态：{'已验证' if is_verified else '未验证'}）"
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理新成员入群失败: {e}")

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

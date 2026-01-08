from .. import MODULE_NAME, SWITCH_NAME, VERIFY_COMMAND, PENDING_LIST_COMMAND
from core.menu_manager import MENU_COMMAND
from logger import logger
from core.switchs import is_group_switch_on, handle_module_group_switch
from utils.auth import is_system_admin, is_group_admin
from api.message import send_group_msg
from utils.generate import (
    generate_text_message,
    generate_reply_message,
    generate_at_message,
)
from datetime import datetime
from .data_manager import DataManager
from core.menu_manager import MenuManager
import re


class GroupMessageHandler:
    """群消息处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.sub_type = msg.get("sub_type", "")  # 子类型，只有normal
        self.group_id = str(msg.get("group_id", ""))  # 群号
        self.message_id = str(msg.get("message_id", ""))  # 消息ID
        self.user_id = str(msg.get("user_id", ""))  # 发送者QQ号
        self.message = msg.get("message", {})  # 消息段数组
        self.raw_message = msg.get("raw_message", "")  # 原始消息
        self.sender = msg.get("sender", {})  # 发送者信息
        self.nickname = self.sender.get("nickname", "")  # 昵称
        self.card = self.sender.get("card", "")  # 群名片
        self.role = self.sender.get("role", "")  # 群身份

    async def _handle_switch_command(self):
        """
        处理群聊开关命令
        """
        if self.raw_message.lower() == SWITCH_NAME.lower():
            # 鉴权
            if not is_system_admin(self.user_id):
                logger.error(f"[{MODULE_NAME}]{self.user_id}无权限切换群聊开关")
                return True
            await handle_module_group_switch(
                MODULE_NAME,
                self.websocket,
                self.group_id,
                self.message_id,
            )
            return True
        return False

    async def _handle_menu_command(self):
        """
        处理菜单命令（无视开关状态）
        """
        if self.raw_message.lower() == f"{SWITCH_NAME}{MENU_COMMAND}".lower():
            menu_text = MenuManager.get_module_commands_text(MODULE_NAME)
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(menu_text),
                ],
                note="del_msg=30",
            )
            return True
        return False

    async def _handle_verify_command(self):
        """
        处理验证通过命令
        格式：通过+QQ号 或 通过+艾特 或 通过+多个QQ号（空格/换行等分隔）
        例如：通过123456 或 通过@用户 或 通过123456 789012
        """
        # 检查权限：必须是管理员或系统管理员
        if not is_group_admin(self.role) and not is_system_admin(self.user_id):
            return False

        # 检查消息是否以"通过"开头
        if not self.raw_message.startswith(VERIFY_COMMAND):
            return False

        # 收集目标用户ID列表
        target_user_ids = []

        # 先检查是否有艾特消息
        for segment in self.message:
            if segment.get("type") == "at":
                qq = segment.get("data", {}).get("qq")
                if qq:
                    target_user_ids.append(str(qq))

        # 如果没有艾特，尝试从消息中提取QQ号
        if not target_user_ids:
            # 提取"通过"后面的内容
            content = self.raw_message[len(VERIFY_COMMAND) :].strip()
            # 使用正则匹配所有QQ号（5-11位数字）
            matches = re.findall(r"\d{5,11}", content)
            target_user_ids = matches

        if not target_user_ids:
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message("验证失败：请指定有效的QQ号或艾特用户"),
                ],
                note="del_msg=30",
            )
            return True

        # 执行验证
        success_list = []
        already_verified_list = []
        not_found_list = []

        with DataManager() as dm:
            for target_user_id in target_user_ids:
                result = dm.verify_user(target_user_id, self.group_id)
                if result == "success":
                    success_list.append(target_user_id)
                elif result == "already_verified":
                    already_verified_list.append(target_user_id)
                else:  # not_found or error
                    not_found_list.append(target_user_id)

        # 构建响应消息
        message_parts = [generate_reply_message(self.message_id)]

        if success_list:
            message_parts.append(
                generate_text_message(f"✅ 验证通过 {len(success_list)} 人：")
            )
            # 艾特验证通过的用户
            for uid in success_list:
                message_parts.append(generate_at_message(uid))
                message_parts.append(generate_text_message(f"({uid}) "))
            message_parts.append(generate_text_message("\n"))

        if already_verified_list:
            message_parts.append(
                generate_text_message(f"⚠️ 已验证过 {len(already_verified_list)} 人：")
            )
            # 艾特已验证的用户
            for uid in already_verified_list:
                message_parts.append(generate_at_message(uid))
                message_parts.append(generate_text_message(f"({uid}) "))
            message_parts.append(generate_text_message("\n"))

        if not_found_list:
            message_parts.append(
                generate_text_message(
                    f"❌ 记录不存在 {len(not_found_list)} 人：{', '.join(not_found_list)}"
                )
            )

        await send_group_msg(
            self.websocket,
            self.group_id,
            message_parts,
        )

        logger.info(
            f"[{MODULE_NAME}]管理员 {self.user_id} 批量验证：成功 {len(success_list)} 人，"
            f"已验证 {len(already_verified_list)} 人，记录不存在 {len(not_found_list)} 人"
        )
        return True

    async def _handle_pending_list_command(self):
        """
        处理查看待验证列表命令
        格式：待验证
        """
        # 检查权限：必须是管理员或系统管理员
        if not is_group_admin(self.role) and not is_system_admin(self.user_id):
            return False

        # 检查消息是否为"待验证"
        if self.raw_message.strip() != PENDING_LIST_COMMAND:
            return False

        # 获取待验证用户列表
        with DataManager() as dm:
            pending_users = dm.get_pending_users_by_group(self.group_id)

        if not pending_users:
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message("当前没有待验证的用户"),
                ],
                note="del_msg=30",
            )
            return True

        # 构建消息
        lines = [f"📋 待验证用户列表（共 {len(pending_users)} 人）："]
        for user in pending_users:
            join_time = datetime.fromtimestamp(user["join_time"]).strftime(
                "%Y-%m-%d %H:%M"
            )
            lines.append(f"• {user['user_id']}（入群：{join_time}）")

        await send_group_msg(
            self.websocket,
            self.group_id,
            [
                generate_reply_message(self.message_id),
                generate_text_message("\n".join(lines)),
            ],
            note="del_msg=60",
        )

        logger.info(
            f"[{MODULE_NAME}]管理员 {self.user_id} 查看待验证列表，共 {len(pending_users)} 人"
        )
        return True

    async def handle(self):
        """
        处理群消息
        """
        try:
            # 处理群聊开关命令
            if await self._handle_switch_command():
                return

            # 处理菜单命令
            if await self._handle_menu_command():
                return

            # 如果没开启群聊开关，则不处理
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

            # 处理验证通过命令
            if await self._handle_verify_command():
                return

            # 处理查看待验证列表命令
            if await self._handle_pending_list_command():
                return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

from .. import MODULE_NAME, SWITCH_NAME, VERIFY_COMMAND
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
        格式：通过+QQ号 或 通过+艾特
        例如：通过123456 或 通过@用户
        """
        # 检查权限：必须是管理员或系统管理员
        if not is_group_admin(self.role) and not is_system_admin(self.user_id):
            return False

        # 检查消息是否以"通过"开头
        if not self.raw_message.startswith(VERIFY_COMMAND):
            return False

        # 提取目标用户ID
        target_user_id = None

        # 先检查是否有艾特消息
        for segment in self.message:
            if segment.get("type") == "at":
                qq = segment.get("data", {}).get("qq")
                if qq:
                    target_user_id = str(qq)
                    break

        # 如果没有艾特，尝试从消息中提取QQ号
        if not target_user_id:
            # 提取"通过"后面的内容
            content = self.raw_message[len(VERIFY_COMMAND) :].strip()
            # 使用正则匹配纯数字QQ号
            match = re.match(r"^(\d{5,11})$", content)
            if match:
                target_user_id = match.group(1)

        if not target_user_id:
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
        with DataManager() as dm:
            if dm.verify_user(target_user_id, self.group_id):
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_at_message(target_user_id),
                        generate_text_message(f"✅ 用户 {target_user_id} 验证通过"),
                    ],
                )
                logger.info(
                    f"[{MODULE_NAME}]管理员 {self.user_id} 验证通过用户 {target_user_id}"
                )
            else:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(
                            f"验证失败：用户 {target_user_id} 未找到待验证记录或已验证"
                        ),
                    ],
                    note="del_msg=30",
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

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

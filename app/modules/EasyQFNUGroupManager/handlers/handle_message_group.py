from .. import (
    MODULE_NAME,
    SWITCH_NAME,
    VERIFY_COMMAND,
    PENDING_LIST_COMMAND,
    UNRECORDED_LIST_COMMAND,
    TIMEOUT_HOURS,
)
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
from core.get_group_member_list import get_group_member_user_ids, is_user_admin_or_owner
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
        支持无记录用户直接通过并自动添加记录
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
        added_and_verified_list = []  # 无记录用户直接添加并验证

        with DataManager() as dm:
            for target_user_id in target_user_ids:
                result = dm.verify_user(target_user_id, self.group_id)
                if result == "success":
                    success_list.append(target_user_id)
                elif result == "already_verified":
                    already_verified_list.append(target_user_id)
                elif result == "not_found":
                    # 无记录用户，直接添加记录并设为通过状态
                    add_result = dm.add_and_verify_user(target_user_id, self.group_id)
                    if add_result == "success":
                        added_and_verified_list.append(target_user_id)

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

        if added_and_verified_list:
            message_parts.append(
                generate_text_message(
                    f"✅ 无记录用户已添加并验证 {len(added_and_verified_list)} 人："
                )
            )
            # 艾特添加并验证的用户
            for uid in added_and_verified_list:
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

        # 获取剩余未验证用户列表（包括待验证和无记录用户）
        with DataManager() as dm:
            pending_users = dm.get_pending_users_by_group(self.group_id)
            recorded_user_ids = dm.get_all_recorded_user_ids(self.group_id)

        # 获取群成员列表，找出无记录用户（排除管理员和群主）
        group_member_ids = get_group_member_user_ids(self.group_id)
        unrecorded_users = []
        if group_member_ids:
            for user_id in group_member_ids:
                if user_id not in recorded_user_ids:
                    # 忽略管理员和群主
                    if not is_user_admin_or_owner(self.group_id, user_id):
                        unrecorded_users.append(user_id)

        # 显示剩余未验证用户（待验证 + 无记录）
        total_unverified = len(pending_users) + len(unrecorded_users)
        if total_unverified > 0:
            message_parts.append(
                generate_text_message(
                    f"\n📢 没放群里发并且没回复就是没通过，或者看不到姓名学号，无法核实在校真实身份，剩余未验证用户（{total_unverified} 人）：\n"
                )
            )
            # 先显示待验证用户
            if pending_users:
                message_parts.append(
                    generate_text_message(f"待验证（{len(pending_users)} 人）：")
                )
                for user in pending_users:
                    message_parts.append(generate_at_message(user["user_id"]))
                    message_parts.append(generate_text_message(" "))
                message_parts.append(generate_text_message("\n"))
            # 再显示无记录用户
            if unrecorded_users:
                message_parts.append(
                    generate_text_message(f"无记录（{len(unrecorded_users)} 人）：")
                )
                for user_id in unrecorded_users:
                    message_parts.append(generate_at_message(user_id))
                    message_parts.append(generate_text_message(" "))

        await send_group_msg(
            self.websocket,
            self.group_id,
            message_parts,
        )

        logger.info(
            f"[{MODULE_NAME}]管理员 {self.user_id} 批量验证：成功 {len(success_list)} 人，"
            f"无记录添加 {len(added_and_verified_list)} 人，"
            f"已验证 {len(already_verified_list)} 人"
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
        message_parts = [
            generate_reply_message(self.message_id),
            generate_text_message(
                f"📋 待验证用户列表（共 {len(pending_users)} 人）：\n"
            ),
        ]

        for user in pending_users:
            join_time = datetime.fromtimestamp(user["join_time"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            message_parts.append(generate_at_message(user["user_id"]))
            message_parts.append(generate_text_message(f"({join_time})\n"))

        message_parts.append(
            generate_text_message(
                f"请及时验证，入群{TIMEOUT_HOURS}小时后自动踢出未验证用户\n"
                "请私聊群主提交：\n"
                "1.能证明在校学生身份的证明（智慧曲园、教务系统截图、学信网等，需带有截图日期、姓名、学号）\n"
                "2.你的QQ号(单条消息发送，勿合并发送，只发QQ号即可无需携带其他字符)\n\n"
                "经审核通过后解除状态，未经验证的用户将会在入群固定时间后自动踢出。若群主未回复，被踢出后重新进群即可"
            )
        )

        await send_group_msg(self.websocket, self.group_id, message_parts)

        logger.info(
            f"[{MODULE_NAME}]管理员 {self.user_id} 查看待验证列表，共 {len(pending_users)} 人"
        )
        return True

    async def _handle_unrecorded_list_command(self):
        """
        处理查看无记录成员列表命令
        格式：无记录
        用于检测数据库内无记录但在群内的成员
        """
        # 检查权限：必须是管理员或系统管理员
        if not is_group_admin(self.role) and not is_system_admin(self.user_id):
            return False

        # 检查消息是否为"无记录"
        if self.raw_message.strip() != UNRECORDED_LIST_COMMAND:
            return False

        # 获取群成员列表（从Core数据目录）
        group_member_ids = get_group_member_user_ids(self.group_id)

        if not group_member_ids:
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message("无法获取群成员列表，请稍后再试"),
                ],
                note="del_msg=30",
            )
            return True

        # 获取数据库中已记录的用户ID集合
        with DataManager() as dm:
            recorded_user_ids = dm.get_all_recorded_user_ids(self.group_id)

        # 找出在群内但数据库无记录的成员（排除管理员和群主）
        unrecorded_users = []
        for user_id in group_member_ids:
            if user_id not in recorded_user_ids:
                # 忽略管理员和群主
                if not is_user_admin_or_owner(self.group_id, user_id):
                    unrecorded_users.append(user_id)

        if not unrecorded_users:
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(
                        "当前没有无记录的群成员（所有成员都在数据库中有记录）"
                    ),
                ],
                note="del_msg=30",
            )
            return True

        # 构建消息
        message_parts = [
            generate_reply_message(self.message_id),
            generate_text_message(
                f"📋 无记录成员列表（共 {len(unrecorded_users)} 人）：\n"
                f"以下成员在群内但数据库中无入群记录\n\n"
            ),
        ]

        for user_id in unrecorded_users:
            message_parts.append(generate_at_message(user_id))
            message_parts.append(generate_text_message(f"({user_id})\n"))

        message_parts.append(
            generate_text_message(f"\n提示：可使用 通过+QQ号 命令为他们添加验证记录")
        )

        await send_group_msg(self.websocket, self.group_id, message_parts)

        logger.info(
            f"[{MODULE_NAME}]管理员 {self.user_id} 查看无记录成员列表，共 {len(unrecorded_users)} 人"
        )
        return True

    async def _handle_auto_verify_from_numbers(self):
        """
        智能验证：从群主消息中提取数字并自动验证待验证用户
        发送群消息提醒验证结果
        新逻辑：先获取所有未验证用户的QQ号，然后检查这些QQ号是否被包含在群主消息的数字中
        这样可以实现消息内无空格或者间隔符号也能智能匹配到
        """
        # 1. 权限检查：必须是群主
        if self.role != "owner" and not is_system_admin(self.user_id):
            return False

        # 2. 提取消息中的所有数字（去除非数字字符，合并成一个字符串）
        all_digits = re.sub(r"\D", "", self.raw_message)
        if not all_digits:
            return False

        # 3. 获取本群所有未验证用户的QQ号
        with DataManager() as dm:
            pending_users = dm.get_pending_users_by_group(self.group_id)

        if not pending_users:
            return False

        # 4. 检查每个待验证用户的QQ号是否被包含在消息数字字符串中
        success_list = []
        with DataManager() as dm:
            for user in pending_users:
                user_id = user["user_id"]
                # 检查该QQ号是否作为子串包含在消息的所有数字中
                if user_id in all_digits:
                    # 执行验证
                    result = dm.verify_user(user_id, self.group_id)
                    if result == "success":
                        success_list.append(user_id)

        # 5. 如果有验证成功的用户，发送群消息提醒
        if success_list:
            message_parts = [generate_reply_message(self.message_id)]
            message_parts.append(
                generate_text_message(f"🤖 智能验证通过 {len(success_list)} 人：")
            )
            # 艾特验证通过的用户
            for uid in success_list:
                message_parts.append(generate_at_message(uid))
                message_parts.append(generate_text_message(f"({uid}) "))

            await send_group_msg(
                self.websocket,
                self.group_id,
                message_parts,
            )

            logger.info(
                f"[{MODULE_NAME}]智能验证：管理员 {self.user_id} "
                f"消息中自动验证了 {len(success_list)} 个用户"
            )

        return False  # 返回False，不阻止其他处理器

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

            # 处理查看无记录成员列表命令
            if await self._handle_unrecorded_list_command():
                return

            # 新增：智能验证（放在最后，不阻止其他处理）
            await self._handle_auto_verify_from_numbers()

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

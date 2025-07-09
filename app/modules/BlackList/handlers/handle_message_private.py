from .. import MODULE_NAME, SWITCH_NAME
from core.menu_manager import MENU_COMMAND
import logger
from core.switchs import is_private_switch_on, handle_module_private_switch
from api.message import send_private_msg
from utils.generate import generate_text_message, generate_reply_message
from datetime import datetime
from core.menu_manager import MenuManager
from utils.auth import is_system_admin
from .handle_blacklist import BlackListHandle
from .. import (
    GLOBAL_BLACKLIST_ADD_COMMAND,
    GLOBAL_BLACKLIST_REMOVE_COMMAND,
    GLOBAL_BLACKLIST_LIST_COMMAND,
    GLOBAL_BLACKLIST_CLEAR_COMMAND,
    PRIVATE_BLACKLIST_ADD_COMMAND,
    PRIVATE_BLACKLIST_REMOVE_COMMAND,
    PRIVATE_BLACKLIST_LIST_COMMAND,
    PRIVATE_BLACKLIST_CLEAR_COMMAND,
)


class PrivateMessageHandler:
    """私聊消息处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.sub_type = msg.get("sub_type", "")  # 子类型,friend/group
        self.user_id = str(msg.get("user_id", ""))  # 发送者QQ号
        self.message_id = str(msg.get("message_id", ""))  # 消息ID
        self.message = msg.get("message", {})  # 消息段数组
        self.raw_message = msg.get("raw_message", "")  # 原始消息
        self.sender = msg.get("sender", {})  # 发送者信息
        self.nickname = self.sender.get("nickname", "")  # 昵称

    async def handle(self):
        """
        处理私聊消息
        """
        try:
            if self.raw_message.lower() == SWITCH_NAME.lower():
                # 鉴权
                if not is_system_admin(self.user_id):
                    return
                await handle_module_private_switch(
                    MODULE_NAME,
                    self.websocket,
                    self.user_id,
                    self.message_id,
                )
                return

            # 处理菜单命令（无视开关状态）
            if self.raw_message.lower() == f"{SWITCH_NAME}{MENU_COMMAND}".lower():
                menu_text = MenuManager.get_module_commands_text(MODULE_NAME)
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(menu_text),
                    ],
                    note="del_msg=30",
                )
                return

            # 如果没开启私聊开关，则不处理
            if not is_private_switch_on(MODULE_NAME):
                return

            # 处理全局黑名单命令（只有系统管理员可用）
            if is_system_admin(self.user_id):
                # 创建一个临时的消息对象，将user_id作为group_id传递给BlackListHandle
                # 因为BlackListHandle的回复方法中使用了group_id，我们需要适配私聊场景
                temp_msg = self.msg.copy()
                temp_msg["group_id"] = self.user_id  # 将私聊用户ID作为group_id传递

                blacklist_handler = BlackListHandlePrivate(self.websocket, temp_msg)

                # 处理显式的全局黑名单命令
                if self.raw_message.startswith(GLOBAL_BLACKLIST_ADD_COMMAND):
                    await blacklist_handler.add_global_blacklist()
                    return
                elif self.raw_message.startswith(GLOBAL_BLACKLIST_REMOVE_COMMAND):
                    await blacklist_handler.remove_global_blacklist()
                    return
                elif self.raw_message.startswith(GLOBAL_BLACKLIST_LIST_COMMAND):
                    await blacklist_handler.list_global_blacklist()
                    return
                elif self.raw_message.startswith(GLOBAL_BLACKLIST_CLEAR_COMMAND):
                    await blacklist_handler.clear_global_blacklist()
                    return

                # 处理私聊中的普通拉黑命令（视为全局拉黑）
                elif self.raw_message.startswith(PRIVATE_BLACKLIST_ADD_COMMAND):
                    await blacklist_handler.add_global_blacklist_private()
                    return
                elif self.raw_message.startswith(PRIVATE_BLACKLIST_REMOVE_COMMAND):
                    await blacklist_handler.remove_global_blacklist_private()
                    return
                elif self.raw_message.startswith(PRIVATE_BLACKLIST_LIST_COMMAND):
                    await blacklist_handler.list_global_blacklist()
                    return
                elif self.raw_message.startswith(PRIVATE_BLACKLIST_CLEAR_COMMAND):
                    await blacklist_handler.clear_global_blacklist()
                    return

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理私聊消息失败: {e}")


class BlackListHandlePrivate(BlackListHandle):
    """私聊版本的黑名单处理器"""

    def __init__(self, websocket, msg):
        super().__init__(websocket, msg)
        # 私聊场景下，使用user_id作为目标ID
        self.target_id = self.user_id

    async def add_global_blacklist(self):
        """
        添加全局黑名单 - 私聊版本
        """
        try:
            # 删除命令
            self.raw_message = self.raw_message.replace(
                GLOBAL_BLACKLIST_ADD_COMMAND, ""
            ).strip()

            # 解析QQ号
            user_ids = []

            # 处理at消息
            import re

            at_pattern = r"\[CQ:at,qq=(\d+)\]"
            at_matches = re.findall(at_pattern, self.raw_message)
            if at_matches:
                user_ids.extend(at_matches)
            else:
                # 处理纯QQ号
                qq_numbers = self.raw_message.split()
                for qq in qq_numbers:
                    if qq.isdigit():
                        user_ids.append(qq)

            if not user_ids:
                logger.error(f"[{MODULE_NAME}]未找到有效的QQ号")
                reply_message = "请提供有效的QQ号或@用户"
                await send_private_msg(
                    self.websocket,
                    self.target_id,
                    [
                        generate_reply_message(reply_message),
                        generate_text_message(reply_message),
                    ],
                )
                return False

            # 添加全局黑名单
            from .data_manager import BlackListDataManager

            success_users = []
            already_exists_users = []

            with BlackListDataManager() as data_manager:
                for user_id in user_ids:
                    if data_manager.add_global_blacklist(user_id):
                        success_users.append(user_id)
                    else:
                        already_exists_users.append(user_id)

            # 构建反馈消息
            reply_parts = []
            if success_users:
                reply_parts.append(f"成功添加到全局黑名单：{', '.join(success_users)}")
            if already_exists_users:
                reply_parts.append(
                    f"已在全局黑名单中：{', '.join(already_exists_users)}"
                )

            reply_message = "\n".join(reply_parts) if reply_parts else "操作完成"

            await send_private_msg(
                self.websocket,
                self.target_id,
                [
                    generate_reply_message(reply_message),
                    generate_text_message(reply_message),
                ],
            )

            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]添加全局黑名单失败: {e}")
            return False

    async def remove_global_blacklist(self):
        """
        移除全局黑名单 - 私聊版本
        """
        try:
            # 删除命令
            self.raw_message = self.raw_message.replace(
                GLOBAL_BLACKLIST_REMOVE_COMMAND, ""
            ).strip()

            # 解析QQ号
            user_ids = []

            # 处理at消息
            import re

            at_pattern = r"\[CQ:at,qq=(\d+)\]"
            at_matches = re.findall(at_pattern, self.raw_message)
            if at_matches:
                user_ids.extend(at_matches)
            else:
                # 处理纯QQ号
                qq_numbers = self.raw_message.split()
                for qq in qq_numbers:
                    if qq.isdigit():
                        user_ids.append(qq)

            if not user_ids:
                logger.error(f"[{MODULE_NAME}]未找到有效的QQ号")
                reply_message = "请提供有效的QQ号或@用户"
                await send_private_msg(
                    self.websocket,
                    self.target_id,
                    [
                        generate_reply_message(reply_message),
                        generate_text_message(reply_message),
                    ],
                )
                return False

            # 移除全局黑名单
            from .data_manager import BlackListDataManager

            success_users = []
            not_exists_users = []

            with BlackListDataManager() as data_manager:
                for user_id in user_ids:
                    if data_manager.is_in_global_blacklist(user_id):
                        if data_manager.remove_global_blacklist(user_id):
                            success_users.append(user_id)
                    else:
                        not_exists_users.append(user_id)

            # 构建反馈消息
            reply_parts = []
            if success_users:
                reply_parts.append(
                    f"成功从全局黑名单中移除：{', '.join(success_users)}"
                )
            if not_exists_users:
                reply_parts.append(f"不在全局黑名单中：{', '.join(not_exists_users)}")

            reply_message = "\n".join(reply_parts) if reply_parts else "操作完成"

            await send_private_msg(
                self.websocket,
                self.target_id,
                [
                    generate_reply_message(reply_message),
                    generate_text_message(reply_message),
                ],
            )

            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]移除全局黑名单失败: {e}")
            return False

    async def list_global_blacklist(self):
        """
        查看全局黑名单 - 私聊版本
        """
        try:
            from .data_manager import BlackListDataManager

            with BlackListDataManager() as data_manager:
                blacklist = data_manager.get_global_blacklist()

            if not blacklist:
                reply_message = "当前没有全局黑名单用户"
            else:
                blacklist_users = []
                for user_id, created_at in blacklist:
                    blacklist_users.append(f"{user_id}（添加时间：{created_at}）")

                reply_message = (
                    f"全局黑名单用户（共{len(blacklist)}人）：\n"
                    + "\n".join(blacklist_users)
                )

            await send_private_msg(
                self.websocket,
                self.target_id,
                [
                    generate_reply_message(reply_message),
                    generate_text_message(reply_message),
                ],
            )

            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]查看全局黑名单失败: {e}")
            return False

    async def clear_global_blacklist(self):
        """
        清空全局黑名单 - 私聊版本
        """
        try:
            # 获取全局黑名单
            from .data_manager import BlackListDataManager

            with BlackListDataManager() as data_manager:
                blacklist = data_manager.get_global_blacklist()

            if not blacklist:
                reply_message = "当前没有全局黑名单用户"
                await send_private_msg(
                    self.websocket,
                    self.target_id,
                    [
                        generate_reply_message(reply_message),
                        generate_text_message(reply_message),
                    ],
                )
                return True

            # 移除所有全局黑名单
            for user_id, _ in blacklist:
                with BlackListDataManager() as data_manager:
                    data_manager.remove_global_blacklist(user_id)

            reply_message = f"已清空所有全局黑名单用户（共{len(blacklist)}人）"
            await send_private_msg(
                self.websocket,
                self.target_id,
                [
                    generate_reply_message(reply_message),
                    generate_text_message(reply_message),
                ],
            )

            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]清空全局黑名单失败: {e}")
            return False

    async def add_global_blacklist_private(self):
        """
        私聊中的拉黑命令（视为全局拉黑）
        """
        try:
            # 删除命令
            self.raw_message = self.raw_message.replace(
                PRIVATE_BLACKLIST_ADD_COMMAND, ""
            ).strip()

            # 解析QQ号
            user_ids = []

            # 处理at消息
            import re

            at_pattern = r"\[CQ:at,qq=(\d+)\]"
            at_matches = re.findall(at_pattern, self.raw_message)
            if at_matches:
                user_ids.extend(at_matches)
            else:
                # 处理纯QQ号
                qq_numbers = self.raw_message.split()
                for qq in qq_numbers:
                    if qq.isdigit():
                        user_ids.append(qq)

            if not user_ids:
                logger.error(f"[{MODULE_NAME}]未找到有效的QQ号")
                reply_message = "请提供有效的QQ号或@用户"
                await send_private_msg(
                    self.websocket,
                    self.target_id,
                    [
                        generate_reply_message(reply_message),
                        generate_text_message(reply_message),
                    ],
                )
                return False

            # 添加全局黑名单
            from .data_manager import BlackListDataManager

            success_users = []
            already_exists_users = []

            with BlackListDataManager() as data_manager:
                for user_id in user_ids:
                    if data_manager.add_global_blacklist(user_id):
                        success_users.append(user_id)
                    else:
                        already_exists_users.append(user_id)

            # 构建反馈消息
            reply_parts = []
            if success_users:
                reply_parts.append(f"成功添加到全局黑名单：{', '.join(success_users)}")
            if already_exists_users:
                reply_parts.append(
                    f"已在全局黑名单中：{', '.join(already_exists_users)}"
                )

            reply_message = "\n".join(reply_parts) if reply_parts else "操作完成"

            await send_private_msg(
                self.websocket,
                self.target_id,
                [
                    generate_reply_message(reply_message),
                    generate_text_message(reply_message),
                ],
            )

            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]私聊拉黑失败: {e}")
            return False

    async def remove_global_blacklist_private(self):
        """
        私聊中的解黑命令（视为全局解黑）
        """
        try:
            # 删除命令
            self.raw_message = self.raw_message.replace(
                PRIVATE_BLACKLIST_REMOVE_COMMAND, ""
            ).strip()

            # 解析QQ号
            user_ids = []

            # 处理at消息
            import re

            at_pattern = r"\[CQ:at,qq=(\d+)\]"
            at_matches = re.findall(at_pattern, self.raw_message)
            if at_matches:
                user_ids.extend(at_matches)
            else:
                # 处理纯QQ号
                qq_numbers = self.raw_message.split()
                for qq in qq_numbers:
                    if qq.isdigit():
                        user_ids.append(qq)

            if not user_ids:
                logger.error(f"[{MODULE_NAME}]未找到有效的QQ号")
                reply_message = "请提供有效的QQ号或@用户"
                await send_private_msg(
                    self.websocket,
                    self.target_id,
                    [
                        generate_reply_message(reply_message),
                        generate_text_message(reply_message),
                    ],
                )
                return False

            # 移除全局黑名单
            from .data_manager import BlackListDataManager

            success_users = []
            not_exists_users = []

            with BlackListDataManager() as data_manager:
                for user_id in user_ids:
                    if data_manager.is_in_global_blacklist(user_id):
                        if data_manager.remove_global_blacklist(user_id):
                            success_users.append(user_id)
                    else:
                        not_exists_users.append(user_id)

            # 构建反馈消息
            reply_parts = []
            if success_users:
                reply_parts.append(
                    f"成功从全局黑名单中移除：{', '.join(success_users)}"
                )
            if not_exists_users:
                reply_parts.append(f"不在全局黑名单中：{', '.join(not_exists_users)}")

            reply_message = "\n".join(reply_parts) if reply_parts else "操作完成"

            await send_private_msg(
                self.websocket,
                self.target_id,
                [
                    generate_reply_message(reply_message),
                    generate_text_message(reply_message),
                ],
            )

            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]私聊解黑失败: {e}")
            return False

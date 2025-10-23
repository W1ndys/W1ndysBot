from .. import MODULE_NAME, SWITCH_NAME
from core.menu_manager import MENU_COMMAND
from logger import logger
from core.switchs import is_private_switch_on, handle_module_private_switch
from api.message import send_private_msg, get_msg
from utils.generate import (
    generate_text_message,
    generate_reply_message,
    generate_at_message,
)
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
    PRIVATE_BLACKLIST_SCAN_COMMAND,
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
                elif self.raw_message.startswith(PRIVATE_BLACKLIST_SCAN_COMMAND):
                    await blacklist_handler.scan_blacklist_private()
                    return

                if (
                    self.raw_message.startswith("[CQ:reply,id=")
                    and PRIVATE_BLACKLIST_ADD_COMMAND in self.raw_message
                ):
                    # 检查是否是单纯的回复拉黑（不包含其他QQ号或@）
                    reply_content = self.raw_message.split("]", 1)[1].strip()
                    if reply_content == PRIVATE_BLACKLIST_ADD_COMMAND:
                        # 这是回复某条消息进行拉黑的情况
                        await blacklist_handler.add_global_blacklist_by_reply()
                    else:
                        # 这是回复消息同时包含其他拉黑目标的情况
                        await blacklist_handler.add_global_blacklist_private()
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

    async def add_global_blacklist_by_reply(self):
        """
        通过回复消息进行拉黑
        """
        try:
            # 提取回复消息的ID
            import re

            reply_pattern = r"\[CQ:reply,id=(\d+)\]"
            reply_match = re.search(reply_pattern, self.raw_message)

            if not reply_match:
                logger.error(f"[{MODULE_NAME}]未找到有效的回复消息ID")
                reply_message = "无法获取回复消息ID"
                await send_private_msg(
                    self.websocket,
                    self.target_id,
                    [
                        generate_reply_message(reply_message),
                        generate_text_message(reply_message),
                    ],
                )
                return False

            reply_msg_id = reply_match.group(1)
            logger.info(f"[{MODULE_NAME}]提取到回复消息ID: {reply_msg_id}")

            # 调用获取消息详情的方法
            await get_msg(
                self.websocket,
                reply_msg_id,
                note=f"{MODULE_NAME}-action={PRIVATE_BLACKLIST_ADD_COMMAND}",
            )

            return True

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]通过回复消息拉黑失败: {e}")
            return False

    async def scan_blacklist_private(self):
        """
        私聊中的扫黑命令
        支持两种格式：
        - 扫黑：扫描所有开启黑名单功能的群
        - 扫黑 群号：扫描指定群
        使用等待+读文件的方式，逻辑简单直观
        """
        try:
            # 删除命令，获取参数
            command_content = self.raw_message.replace(
                PRIVATE_BLACKLIST_SCAN_COMMAND, ""
            ).strip()

            # 导入必要的模块
            from core.switchs import get_all_enabled_groups
            from api.group import get_group_member_list
            from core.get_group_member_list import (
                get_group_member_user_ids,
                get_group_name_by_id,
            )
            from .data_manager import BlackListDataManager
            from api.group import set_group_kick
            from api.message import send_group_msg
            from utils.generate import generate_text_message
            import asyncio

            if command_content:
                # 扫描指定群
                if command_content.isdigit():
                    target_groups = [command_content]
                    reply_message = f"开始扫描指定群 {command_content} 的黑名单用户..."
                else:
                    reply_message = "群号格式错误，请输入有效的群号"
                    await send_private_msg(
                        self.websocket,
                        self.target_id,
                        [
                            generate_reply_message(reply_message),
                            generate_text_message(reply_message),
                        ],
                    )
                    return False
            else:
                # 扫描所有开启黑名单功能的群
                target_groups = get_all_enabled_groups(MODULE_NAME)
                if not target_groups:
                    reply_message = "当前没有开启黑名单功能的群"
                    await send_private_msg(
                        self.websocket,
                        self.target_id,
                        [
                            generate_reply_message(reply_message),
                            generate_text_message(reply_message),
                        ],
                    )
                    return True
                reply_message = (
                    f"开始扫描所有开启黑名单功能的群（共{len(target_groups)}个群）..."
                )

            # 发送开始扫描的消息
            await send_private_msg(
                self.websocket,
                self.target_id,
                [
                    generate_reply_message(reply_message),
                    generate_text_message(reply_message),
                ],
            )

            # 扫描统计
            total_kicked = 0
            scan_results = []
            batch_results = []  # 用于存储批次处理结果

            for index, group_id in enumerate(target_groups, 1):
                try:
                    group_name = get_group_name_by_id(group_id) or f"群{group_id}"

                    # 先获取最新的群成员列表
                    await get_group_member_list(
                        self.websocket,
                        group_id,
                        True,  # 不使用缓存
                        note=f"{MODULE_NAME}-update-member-list-{group_id}",
                    )

                    # 等待一下让数据更新
                    await asyncio.sleep(0.5)

                    # 获取群成员QQ号列表
                    member_ids = get_group_member_user_ids(group_id)

                    if not member_ids:
                        scan_results.append(
                            f"{group_name}({group_id})：无法获取群成员列表"
                        )
                        batch_results.append(
                            f"{group_name}({group_id})：无法获取群成员列表"
                        )
                    else:
                        # 检查每个成员是否在黑名单中
                        blacklisted_members = []
                        with BlackListDataManager() as data_manager:
                            for member_id in member_ids:
                                if data_manager.is_user_blacklisted(
                                    group_id, member_id
                                ):
                                    blacklisted_members.append(member_id)

                        if not blacklisted_members:
                            batch_results.append(
                                f"{group_name}({group_id})：未发现黑名单用户"
                            )
                        else:
                            # 踢出黑名单用户
                            kicked_count = 0
                            kick_user_ids = []

                            for member_id in blacklisted_members:
                                try:
                                    # 踢出用户
                                    await set_group_kick(
                                        self.websocket, group_id, member_id
                                    )
                                    kicked_count += 1
                                    kick_user_ids.append(f"{member_id}")
                                except Exception as e:
                                    logger.error(
                                        f"[{MODULE_NAME}]踢出用户 {member_id} 失败: {e}"
                                    )

                            # 群内播报
                            if kicked_count > 0:
                                # 播报头消息
                                broadcast_message = [
                                    generate_text_message(
                                        f"🚫 扫黑完成：发现并踢出 {kicked_count} 个黑名单用户\n"
                                    )
                                ]

                                # 构建被踢成员汇总
                                for kick_user_id in kick_user_ids:
                                    broadcast_message += [
                                        generate_at_message(kick_user_id),
                                        (generate_text_message(f"({kick_user_id})\n")),
                                    ]

                                logger.debug(
                                    f"[{MODULE_NAME}]广播消息: {broadcast_message}"
                                )

                                await send_group_msg(
                                    self.websocket, group_id, broadcast_message
                                )

                            total_kicked += kicked_count
                            # 只有成功踢出黑名单用户的群才添加到扫描结果中
                            if kicked_count > 0:
                                scan_results.append(
                                    f"{group_name}({group_id})：踢出 {kicked_count} 个黑名单用户"
                                )
                                batch_results.append(
                                    f"{group_name}({group_id})：踢出 {kicked_count} 个黑名单用户"
                                )
                            else:
                                batch_results.append(
                                    f"{group_name}({group_id})：未发现黑名单用户"
                                )

                    # await asyncio.sleep(1)  # 群间间隔

                except Exception as e:
                    logger.error(f"[{MODULE_NAME}]扫描群 {group_id} 失败: {e}")
                    scan_results.append(f"{group_id}：扫描失败 - {str(e)}")
                    batch_results.append(f"{group_id}：扫描失败 - {str(e)}")

                # 每10个群或最后一个群时发送进度消息（将此逻辑移出异常处理块）
                if index % 10 == 0 or index == len(target_groups):
                    batch_start = max(1, index - 9)
                    progress_msg = (
                        f"🔍 扫黑进度 ({batch_start}-{index}/{len(target_groups)})\n\n"
                    )
                    progress_msg += "\n".join(batch_results)

                    await send_private_msg(
                        self.websocket,
                        self.target_id,
                        [generate_text_message(progress_msg)],
                    )
                    batch_results = []  # 清空批次结果

            # 发送最终扫描结果
            result_message = f"🔍 扫黑任务完成！\n\n"
            result_message += f"扫描群数：{len(target_groups)}\n"
            result_message += f"发现黑名单群数：{len(scan_results)}\n"
            result_message += f"总计踢出：{total_kicked} 人\n\n"

            if scan_results:
                result_message += "详细结果：\n" + "\n".join(scan_results)
            else:
                result_message += "🎉 所有扫描的群都很干净，未发现黑名单用户！"

            await send_private_msg(
                self.websocket,
                self.target_id,
                [
                    generate_reply_message(result_message),
                    generate_text_message(result_message),
                ],
            )

            return True

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]私聊扫黑失败: {e}")
            error_message = f"扫黑失败：{str(e)}"
            await send_private_msg(
                self.websocket,
                self.target_id,
                [
                    generate_reply_message(error_message),
                    generate_text_message(error_message),
                ],
            )
            return False

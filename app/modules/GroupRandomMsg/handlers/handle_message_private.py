from .. import MODULE_NAME, SWITCH_NAME, ADD_GROUP_RANDOM_MSG
from core.menu_manager import MENU_COMMAND
import logger
from core.switchs import is_private_switch_on, handle_module_private_switch
from api.message import send_private_msg
from utils.generate import generate_text_message, generate_reply_message
from datetime import datetime
from utils.auth import is_system_admin
from core.menu_manager import MenuManager
from .data_manager import DataManager


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

    async def _handle_add_message_by_group(self):
        """处理私聊按群号添加随机消息"""
        try:
            # 鉴权
            if not is_system_admin(self.user_id):
                logger.error(f"[{MODULE_NAME}]{self.user_id}无权限添加随机消息")
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("权限不足，仅系统管理员可使用此功能"),
                    ],
                )
                return

            # 解析命令格式：ADD_GROUP_RANDOM_MSG 群号 消息内容
            command_parts = self.raw_message.split(" ", 2)
            if len(command_parts) < 3:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("格式错误，正确格式：命令 群号 消息内容"),
                    ],
                )
                return

            group_id = command_parts[1].strip()
            message_content = command_parts[2].strip()

            # 验证群号格式
            if not group_id.isdigit():
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("群号格式错误，请输入纯数字"),
                    ],
                )
                return

            # 验证消息内容
            if not message_content:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("消息内容不能为空"),
                    ],
                )
                return

            # 实例化数据管理器
            data_manager = DataManager(group_id)

            # 添加数据
            new_id = data_manager.add_data(message_content, self.user_id)
            logger.info(
                f"[{MODULE_NAME}]私聊添加随机消息成功: 群{group_id} - {message_content}"
            )

            await send_private_msg(
                self.websocket,
                self.user_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(
                        f"添加随机消息成功\n群号：{group_id}\nID：{new_id}\n内容：{message_content}"
                    ),
                ],
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]私聊添加随机消息时发生异常: {e}")
            await send_private_msg(
                self.websocket,
                self.user_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message("添加失败，请稍后重试"),
                ],
            )

    async def _handle_batch_add_message_by_group(self):
        """处理私聊批量添加随机消息"""
        try:
            # 鉴权
            if not is_system_admin(self.user_id):
                logger.error(f"[{MODULE_NAME}]{self.user_id}无权限批量添加随机消息")
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("权限不足，仅系统管理员可使用此功能"),
                    ],
                )
                return

            # 解析命令格式：ADD_GROUP_RANDOM_MSG 群号\n消息1\n消息2\n...
            lines = self.raw_message.split("\n")
            if len(lines) < 2:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(
                            "格式错误，正确格式：命令 群号\\n消息1\\n消息2\\n..."
                        ),
                    ],
                )
                return

            # 解析第一行获取群号
            first_line_parts = lines[0].split(" ", 1)
            if len(first_line_parts) < 2:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("格式错误，第一行应为：命令 群号"),
                    ],
                )
                return

            group_id = first_line_parts[1].strip()

            # 验证群号格式
            if not group_id.isdigit():
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("群号格式错误，请输入纯数字"),
                    ],
                )
                return

            # 获取待添加的消息列表
            messages = [line.strip() for line in lines[1:] if line.strip()]
            if not messages:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("没有找到待添加的消息"),
                    ],
                )
                return

            # 实例化数据管理器
            data_manager = DataManager(group_id)

            # 批量添加消息
            added_ids = []
            for message_content in messages:
                try:
                    new_id = data_manager.add_data(message_content, self.user_id)
                    added_ids.append((new_id, message_content))
                    logger.info(
                        f"[{MODULE_NAME}]私聊批量添加随机消息: 群{group_id} - ID{new_id} - {message_content}"
                    )
                except Exception as e:
                    logger.error(
                        f"[{MODULE_NAME}]添加消息失败: {message_content} - {e}"
                    )

            # 发送结果
            if added_ids:
                result_text = f"批量添加随机消息成功\n群号：{group_id}\n成功添加 {len(added_ids)} 条消息：\n"
                for msg_id, content in added_ids:
                    result_text += f"ID{msg_id}: {content[:20]}{'...' if len(content) > 20 else ''}\n"

                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(result_text.strip()),
                    ],
                )
            else:
                await send_private_msg(
                    self.websocket,
                    self.user_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("批量添加失败，请检查消息格式"),
                    ],
                )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]私聊批量添加随机消息时发生异常: {e}")
            await send_private_msg(
                self.websocket,
                self.user_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message("批量添加失败，请稍后重试"),
                ],
            )

    async def _handle_switch_command(self):
        """
        处理开关命令
        """
        if self.raw_message.lower() == SWITCH_NAME.lower():
            # 鉴权
            if not is_system_admin(self.user_id):
                logger.error(f"[{MODULE_NAME}]{self.user_id}无权限切换私聊开关")
                return True
            await handle_module_private_switch(
                MODULE_NAME,
                self.websocket,
                self.user_id,
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
            await send_private_msg(
                self.websocket,
                self.user_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(menu_text),
                ],
            )
            return True
        return False

    async def handle(self):
        """
        处理私聊消息
        """
        try:
            # 处理开关命令
            if await self._handle_switch_command():
                return

            # 处理菜单命令（无视开关状态）
            if await self._handle_menu_command():
                return

            # 如果没开启私聊开关，则不处理
            if not is_private_switch_on(MODULE_NAME):
                return

            # 处理私聊添加随机消息命令
            if self.raw_message.startswith(ADD_GROUP_RANDOM_MSG):
                # 判断是单条添加还是批量添加
                if "\n" in self.raw_message:
                    await self._handle_batch_add_message_by_group()
                else:
                    await self._handle_add_message_by_group()
                return

            # 新增：根据sub_type判断消息类型
            if self.sub_type == "friend":
                # 处理好友私聊消息
                pass
            elif self.sub_type == "group":
                # 处理临时会话消息（如群临时会话）
                pass
            else:
                # 其他类型的私聊消息
                logger.info(
                    f"[{MODULE_NAME}]收到未知sub_type的私聊消息: {self.sub_type}"
                )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理私聊消息失败: {e}")

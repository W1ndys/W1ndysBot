from logger import logger
from .. import (
    MODULE_NAME,
    ADD_GROUP_RANDOM_MSG,
    DELETE_GROUP_RANDOM_MSG,
    SILENCE_MINUTES,
)
from utils.auth import is_system_admin, is_group_admin
from .data_manager import DataManager
from api.message import send_group_msg
from utils.generate import generate_text_message, generate_reply_message
from datetime import datetime


async def send_group_random_msg(websocket, group_id):
    """处理群随机消息相关命令"""
    try:
        # 检查当前时间是否在凌晨1点到6点之间
        current_hour = datetime.now().hour
        if 1 <= current_hour <= 6:
            return  # 凌晨1点到6点不发送消息

        # 检查群活跃度，只有在静默时间后才发送
        data_manager = DataManager(group_id)
        if not data_manager.should_send_random_message(SILENCE_MINUTES):
            logger.info(f"[{MODULE_NAME}]{group_id}群聊活跃，跳过随机消息发送")
            return

        # 获取随机消息
        random_msg = data_manager.get_random_data()
        if random_msg:
            # random_msg 格式: (id, message, random_count, added_by, add_time)
            message_id = random_msg[0]
            message_content = random_msg[1]

            # 把转义后的换行符还原
            message_content = message_content.replace("\\n", "\n")

            # 格式化消息
            formatted_message = f"{message_content}（ID：{message_id}）"

            await send_group_msg(
                websocket, group_id, [generate_text_message(formatted_message)]
            )
            logger.info(f"[{MODULE_NAME}]{group_id}发送随机消息成功: {message_content}")
            # 更新群最近一次发言时间
            data_manager.update_last_message_time()
        else:
            logger.error(f"[{MODULE_NAME}]{group_id}获取随机消息失败")
    except Exception as e:
        logger.error(f"[{MODULE_NAME}]{group_id}处理群随机消息时发生异常: {e}")


class GroupRandomMsg:
    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.user_id = str(msg.get("user_id", ""))
        self.group_id = str(msg.get("group_id", ""))
        self.message_id = str(msg.get("message_id", ""))
        self.message = msg.get("message", {})
        self.raw_message = msg.get("raw_message", "")
        self.sender = msg.get("sender", {})
        self.role = self.sender.get("role", "")

    async def _handle_add_message(self):
        """处理添加随机消息"""
        try:
            # 鉴权
            if not is_system_admin(self.user_id) and not is_group_admin(self.role):
                logger.error(f"[{MODULE_NAME}]{self.user_id}无权限添加随机消息")
                return

            # 分离出待添加消息
            message_content = self.raw_message.split(ADD_GROUP_RANDOM_MSG)[1].strip()
            # 验证消息内容
            if not message_content:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("消息内容不能为空"),
                    ],
                )
                return

            # 实例化数据管理器
            data_manager = DataManager(self.group_id)

            # 添加数据
            new_id = data_manager.add_data(message_content, self.user_id)
            logger.info(f"[{MODULE_NAME}]添加随机消息成功: {message_content}")

            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(f"添加随机消息成功，ID：{new_id}"),
                ],
                note="del_msg=10",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]添加随机消息时发生异常: {e}")

    async def _handle_batch_add_message(self):
        """处理群聊批量添加随机消息"""
        try:
            # 鉴权
            if not is_system_admin(self.user_id) and not is_group_admin(self.role):
                logger.error(f"[{MODULE_NAME}]{self.user_id}无权限批量添加随机消息")
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("权限不足，需要管理员权限"),
                    ],
                )
                return

            # 解析批量消息内容
            content_after_command = self.raw_message.split(ADD_GROUP_RANDOM_MSG)[
                1
            ].strip()

            # 按换行分割消息
            messages = [
                line.strip()
                for line in content_after_command.split("\n")
                if line.strip()
            ]

            if not messages:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("没有找到待添加的消息"),
                    ],
                )
                return

            # 实例化数据管理器
            data_manager = DataManager(self.group_id)

            # 批量添加消息
            added_ids = []
            for message_content in messages:
                try:
                    new_id = data_manager.add_data(message_content, self.user_id)
                    added_ids.append((new_id, message_content))
                    logger.info(
                        f"[{MODULE_NAME}]群聊批量添加随机消息: ID{new_id} - {message_content}"
                    )
                except Exception as e:
                    logger.error(
                        f"[{MODULE_NAME}]添加消息失败: {message_content} - {e}"
                    )

            # 发送结果
            if added_ids:
                result_text = (
                    f"批量添加随机消息成功\n成功添加 {len(added_ids)} 条消息：\n"
                )
                for msg_id, content in added_ids[:5]:  # 只显示前5条
                    result_text += f"ID{msg_id}: {content[:15]}{'...' if len(content) > 15 else ''}\n"

                if len(added_ids) > 5:
                    result_text += f"... 还有 {len(added_ids) - 5} 条消息"

                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(result_text.strip()),
                    ],
                    note="del_msg=15",
                )
            else:
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message("批量添加失败，请检查消息格式"),
                    ],
                )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]群聊批量添加随机消息时发生异常: {e}")

    async def _handle_delete_message(self):
        """处理删除随机消息"""
        try:
            # 鉴权
            if not is_system_admin(self.user_id) and not is_group_admin(self.role):
                logger.error(f"[{MODULE_NAME}]{self.user_id}无权限删除随机消息")
                return

            # 分离出待删除消息ID
            delete_message_id = int(
                self.raw_message.split(DELETE_GROUP_RANDOM_MSG)[1].strip()
            )

            # 实例化数据管理器
            data_manager = DataManager(self.group_id)

            # 检查消息是否存在
            if not data_manager.data_exists(delete_message_id):
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(f"消息ID {delete_message_id} 不存在"),
                    ],
                )
                return

            # 删除数据
            data_manager.delete_data_by_id(delete_message_id)
            logger.info(f"[{MODULE_NAME}]删除随机消息成功: {delete_message_id}")

            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(f"删除随机消息成功，ID：{delete_message_id}"),
                ],
                note="del_msg=10",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]删除随机消息时发生异常: {e}")

    async def handle_group_random_msg(self):
        """处理群随机消息相关命令"""
        try:
            if self.raw_message.startswith(ADD_GROUP_RANDOM_MSG):
                # 判断是单条添加还是批量添加
                content_after_command = self.raw_message.split(ADD_GROUP_RANDOM_MSG)[
                    1
                ].strip()
                if "\n" in content_after_command:
                    await self._handle_batch_add_message()
                else:
                    await self._handle_add_message()
            elif self.raw_message.startswith(DELETE_GROUP_RANDOM_MSG):
                await self._handle_delete_message()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

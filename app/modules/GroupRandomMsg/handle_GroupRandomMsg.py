from logger import logger
from . import MODULE_NAME, ADD_GROUP_RANDOM_MSG, DELETE_GROUP_RANDOM_MSG
from core.auth import is_system_admin, is_group_admin
from .data_manager import DataManager
from api.message import send_group_msg
from api.generate import generate_text_message, generate_reply_message
from datetime import datetime


async def send_group_random_msg(websocket, group_id):
    """处理群随机消息相关命令"""
    try:
        # 检查当前分钟是否是30的倍数
        if datetime.now().minute % 30 == 0:
            # 获取随机消息
            random_msg = DataManager(group_id).get_random_data()
            if random_msg:
                # random_msg 格式: (id, message, random_count, added_by, add_time)
                message_id = random_msg[0]
                message_content = random_msg[1]
                added_by = random_msg[3]

                # 格式化消息
                formatted_message = f"✨ {message_content}\n本条消息由 {added_by} 添加\nID：{message_id}"

                await send_group_msg(
                    websocket, group_id, [generate_text_message(formatted_message)]
                )
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
                await self._handle_add_message()
            elif self.raw_message.startswith(DELETE_GROUP_RANDOM_MSG):
                await self._handle_delete_message()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

import asyncio
from logger import logger
from .. import (
    MODULE_NAME,
    ASSOCIATE_GROUPS_COMMAND,
    REMOVE_GROUPS_COMMAND,
    ADD_GROUPS_COMMAND,
    SEND_MESSAGE_COMMAND,
)
from .data_manager import DataManager
from api.message import send_private_msg, send_group_msg_with_cq
from core.get_group_member_list import get_group_member_user_ids


def get_user_groups_in_associated_groups(user_id: str, group_id: str):
    """
    获取用户在同组其他群中的群号和组名
    """
    user_group_ids = []
    group_name = ""
    with DataManager() as dm:
        result = dm.get_associated_groups(group_id)
        if result:
            for group_name in result:
                for other_group_id in result[group_name]:
                    member_list = get_group_member_user_ids(other_group_id)
                    if user_id in member_list:
                        user_group_ids.append(other_group_id)
    return user_group_ids, group_name


class Core:
    def __init__(self, websocket, user_id: str, raw_message: str):
        self.user_id = user_id
        self.raw_message = raw_message
        self.websocket = websocket

    async def _handle_associate_groups_command(self):
        try:
            # 解析命令
            command = self.raw_message.split()[0]
            if command == ASSOCIATE_GROUPS_COMMAND:
                # 解析参数
                params = self.raw_message.split()[1:]
                # 处理参数
                group_name = params[0]
                group_ids = params[1:]
                # 处理参数
                with DataManager() as dm:
                    result, message = dm.create_group_association(group_name, group_ids)
                    if result:
                        await send_private_msg(self.websocket, self.user_id, message)
                    else:
                        await send_private_msg(self.websocket, self.user_id, message)
                    return True
        except Exception as e:
            logger.error(
                f"[{MODULE_NAME}]{self.user_id}处理关联群号命令时发生异常: {e}"
            )
            await send_private_msg(
                self.websocket, self.user_id, "处理关联群号命令时发生异常: " + str(e)
            )
            return False

    async def _handle_remove_groups_command(self):
        try:
            # 解析命令
            command = self.raw_message.split()[0]
            if command == REMOVE_GROUPS_COMMAND:
                # 解析参数
                params = self.raw_message.split()[1:]
                # 处理参数
                group_name = params[0]
                group_ids = params[1:]
                # 处理参数
                with DataManager() as dm:
                    result, message = dm.remove_groups_from_association(
                        group_name, group_ids
                    )
                    if result:
                        await send_private_msg(self.websocket, self.user_id, message)
                    else:
                        await send_private_msg(self.websocket, self.user_id, message)
                    return True
        except Exception as e:
            logger.error(
                f"[{MODULE_NAME}]{self.user_id}处理删除群号命令时发生异常: {e}"
            )
            await send_private_msg(
                self.websocket, self.user_id, "处理删除群号命令时发生异常: " + str(e)
            )
            return False

    async def _handle_add_groups_command(self):
        try:
            # 解析命令
            command = self.raw_message.split()[0]
            if command == ADD_GROUPS_COMMAND:
                # 解析参数
                params = self.raw_message.split()[1:]
                # 处理参数
                group_name = params[0]
                group_ids = params[1:]
                # 处理参数
                with DataManager() as dm:
                    result, message = dm.add_groups_to_association(
                        group_name, group_ids
                    )
                    if result:
                        await send_private_msg(self.websocket, self.user_id, message)
                    else:
                        await send_private_msg(self.websocket, self.user_id, message)
                    return True
        except Exception as e:
            logger.error(
                f"[{MODULE_NAME}]{self.user_id}处理添加群号命令时发生异常: {e}"
            )
            await send_private_msg(
                self.websocket, self.user_id, "处理添加群号命令时发生异常: " + str(e)
            )
            return False

    async def _handle_send_message_command(self):
        try:
            # 解析命令
            params = self.raw_message.split()

            # 处理参数
            group_name = params[1]
            message = params[2]

            logger.success(
                f"[{MODULE_NAME}]{self.user_id}处理群发命令: {group_name} {message}"
            )

            # 处理参数
            with DataManager() as dm:
                group_ids = dm.get_group_info(group_name)
                if group_ids:
                    for group_id in group_ids:
                        await send_group_msg_with_cq(self.websocket, group_id, message)
                        await asyncio.sleep(0.5)
                else:
                    await send_private_msg(self.websocket, self.user_id, message)
                return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]{self.user_id}处理群发命令时发生异常: {e}")
            await send_private_msg(
                self.websocket, self.user_id, "处理群发命令时发生异常: " + str(e)
            )
            return False

    async def handle(self):
        try:
            if self.raw_message.startswith(ASSOCIATE_GROUPS_COMMAND):
                await self._handle_associate_groups_command()
            elif self.raw_message.startswith(REMOVE_GROUPS_COMMAND):
                await self._handle_remove_groups_command()
            elif self.raw_message.startswith(ADD_GROUPS_COMMAND):
                await self._handle_add_groups_command()
            elif self.raw_message.startswith(SEND_MESSAGE_COMMAND):
                await self._handle_send_message_command()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]{self.user_id}处理私聊消息失败: {e}")
            await send_private_msg(
                self.websocket,
                self.user_id,
                f"[{MODULE_NAME}]处理私聊消息失败: {e}",
            )

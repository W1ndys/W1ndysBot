import asyncio
from logger import logger
from .. import (
    MODULE_NAME,
    ASSOCIATE_GROUPS_COMMAND,
    REMOVE_GROUPS_COMMAND,
    ADD_GROUPS_COMMAND,
    SEND_MESSAGE_COMMAND,
    VIEW_GROUPS_COMMAND,
    VIEW_GROUPS_LIST_COMMAND,
    DELETE_GROUP_COMMAND,
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
            # 解析命令 - 限制分割次数，保留消息中的空格
            parts = self.raw_message.split(" ", 2)  # 最多分割2次，得到3个部分

            if len(parts) < 3:
                await send_private_msg(
                    self.websocket, self.user_id, "命令格式错误，请提供群组名和消息内容"
                )
                return False

            # 处理参数
            group_name = parts[1]
            message = parts[2]  # 第二个空格后的所有内容，保持原样

            logger.info(
                f"[{MODULE_NAME}]{self.user_id}处理群发命令: {group_name} {message}"
            )

            # 把消息中的“atall”转换为CQ码格式的全体成员
            message = message.replace("atall", "[CQ:at,qq=all]")

            note = ""
            # 检测消息中是否有“settodo”
            if "settodo" in message:
                # 定义note变量以便发消息接口使用
                note = "settodo"
                # 去除消息里的settodo
                message = message.replace("settodo", "").strip()

            # 处理参数
            with DataManager() as dm:
                group_ids = dm.get_group_info(group_name)
                if group_ids:
                    for group_id in group_ids:
                        await send_group_msg_with_cq(
                            self.websocket,
                            group_id,
                            message,
                            note=f"{note}-group_id={group_id}",
                        )
                    await send_private_msg(
                        self.websocket,
                        self.user_id,
                        f"群发成功, 已发送到下列群号：{', '.join(group_ids)}",
                    )
                else:
                    await send_private_msg(
                        self.websocket, self.user_id, "未找到指定的群组"
                    )
                return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]{self.user_id}处理群发命令时发生异常: {e}")
            await send_private_msg(
                self.websocket, self.user_id, "处理群发命令时发生异常: " + str(e)
            )
            return False

    async def _handle_view_groups_command(self):
        """处理查看指定群组下所有群号的命令"""
        try:
            # 解析命令
            parts = self.raw_message.split()
            if len(parts) < 2:
                await send_private_msg(
                    self.websocket, self.user_id, "命令格式错误，请提供群组名"
                )
                return False

            group_name = parts[1]

            with DataManager() as dm:
                group_ids = dm.get_groups_in_association(group_name)
                if group_ids:
                    message = f"群组 '{group_name}' 包含以下群号：\n"
                    message += "\n".join([f"- {group_id}" for group_id in group_ids])
                    message += f"\n\n共 {len(group_ids)} 个群"
                else:
                    message = f"群组 '{group_name}' 不存在或为空"

                await send_private_msg(self.websocket, self.user_id, message)
                return True

        except Exception as e:
            logger.error(
                f"[{MODULE_NAME}]{self.user_id}处理查看群组命令时发生异常: {e}"
            )
            await send_private_msg(
                self.websocket, self.user_id, "处理查看群组命令时发生异常: " + str(e)
            )
            return False

    async def _handle_view_groups_list_command(self):
        """处理查看所有群组名字的命令"""
        try:
            with DataManager() as dm:
                group_names = dm.get_all_group_names()
                if group_names:
                    message = "所有群组名字：\n"
                    message += "\n".join([f"- {name}" for name in group_names])
                    message += f"\n\n共 {len(group_names)} 个群组"
                else:
                    message = "暂无任何群组"

                await send_private_msg(self.websocket, self.user_id, message)
                return True

        except Exception as e:
            logger.error(
                f"[{MODULE_NAME}]{self.user_id}处理查看群组列表命令时发生异常: {e}"
            )
            await send_private_msg(
                self.websocket,
                self.user_id,
                "处理查看群组列表命令时发生异常: " + str(e),
            )
            return False

    async def _handle_delete_group_command(self):
        """处理删除群组命令"""
        try:
            # 解析命令
            parts = self.raw_message.split()
            if len(parts) < 2:
                await send_private_msg(
                    self.websocket, self.user_id, "命令格式错误，请提供群组名"
                )
                return False

            group_name = parts[1]

            with DataManager() as dm:
                result, message = dm.delete_group_association(group_name)
                await send_private_msg(self.websocket, self.user_id, message)
                return True

        except Exception as e:
            logger.error(
                f"[{MODULE_NAME}]{self.user_id}处理删除群组命令时发生异常: {e}"
            )
            await send_private_msg(
                self.websocket, self.user_id, "处理删除群组命令时发生异常: " + str(e)
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
            elif self.raw_message.startswith(VIEW_GROUPS_COMMAND):
                await self._handle_view_groups_command()
            elif self.raw_message.startswith(VIEW_GROUPS_LIST_COMMAND):
                await self._handle_view_groups_list_command()
            elif self.raw_message.startswith(DELETE_GROUP_COMMAND):
                await self._handle_delete_group_command()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]{self.user_id}处理私聊消息失败: {e}")
            await send_private_msg(
                self.websocket,
                self.user_id,
                f"[{MODULE_NAME}]处理私聊消息失败: {e}",
            )

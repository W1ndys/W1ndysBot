from .. import MODULE_NAME, BLACKLIST_SCAN_COMMAND, PRIVATE_BLACKLIST_ADD_COMMAND
from .data_manager import BlackListDataManager
from api.group import set_group_kick_members
from api.message import send_group_msg, send_private_msg
from config import OWNER_ID
from utils.generate import generate_text_message
import logger
import re


class ResponseHandler:
    """响应处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.echo = msg.get("echo", {})

    async def handle(self):
        try:
            # 检查是否是扫黑命令的群成员列表响应
            if (
                self.echo.startswith("get_group_member_list-")
                and MODULE_NAME in self.echo
                and BLACKLIST_SCAN_COMMAND in self.echo
            ):
                await self.handle_scan_blacklist_response()
            elif self.echo.startswith("get_msg-") and MODULE_NAME in self.echo:
                await self.handle_get_msg_response()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理响应失败: {e}")

    async def handle_get_msg_response(self):
        """
        处理获取消息响应
        """
        try:
            # 正则匹配action
            pattern = r"action=(.*)"
            match = re.search(pattern, self.echo)
            if not match:
                logger.error(f"[{MODULE_NAME}]从echo中提取action失败: {self.echo}")
                return
            action = match.group(1)
            if action == PRIVATE_BLACKLIST_ADD_COMMAND:
                await self.handle_private_blacklist_add_response()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理获取消息响应失败: {e}")

    async def handle_private_blacklist_add_response(self):
        """
        处理私聊拉黑响应
        """
        try:
            raw_message = self.data.get("raw_message", "")
            # 在原始消息里提取user_id
            pattern = r"user_id=(\d+)"
            matches = re.findall(pattern, raw_message)
            if not matches:
                logger.error(
                    f"[{MODULE_NAME}]从原始消息里提取user_id失败: {raw_message}"
                )
                return False
            for user_id in matches:
                logger.info(f"[{MODULE_NAME}]提取到user_id: {user_id}")
                # 添加全局黑名单
                with BlackListDataManager() as data_manager:
                    data_manager.add_global_blacklist(user_id)
                await send_private_msg(
                    self.websocket,
                    OWNER_ID,
                    [
                        generate_text_message(
                            f"[{MODULE_NAME}]已将用户{', '.join(matches)}拉入全局黑名单"
                        )
                    ],
                )
            return True
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理私聊拉黑响应失败: {e}")

    async def handle_scan_blacklist_response(self):
        """
        处理扫黑命令的群成员列表响应
        """
        try:
            # 从echo中提取群号
            pattern = r"group_id=(\d+)"
            match = re.search(pattern, self.echo)
            if not match:
                logger.error(f"[{MODULE_NAME}]从echo中提取群号失败: {self.echo}")
                return

            group_id = match.group(1)
            member_list = self.data

            if not member_list:
                await send_group_msg(
                    self.websocket,
                    group_id,
                    [generate_text_message("获取群成员列表失败")],
                    note="del_msg=10",
                )
                return

            logger.info(
                f"[{MODULE_NAME}]开始扫描群 {group_id} 的 {len(member_list)} 个成员"
            )

            # 检查群成员是否在黑名单中
            blacklisted_users = []
            with BlackListDataManager() as data_manager:
                for member in member_list:
                    user_id = str(member.get("user_id", ""))
                    role = member.get("role", "")

                    # 跳过管理员和群主
                    if role in ["admin", "owner"]:
                        continue

                    if user_id and data_manager.is_user_blacklisted(group_id, user_id):
                        # 优先判断是否在群黑名单中，如果在群黑名单中则显示为群黑名单
                        if data_manager.is_in_blacklist(group_id, user_id):
                            blacklist_type = "群黑名单"
                        else:
                            # 如果不在群黑名单中但在全局黑名单中，则显示为全局黑名单
                            blacklist_type = "全局黑名单"

                        nickname = member.get("nickname", "")
                        card = member.get("card", "")
                        display_name = card if card else nickname
                        blacklisted_users.append(
                            {
                                "user_id": user_id,
                                "type": blacklist_type,
                                "display_name": display_name,
                            }
                        )

            if not blacklisted_users:
                await send_group_msg(
                    self.websocket,
                    group_id,
                    [generate_text_message("扫描完成，未发现黑名单用户")],
                    note="del_msg=10",
                )
                return

            # 分别统计全局黑名单和群黑名单用户
            global_blacklisted = [
                user for user in blacklisted_users if user["type"] == "全局黑名单"
            ]
            group_blacklisted = [
                user for user in blacklisted_users if user["type"] == "群黑名单"
            ]

            # 构建踢出用户列表（所有黑名单用户的ID）
            users_to_kick = [user["user_id"] for user in blacklisted_users]

            # 发送发现黑名单用户的消息
            result_parts = []
            if global_blacklisted:
                global_names = [
                    f"{user['user_id']}({user['display_name']})"
                    for user in global_blacklisted
                ]
                result_parts.append(f"全局黑名单用户: {', '.join(global_names)}")
            if group_blacklisted:
                group_names = [
                    f"{user['user_id']}({user['display_name']})"
                    for user in group_blacklisted
                ]
                result_parts.append(f"群黑名单用户: {', '.join(group_names)}")

            discovery_message = (
                f"发现 {len(blacklisted_users)} 个黑名单用户:\n"
                + "\n".join(result_parts)
                + "\n正在踢出..."
            )

            await send_group_msg(
                self.websocket,
                group_id,
                [generate_text_message(discovery_message)],
                note="del_msg=10",
            )

            # 批量踢出黑名单用户
            await set_group_kick_members(
                self.websocket,
                group_id,
                users_to_kick,
                True,
            )

            # 发送完成消息
            completion_message = f"扫黑完成！已踢出 {len(blacklisted_users)} 个黑名单用户并拒绝其后续加群请求"
            await send_group_msg(
                self.websocket,
                group_id,
                [generate_text_message(completion_message)],
                note="del_msg=30",
            )

            logger.info(
                f"[{MODULE_NAME}]群 {group_id} 扫黑完成，已踢出 {len(blacklisted_users)} 个用户"
            )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理扫黑响应失败: {e}")

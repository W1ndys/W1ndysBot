import time
from .. import MODULE_NAME, SCAN_INACTIVE_USER_COMMAND
import logger
from utils.generate import generate_text_message, generate_at_message
from api.message import send_group_msg
import re

# 临时缓存：用于存储通过echo标识获取到的群历史消息
# key: 完整的echo字符串（如 get_group_msg_history-{group_id}-{note}）
# value: messages 列表
TEMP_GROUP_HISTORY_CACHE = {}

# 临时缓存：用于存储通过echo标识获取到的群成员列表（用于批量撤回时过滤管理员/群主）
# key: 完整的echo字符串（如 get_group_member_list-group_id={group_id}-{note}）
# value: 群成员列表数据
TEMP_GROUP_MEMBERS_CACHE = {}


class ResponseHandler:
    """响应处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.echo = msg.get("echo", {})

    async def handle_get_group_member_list(self):
        """
        处理获取群成员列表的响应
        """
        try:
            # 是否是扫描未活跃用户的响应
            if SCAN_INACTIVE_USER_COMMAND in self.echo:
                days = 30  # 默认30天
                group_id = None

                # 使用正则表达式提取days和group_id参数
                days_match = re.search(r"days=(\d+)", self.echo)
                group_id_match = re.search(r"group_id=(\d+)", self.echo)
                if days_match:
                    days = int(days_match.group(1))
                if group_id_match:
                    group_id = int(group_id_match.group(1))

                # 计算时间阈值（当前时间戳 - 指定天数的秒数）
                current_time = int(time.time())
                threshold_time = current_time - (days * 24 * 60 * 60)

                # 存储未活跃用户的QQ号
                inactive_users = []

                # 群号
                group_id = ""

                # 遍历群成员列表，检查最后发言时间戳
                for member in self.data:
                    group_id = member.get("group_id")
                    user_id = member.get("user_id")
                    last_sent_time = member.get("last_sent_time", 0)
                    nickname = member.get("nickname", "")
                    card = member.get("card", "")

                    # 如果最后发言时间小于阈值时间，说明超过了指定天数未发言
                    if last_sent_time < threshold_time:
                        inactive_users.append(
                            {
                                "user_id": user_id,
                                "nickname": nickname,
                                "card": card,
                                "last_sent_time": last_sent_time,
                                "days_inactive": (
                                    (current_time - last_sent_time) // (24 * 60 * 60)
                                    if last_sent_time > 0
                                    else "从未发言"
                                ),
                            }
                        )

                message = []
                # 构建艾特消息
                for user in inactive_users:
                    message.append(generate_at_message(user["user_id"]))

                message.append(
                    generate_text_message(
                        f"\n\n\n以上用户{days}天未发言，请保持活跃，长时间未发言可能会被自动移出群聊，请及时冒泡"
                    )
                )

                # 发送消息
                await send_group_msg(self.websocket, group_id, message)

            # 缓存用于撤回的群成员列表（用于识别admin/owner）
            elif (
                isinstance(self.echo, str)
                and self.echo.startswith("get_group_member_list-")
                and f"{MODULE_NAME}-recall" in self.echo
            ):
                TEMP_GROUP_MEMBERS_CACHE[self.echo] = self.data
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]获取群成员列表失败: {e}")

    async def handle_get_group_msg_history_for_recall(self):
        """
        处理获取群历史消息（用于批量撤回）的响应，将数据写入临时缓存
        """
        try:
            # 仅缓存本模块发起且带有recall标记的请求
            if (
                isinstance(self.echo, str)
                and self.echo.startswith("get_group_msg_history-")
                and f"{MODULE_NAME}-recall" in self.echo
            ):
                messages = self.data.get("messages", [])
                TEMP_GROUP_HISTORY_CACHE[self.echo] = messages
                logger.info(
                    f"[{MODULE_NAME}]已缓存群历史消息用于撤回，echo={self.echo}，条数={len(messages)}"
                )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群历史消息响应失败: {e}")

    async def handle(self):
        try:
            if isinstance(self.echo, str) and self.echo.startswith("get_group_member_list"):
                await self.handle_get_group_member_list()
            elif (
                isinstance(self.echo, str)
                and self.echo.startswith("get_group_msg_history-")
                and f"{MODULE_NAME}-recall" in self.echo
            ):
                await self.handle_get_group_msg_history_for_recall()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理响应失败: {e}")

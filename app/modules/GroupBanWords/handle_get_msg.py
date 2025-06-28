from . import MODULE_NAME, UNBAN_WORD_COMMAND, KICK_BAN_WORD_COMMAND
import logger
import re
from api.group import set_group_ban, set_group_kick
from api.message import send_group_msg, send_private_msg
from utils.generate import generate_text_message, generate_at_message
from config import OWNER_ID


class GetMsgHandler:
    """获取消息内容处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.echo = msg.get("echo", "")
        self.raw_message = self.data.get("raw_message", "")

    async def handle_get_msg(self):
        try:
            # 正则提取群号和用户ID，raw_message中有格式为"群1049225772用户1414100329发送违禁词"的消息
            pattern = r"群(\d+)用户(\d+)发送违禁词"
            match_group_id_and_user_id = re.search(pattern, self.raw_message)
            # 正则提取命令里的action，按-分割，遍历，找到action=后面的值
            action = None
            for part in self.echo.split("-"):
                part = part.strip()
                if part.startswith("action="):
                    action = part.replace("action=", "", 1)  # 只替换第一个匹配项
                    break

            if match_group_id_and_user_id and action:
                group_id = match_group_id_and_user_id.group(1)
                user_id = match_group_id_and_user_id.group(2)
                # 解禁
                if action == UNBAN_WORD_COMMAND:
                    logger.info(f"[{MODULE_NAME}]解禁用户{user_id}，群号{group_id}")
                    await set_group_ban(self.websocket, group_id, user_id, 0)
                    # 群内通知
                    await send_group_msg(
                        self.websocket,
                        group_id,
                        [
                            generate_at_message(user_id),
                            generate_text_message(f"({user_id})你已被系统管理员解禁"),
                        ],
                    )
                    # 私聊管理员通知
                    await send_private_msg(
                        self.websocket,
                        OWNER_ID,
                        [
                            generate_text_message(
                                f"已将用户{user_id}解禁，群号{group_id}"
                            )
                        ],
                    )
                # 踢出
                elif action == KICK_BAN_WORD_COMMAND:
                    logger.info(f"[{MODULE_NAME}]踢出用户{user_id}，群号{group_id}")
                    # 群内通知
                    await send_group_msg(
                        self.websocket,
                        group_id,
                        [
                            generate_at_message(user_id),
                            generate_text_message(
                                f"({user_id})你因发送违禁词，即将被管理员踢出"
                            ),
                        ],
                    )
                    await set_group_kick(self.websocket, group_id, user_id, False)
                    # 私聊管理员通知
                    await send_private_msg(
                        self.websocket,
                        OWNER_ID,
                        [
                            generate_text_message(
                                f"已将用户{user_id}踢出群{group_id}，理由：发送违禁词"
                            )
                        ],
                    )

            else:
                logger.error(
                    f"[{MODULE_NAME}]处理获取消息内容失败: 未找到群号和用户ID，action:{action}"
                )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理获取消息内容失败: {e}")

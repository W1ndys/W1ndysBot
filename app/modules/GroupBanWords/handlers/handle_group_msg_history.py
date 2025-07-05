from api.message import delete_msg
from logger import logger
from .. import MODULE_NAME


class GetGroupMsgHistoryHandler:
    """获取群历史消息处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.echo = msg.get("echo", "")
        self.messages = self.data.get("messages", [])
        # 分离违规的群号和QQ号，格式：get_group_msg_history-GroupBanWords-group_id={group_id}-is_banned_user_id={user_id}
        self.group_id = None
        self.is_banned_user_id = None

    async def handle_get_group_msg_history(self):
        # 分离违规的群号和QQ号
        for part in self.echo.split("-"):
            if "group_id=" in part:
                self.group_id = part.split("=")[1]
                logger.info(f"[{MODULE_NAME}]获取到违规的群号: {self.group_id}")
            elif "is_banned_user_id=" in part:
                self.is_banned_user_id = part.split("=")[1]
                logger.info(
                    f"[{MODULE_NAME}]获取到被封禁的QQ号: {self.is_banned_user_id}"
                )

        # 遍历messages，撤回所有被封禁的QQ号发送的消息
        for message in self.messages:
            if str(message.get("sender", {}).get("user_id")) == str(
                self.is_banned_user_id
            ):
                await delete_msg(self.websocket, message.get("message_id"))
        logger.info(
            f"[{MODULE_NAME}]撤回群({self.group_id})中被封禁的QQ号({self.is_banned_user_id})发送的历史消息"
        )

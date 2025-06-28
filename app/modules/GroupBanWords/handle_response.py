from . import MODULE_NAME, UNBAN_WORD_COMMAND, KICK_BAN_WORD_COMMAND
from .handle_forward_message import ForwardMessageHandler
from .handle_group_msg_history import GetGroupMsgHistoryHandler
from .handle_get_msg import GetMsgHandler
import logger


class ResponseHandler:
    """响应处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.echo = msg.get("echo", "")

    async def handle(self):
        try:
            # 检查是否是该模块请求解析的转发消息
            if self.echo.startswith("get_forward_msg-") and MODULE_NAME in self.echo:
                logger.info(f"[{MODULE_NAME}]收到转发消息解析请求")
                # 实例化ForwardMessageHandler
                forward_message_handler = ForwardMessageHandler(
                    self.websocket, self.msg
                )
                # 处理转发消息
                await forward_message_handler.handle_forward_message()

            # 检查是否是该模块请求解析的群历史消息
            elif (
                self.echo.startswith("get_group_msg_history-")
                and MODULE_NAME in self.echo
            ):
                logger.info(f"[{MODULE_NAME}]收到获取群历史消息请求")
                # 实例化GetGroupMsgHistoryHandler
                get_group_msg_history_handler = GetGroupMsgHistoryHandler(
                    self.websocket, self.msg
                )
                # 处理获取的群历史消息
                await get_group_msg_history_handler.handle_get_group_msg_history()

            # 检查是否是该模块请求解析的获取消息内容
            elif (
                self.echo.startswith("get_msg-")
                and MODULE_NAME in self.echo
                and (
                    UNBAN_WORD_COMMAND in self.echo
                    or KICK_BAN_WORD_COMMAND in self.echo
                )
            ):
                logger.info(
                    f"[{MODULE_NAME}]收到{'解禁' if UNBAN_WORD_COMMAND in self.echo else '踢出'}消息内容请求"
                )
                # 实例化GetMsgHandler
                get_msg_handler = GetMsgHandler(self.websocket, self.msg)
                # 处理获取的消息内容
                await get_msg_handler.handle_get_msg()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理响应失败: {e}")

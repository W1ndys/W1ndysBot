from .. import MODULE_NAME
from logger import logger
from .db_manager import FAQDatabaseManager
from api.message import send_group_msg
from utils.generate import generate_reply_message, generate_text_message


class ResponseHandler:
    """响应处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.data = msg.get("data", {})
        self.echo = msg.get("echo", {})

    async def handle(self):
        try:
            if self.echo.startswith("get_msg-"):
                await self.handle_get_msg()
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理响应失败: {e}")

    async def handle_get_msg(self):
        """
        处理获取消息详情响应
        """
        try:
            question = ""
            group_id = ""
            reply_message_id = ""
            if MODULE_NAME in self.echo:
                note = self.echo.split("-")
                for item in note:
                    if "question=" in item:
                        question = item.split("=")[1]
                    if "group_id=" in item:
                        group_id = item.split("=")[1]
                    if "reply_message_id=" in item:
                        reply_message_id = item.split("=")[1]

            if question and group_id and reply_message_id:
                answer = self.data.get("raw_message")
                if answer:
                    with FAQDatabaseManager(group_id) as db:
                        result_id = db.add_FAQ_pair(question, answer)
                    await send_group_msg(
                        self.websocket,
                        group_id,
                        [
                            generate_reply_message(reply_message_id),
                            generate_text_message("✅ 更新成功\n"),
                            generate_text_message(
                                "━━━━━━━━━━━━━━\n"
                                f"🌟 问题：{question}\n"
                                f"💡 {answer}\n"
                                f"🆔 问答对ID：{str(result_id)}\n"
                                "━━━━━━━━━━━━━━\n"
                            ),
                            generate_text_message("⏳ 消息将在10秒后撤回，请及时保存"),
                        ],
                        note="del_msg=10",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理获取消息详情响应失败: {e}")

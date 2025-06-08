from .data_manager import DataManager
import logger
from . import (
    MODULE_NAME,
    ADD_COMMAND,
    DELETE_COMMAND,
)
from api.message import send_group_msg_with_cq, send_group_msg
from api.generate import generate_reply_message, generate_text_message
from datetime import datetime


class HandleKeywordsReply:
    """
    关键词回复处理类

    该类用于处理群聊中的关键词回复相关命令，包括添加、删除、查看和清空关键词回复。
    每个方法对应一个具体的命令处理逻辑，需结合消息内容和数据库操作实现具体功能。
    """

    def __init__(self, websocket, msg):
        """
        初始化方法

        :param websocket: WebSocket 连接对象，用于发送消息
        :param msg: 收到的消息字典，包含群号、用户信息、消息内容等
        """
        self.websocket = websocket
        self.msg = msg
        self.group_id = str(msg.get("group_id"))
        self.user_id = str(msg.get("user_id"))
        self.message_id = msg.get("message_id")
        self.raw_message = msg.get("raw_message")
        self.time = msg.get("time")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间

    async def handle_add_keyword(self):
        """
        处理添加关键词回复的命令
        解析消息内容，提取关键词和回复内容，写入数据库，并反馈操作结果
        用法：添加关键词 关键词 回复内容
        """
        try:
            # 第一部分是命令标记，第二部分是关键词，剩下的全是回复内容
            content = self.raw_message.lstrip(f"{ADD_COMMAND}").strip()
            parts = content.split(" ", 1)
            keyword = parts[0].strip()
            reply = parts[1].strip()
            with DataManager() as dm:
                dm.add_keyword(
                    self.group_id, keyword, reply, self.user_id, self.formatted_time
                )
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(
                        f"✅ 添加关键词「{keyword}」成功！\n"
                        f"添加者：{self.user_id}\n"
                        f"添加时间：{self.formatted_time}\n"
                        f"💬 回复内容：{reply}"
                    ),
                ],
                note="del_msg=15",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 添加关键词失败: {e}")

    async def handle_delete_keyword(self):
        """
        处理删除关键词回复的命令
        解析消息内容，提取关键词，从数据库中删除对应记录，并反馈操作结果
        先检查是否有这个关键词
        """
        try:
            content = self.raw_message.lstrip(f"{DELETE_COMMAND}").strip()
            keyword = content.strip()
            with DataManager() as dm:
                # 先检查关键词是否存在
                reply = dm.get_reply(self.group_id, keyword)
                if reply is None:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                f"⚠️ 关键词「{keyword}」不存在，无法删除。"
                            ),
                        ],
                        note="del_msg=15",
                    )
                    return
                dm.delete_keyword(self.group_id, keyword)
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message(f"✅ 删除关键词「{keyword}」成功！"),
                ],
                note="del_msg=15",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 删除关键词失败: {e}")

    async def handle_list_keyword(self):
        """
        处理查看关键词回复的命令
        查询当前群的所有关键词，生成列表并发送给群聊
        """
        try:
            with DataManager() as dm:
                keywords = dm.get_all_keywords(self.group_id)
                if not keywords:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message("当前群没有设置关键词回复。"),
                        ],
                        note="del_msg=15",
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_reply_message(self.message_id),
                            generate_text_message(
                                f"当前群共有{len(keywords)}个关键词回复：\n"
                                + "\n".join(f"🔑 {keyword}" for keyword in keywords)
                            ),
                        ],
                        note="del_msg=15",
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 查看关键词失败: {e}")

    async def handle_clear_keyword(self):
        """
        处理清空关键词回复的命令
        清空当前群的所有关键词回复，并反馈操作结果
        """
        try:
            with DataManager() as dm:
                dm.clear_keywords(self.group_id)
            await send_group_msg(
                self.websocket,
                self.group_id,
                [
                    generate_reply_message(self.message_id),
                    generate_text_message("✅ 已清空当前群的所有关键词回复。"),
                ],
                note="del_msg=15",
            )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 清空关键词失败: {e}")

    async def handle_keywords_reply(self):
        """
        处理关键词回复的命令
        根据关键词匹配回复内容，并发送给群聊
        """
        try:
            with DataManager() as dm:
                reply = dm.get_reply(self.group_id, self.raw_message)
                if reply:
                    await send_group_msg_with_cq(
                        self.websocket,
                        self.group_id,
                        reply,
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}] 关键词回复失败: {e}")

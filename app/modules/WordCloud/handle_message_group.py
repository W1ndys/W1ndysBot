import re
from . import MODULE_NAME, SWITCH_NAME, GENERATE_WORD_CLOUD, SUMMARIZE_CHAT
from core.menu_manager import MENU_COMMAND
import logger
from core.switchs import is_group_switch_on, handle_module_group_switch
from api.message import send_group_msg, send_group_msg_with_cq
from api.generate import (
    generate_text_message,
    generate_image_message,
    generate_reply_message,
)
from datetime import datetime
from .WordCloud import QQMessageAnalyzer
from .LLM import DifyClient
from core.menu_manager import MenuManager
from core.auth import is_group_admin, is_system_admin


class GroupMessageHandler:
    """群消息处理器"""

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.sub_type = msg.get("sub_type", "")  # 子类型，只有normal
        self.group_id = str(msg.get("group_id", ""))  # 群号
        self.message_id = str(msg.get("message_id", ""))  # 消息ID
        self.user_id = str(msg.get("user_id", ""))  # 发送者QQ号
        self.message = msg.get("message", {})  # 消息段数组
        self.raw_message = msg.get("raw_message", "")  # 原始消息
        self.sender = msg.get("sender", {})  # 发送者信息
        self.nickname = self.sender.get("nickname", "")  # 昵称
        self.card = self.sender.get("card", "")  # 群名片
        self.role = self.sender.get("role", "")  # 群身份

    async def handle(self):
        """
        处理群消息
        """
        try:
            if self.raw_message.lower() == SWITCH_NAME.lower():
                # 鉴权
                if not is_group_admin(self.role) and not is_system_admin(self.user_id):
                    return
                await handle_module_group_switch(
                    MODULE_NAME,
                    self.websocket,
                    self.group_id,
                    self.message_id,
                )
                return

            # 处理菜单命令（无视开关状态）
            if self.raw_message.lower() == f"{SWITCH_NAME}{MENU_COMMAND}".lower():
                menu_text = MenuManager.get_module_commands_text(MODULE_NAME)
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_reply_message(self.message_id),
                        generate_text_message(menu_text),
                    ],
                    note="del_msg=30",
                )
                return

            # 如果没开启群聊开关，则不处理
            if not is_group_switch_on(self.group_id, MODULE_NAME):
                return

            analyzer = QQMessageAnalyzer(self.group_id)

            # 如果消息是词云命令，则生成词云
            if self.raw_message.lower() == GENERATE_WORD_CLOUD.lower():
                # 生成今日词云图片和top10词汇
                img_base64 = analyzer.generate_wordcloud_image_base64()
                wordcloud_data, top10_words = analyzer.generate_daily_report()
                # 检查 img_base64 是否为 None
                if img_base64 is None:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [generate_text_message("词云图片生成失败，请稍后重试。")],
                    )
                    return
                # 发送词云图片
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [
                        generate_text_message(
                            "top10词汇：\n"
                            + "\n".join(
                                [
                                    f"{i+1}. {word}（{count}次）"
                                    for i, (word, count) in enumerate(top10_words)
                                ]
                            )
                        ),
                        generate_image_message(img_base64),
                    ],
                )
                return

            # 如果消息是总结聊天命令，则调用LLM总结
            if self.raw_message.lower() == SUMMARIZE_CHAT.lower():
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [generate_text_message("正在总结今日聊天内容，请稍候...")],
                )

                # 获取今日聊天消息
                messages_with_details = analyzer.get_daily_messages_with_details()
                logger.info(f"[{MODULE_NAME}]今日聊天消息: {messages_with_details}")
                if not messages_with_details:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [generate_text_message("今日暂无聊天记录，无法生成总结。")],
                    )
                    return

                # 构建聊天记录文本
                chat_text = self._format_chat_for_summary(messages_with_details)
                logger.info(f"[{MODULE_NAME}]格式化后的聊天记录: {chat_text}")
                # 调用LLM生成总结
                client = DifyClient()

                response = await client.send_request(self.user_id, str(chat_text))
                answer, tokens, price, currency = client.parse_response(response)
                if answer:
                    summary_text = f"{answer}\n\n💬 消息数：{len(messages_with_details)}\n🤖 Token消耗：{tokens}"
                    await send_group_msg_with_cq(
                        self.websocket,
                        self.group_id,
                        summary_text,
                    )
                else:
                    await send_group_msg(
                        self.websocket,
                        self.group_id,
                        [
                            generate_text_message(
                                "聊天总结失败，请检查Dify API配置或稍后重试。"
                            )
                        ],
                    )
                return

            analyzer.add_message(self.raw_message, self.user_id, self.formatted_time)
            logger.info(
                f"[{MODULE_NAME}]群{self.group_id}的{self.nickname}({self.user_id})有新消息存储"
            )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

    def _format_chat_for_summary(self, messages_with_details):
        """
        格式化聊天记录以便LLM总结

        Args:
            messages_with_details: 包含消息详情的列表

        Returns:
            list: 保留原有字段但清理消息内容的记录列表
        """

        formatted_messages = []
        for msg in messages_with_details:
            # 创建新的消息对象，保留原有字段
            formatted_msg = msg.copy()

            # 清理消息内容，移除CQ码等
            content = msg["message_content"]
            # 替换图片CQ码
            content = re.sub(
                r"\[CQ:image.*?\]", "这是一张图片或表情包，内容已隐藏", content
            ).strip()
            # 替换语音CQ码
            content = re.sub(
                r"\[CQ:record.*?\]", "这是一段语音，内容已隐藏", content
            ).strip()
            # 替换视频CQ码
            content = re.sub(
                r"\[CQ:video.*?\]", "这是一段视频，内容已隐藏", content
            ).strip()
            # 替换文件CQ码
            content = re.sub(
                r"\[CQ:file.*?\]", "这是一段文件，内容已隐藏", content
            ).strip()

            if content:  # 只保留有实际内容的消息
                formatted_msg["message_content"] = content
                formatted_messages.append(formatted_msg)

        return formatted_messages

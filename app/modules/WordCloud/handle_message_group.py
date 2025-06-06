from . import MODULE_NAME, SWITCH_NAME, GENERATE_WORD_CLOUD, MENU_COMMAND
import logger
from core.switchs import is_group_switch_on, handle_module_group_switch
from api.message import send_group_msg
from api.generate import (
    generate_text_message,
    generate_image_message,
)
from datetime import datetime
from .WordCloud import QQMessageAnalyzer
from core.menu_manager import MenuManager


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
                await handle_module_group_switch(
                    MODULE_NAME,
                    self.websocket,
                    self.group_id,
                    self.user_id,
                    self.role,
                    self.message_id,
                )
                return

            # 处理菜单命令（无视开关状态）
            if self.raw_message.lower() == (SWITCH_NAME + MENU_COMMAND).lower():
                menu_text = MenuManager.get_module_commands_text(MODULE_NAME)
                await send_group_msg(
                    self.websocket,
                    self.group_id,
                    [menu_text],
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

            analyzer.add_message(self.raw_message, self.user_id)
            logger.info(
                f"[{MODULE_NAME}]群{self.group_id}的{self.nickname}({self.user_id})有新消息存储"
            )

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理群消息失败: {e}")

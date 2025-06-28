from . import MODULE_NAME
import logger
from datetime import datetime
from core.switchs import get_all_enabled_groups
from api.message import send_group_msg, send_group_msg_with_cq
from utils.generate import generate_image_message, generate_text_message
from .WordCloud import QQMessageAnalyzer
from .LLM import DifyClient


class MetaEventHandler:
    """
    元事件处理器/定时任务处理器
    元事件可利用心跳来实现定时任务
    """

    _last_execute_minute = None  # 作为类变量

    def __init__(self, websocket, msg):
        self.websocket = websocket
        self.msg = msg
        self.time = msg.get("time", "")
        self.formatted_time = datetime.fromtimestamp(self.time).strftime(
            "%Y-%m-%d %H:%M:%S"
        )  # 格式化时间
        self.post_type = msg.get("post_type", "")
        self.meta_event_type = msg.get("meta_event_type", "")

    async def handle(self):
        try:
            if self.post_type == "meta_event":
                if self.meta_event_type == "lifecycle":
                    await self.handle_lifecycle()
                elif self.meta_event_type == "heartbeat":
                    await self.handle_heartbeat()
                else:
                    logger.error(
                        f"[{MODULE_NAME}]收到未知元事件类型: {self.meta_event_type}"
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理元事件失败: {e}")

    async def handle_lifecycle(self):
        """
        处理生命周期
        """
        try:
            if self.meta_event_type == "connect":
                pass
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理生命周期失败: {e}")

    async def handle_heartbeat(self):
        """
        处理心跳
        仅在每天23:59执行，并且一分钟内只允许执行一次
        """
        try:
            now = datetime.now()
            # 只在23:59执行
            if now.hour == 23 and now.minute == 59:
                current_minute = now.strftime("%Y-%m-%d %H:%M")
                if MetaEventHandler._last_execute_minute == current_minute:
                    # 已经执行过，不再重复执行
                    return
                MetaEventHandler._last_execute_minute = current_minute

                # 获取所有开启的群聊开关
                group_switches = get_all_enabled_groups(MODULE_NAME)
                logger.info(f"[{MODULE_NAME}]所有开启的群聊开关: {group_switches}")
                # 遍历所有开启的群聊开关，生成群词云和top10词汇
                for group_id in group_switches:
                    analyzer = QQMessageAnalyzer(group_id)
                    # 获取今日所有消息
                    messages = analyzer.get_daily_messages_with_details()
                    # 生成词云和top10词汇
                    img_base64 = analyzer.generate_wordcloud_image_base64()
                    wordcloud_data, top10_words = analyzer.generate_daily_report()
                    messages = [
                        generate_text_message(f"群{group_id}的词云和top10词汇如下：\n"),
                        generate_text_message(
                            "top10词汇：\n"
                            + "\n".join(
                                [
                                    f"{i+1}. {word}（{count}次）"
                                    for i, (word, count) in enumerate(top10_words)
                                ]
                            )
                        ),
                    ]
                    if img_base64 is not None:
                        messages.append(generate_image_message(img_base64))
                    else:
                        logger.warning(
                            f"[{MODULE_NAME}]群{group_id}的词云图片生成失败，img_base64为None"
                        )
                    await send_group_msg(
                        self.websocket,
                        group_id,
                        messages,
                    )
                    # 发送Dify请求
                    response = await DifyClient().send_request(
                        f"group_{group_id}", messages
                    )
                    answer, tokens, price, currency = DifyClient.parse_response(
                        response
                    )
                    # 拼接消息字符串
                    answer_message = f"{answer}\n\n"
                    answer_message += f"Token: {tokens}\n"
                    answer_message += f"Price: {price} {currency}\n"
                    # 发送Dify响应
                    await send_group_msg_with_cq(
                        self.websocket,
                        group_id,
                        answer,
                    )
        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理心跳失败: {e}")

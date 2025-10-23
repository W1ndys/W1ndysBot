from .. import MODULE_NAME
from logger import logger
from datetime import datetime, timedelta
from core.switchs import get_all_enabled_groups
from api.message import send_group_msg, send_group_msg_with_cq
from utils.generate import generate_image_message, generate_text_message
from .WordCloud import QQMessageAnalyzer
from .LLM import DifyClient
import asyncio  # 添加这个导入


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
        仅在每天0:00执行，并且一分钟内只允许执行一次，总结昨日内容
        """
        try:
            now = datetime.now()
            # 只在0:0执行
            if now.hour == 0 and now.minute == 0:
                current_minute = now.strftime("%Y-%m-%d %H:%M")
                if MetaEventHandler._last_execute_minute == current_minute:
                    # 已经执行过，不再重复执行
                    return
                MetaEventHandler._last_execute_minute = current_minute

                # 获取昨日日期
                yesterday = now - timedelta(days=1)
                yesterday_str = yesterday.strftime("%Y-%m-%d")

                # 获取所有开启的群聊开关
                group_switches = get_all_enabled_groups(MODULE_NAME)
                logger.info(f"[{MODULE_NAME}]所有开启的群聊开关: {group_switches}")

                # 第一步：先遍历所有群，发送昨日词云
                group_messages_data = {}  # 存储每个群的消息数据，用于后续AI处理

                # 并发处理所有群的词云生成
                wordcloud_tasks = []
                for group_id in group_switches:
                    task = self._process_wordcloud_generation(group_id, yesterday_str)
                    wordcloud_tasks.append(task)

                # 并发执行所有词云生成任务
                if wordcloud_tasks:
                    wordcloud_results = await asyncio.gather(*wordcloud_tasks)

                    # 收集消息数据用于后续AI处理
                    for result in wordcloud_results:
                        if result:
                            group_id, yesterday_messages = result
                            group_messages_data[group_id] = yesterday_messages

                # 第二步：并发处理所有群的AI总结
                ai_tasks = []
                for group_id, yesterday_messages in group_messages_data.items():
                    task = self._process_ai_summary(
                        group_id, yesterday_messages, yesterday_str
                    )
                    ai_tasks.append(task)

                # 并发执行所有AI总结任务
                if ai_tasks:
                    await asyncio.gather(*ai_tasks)

        except Exception as e:
            logger.error(f"[{MODULE_NAME}]处理心跳失败: {e}")

    async def _process_wordcloud_generation(self, group_id, yesterday_str):
        """
        处理单个群的词云生成（在新线程中执行）
        """
        try:
            # 在新线程中执行词云生成相关的计算密集型任务
            def _generate_wordcloud():
                analyzer = QQMessageAnalyzer(group_id)
                # 获取昨日所有消息
                yesterday_messages = analyzer.get_daily_messages_with_details(
                    yesterday_str
                )
                # 生成词云和top10词汇
                img_base64 = analyzer.generate_wordcloud_image_base64(yesterday_str)
                wordcloud_data, top10_words = analyzer.generate_daily_report(
                    yesterday_str
                )
                return yesterday_messages, img_base64, top10_words

            # 使用 asyncio.to_thread 在新线程中执行
            yesterday_messages, img_base64, top10_words = await asyncio.to_thread(
                _generate_wordcloud
            )

            # 发送词云消息
            messages = [
                generate_text_message(
                    f"群{group_id}昨日({yesterday_str})的词云和top10词汇如下：\n"
                ),
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
                    f"[{MODULE_NAME}]群{group_id}昨日({yesterday_str})的词云图片生成失败，img_base64为None"
                )
            await send_group_msg(
                self.websocket,
                group_id,
                messages,
            )

            # 返回消息数据供AI总结使用
            return group_id, yesterday_messages

        except Exception as e:
            logger.error(
                f"[{MODULE_NAME}]群{group_id}昨日({yesterday_str})的词云生成处理失败: {e}"
            )
            return None

    async def _process_ai_summary(self, group_id, yesterday_messages, yesterday_str):
        """
        处理单个群的AI总结（完全在新线程中执行）
        """
        try:
            # 在新线程中执行整个AI总结流程
            def _ai_summary_workflow():
                # 将消息转换为简洁的txt格式，减少token占用
                messages_txt = self._convert_messages_to_txt(yesterday_messages)

                # 创建DifyClient实例并同步调用
                client = DifyClient()

                # 这里需要在新线程中使用asyncio.run来运行异步函数
                import asyncio

                async def _async_ai_workflow():
                    # 发送Dify请求（现在在新线程中执行）
                    response = await client.send_request(
                        f"group_{group_id}",
                        f"以下是群{group_id}在{yesterday_str}的聊天记录：\n{messages_txt}",
                    )
                    # 解析响应
                    answer, tokens, price, currency = await DifyClient.parse_response(
                        response
                    )
                    return answer

                # 在新线程中运行异步AI工作流
                return asyncio.run(_async_ai_workflow())

            # 使用 asyncio.to_thread 在新线程中执行完整的AI总结流程
            answer = await asyncio.to_thread(_ai_summary_workflow)

            # 发送Dify响应（在主线程中执行）
            await send_group_msg_with_cq(
                self.websocket,
                group_id,
                f"昨日({yesterday_str})聊天总结：\n{answer}",
            )
        except Exception as e:
            logger.error(
                f"[{MODULE_NAME}]群{group_id}昨日({yesterday_str})的AI总结处理失败: {e}"
            )

    def _convert_messages_to_txt(self, messages):
        """
        将消息列表转换为简洁的txt格式，减少token占用
        格式：时间 发言者: 内容
        """
        if not messages:
            return "昨日无聊天记录"

        txt_lines = []
        for msg in messages:
            # 提取时间（只保留时分，去掉秒和日期）
            time_str = msg["message_time"]
            if " " in time_str:
                time_part = time_str.split()[1]  # 获取时间部分
                time_part = time_part[:5]  # 只保留时:分
            else:
                time_part = time_str[:5]

            # 保持发言者ID完整
            sender = msg["sender_id"]

            # 内容去除多余空白和换行
            content = msg["message_content"].strip().replace("\n", " ")

            # 组合成简洁格式：时间 发言者: 内容
            txt_lines.append(f"{time_part} {sender}: {content}")

        return "\n".join(txt_lines)

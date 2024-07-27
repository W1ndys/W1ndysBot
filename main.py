import asyncio
import logging
import sys
from pathlib import Path
import websockets
from collections import defaultdict

# 配置功能模块的路径
ws_url = "ws://127.0.0.1:3001"  # napcatQQ 的 WebSocket API 地址
from scripts.forbidden_word_detector.forbidden_word_detector import (
    handle_message as handle_forbidden_word_detector,
)
from scripts.test import handle_message as handle_test

# 启用的功能列表及其消息处理函数
enabled_features = {
    "test": handle_test,
    "forbidden_word_detector": handle_forbidden_word_detector,
}  # 如果不想启用某个功能，只需移除对应的名称

logging.basicConfig(level=logging.INFO)


async def main():
    async with websockets.connect(ws_url) as websocket:
        logging.info("成功连接到 bot...")
        tasks = []

        # 初始化消息队列
        message_queues = defaultdict(asyncio.Queue)

        # 分发消息的任务
        async def dispatch_message():
            async for message in websocket:
                logging.debug(f"收到消息: {message}")
                for queue in message_queues.values():
                    await queue.put(message)

        # 启动每个功能模块的任务
        for feature_name, handle_message in enabled_features.items():

            async def feature_task():
                while True:
                    message = await message_queues[feature_name].get()
                    await handle_message(websocket, message)

            tasks.append(feature_task())

        # 启动分发消息的任务
        tasks.append(dispatch_message())

        if tasks:
            await asyncio.gather(*tasks)
        else:
            logging.info("没有启用任何功能。")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("已关机...")

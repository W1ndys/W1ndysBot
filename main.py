import asyncio
import logging
import sys
from pathlib import Path
import websockets

# 配置功能模块的路径
ws_url = "ws://127.0.0.1:3001"  # napcatQQ 的 WebSocket API 地址
from scripts.forbidden_word_detector.forbidden_word_detector import (
    run as run_forbidden_word_detector,
)
from scripts.test import run as run_test

# 启用的功能列表
enabled_features = {
    "test": run_test,
    "forbidden_word_detector": run_forbidden_word_detector,
}  # 如果不想启用某个功能，只需移除对应的名称

logging.basicConfig(level=logging.INFO)


async def main():
    tasks = []

    async with websockets.connect(ws_url) as websocket:
        logging.info("成功连接到 bot...")

        for feature_name, feature_func in enabled_features.items():
            tasks.append(feature_func(websocket))

        if tasks:
            await asyncio.gather(*tasks)
        else:
            logging.info("没有启用任何功能。")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("已关机...")

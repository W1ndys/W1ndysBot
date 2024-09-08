# bot.py

import logging
import asyncio
import websockets
from config import *
import os
import sys
import datetime
from dingtalk import dingtalk
from config import owner_id

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from authentication import authenticate
from handler_events import handle_message

from api import send_private_msg, send_group_msg


async def connect_to_bot():
    logging.info("正在连接到机器人...")
    logging.info(f"连接地址: {ws_url}")
    async with websockets.connect(ws_url) as websocket:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"已连接到机器人。当前时间: {current_time}")
        if authenticate is not None:
            await authenticate(websocket)
        for _ in owner_id:
            await send_private_msg(
                websocket, _, f"机器人已连接。当前时间: {current_time}"
            )
        for _ in test_group_id:
            await send_group_msg(
                websocket, _, f"机器人已连接。当前时间: {current_time}"
            )
        await dingtalk(
            f"机器人已连接。",
            f"当前时间: {current_time}",
        )
        async for message in websocket:
            # 处理ws消息
            await handle_message(websocket, message)


if __name__ == "__main__":
    asyncio.run(connect_to_bot())

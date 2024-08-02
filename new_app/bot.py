# bot.py

import logging
import asyncio
import websockets
from config import *
import os
import sys
import datetime
import json
from config import owner_id

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from authentication import authenticate
from handler_message import handle_message
from logger import setup_logger
from api import send_private_msg

setup_logger()


async def connect_to_bot():
    logging.info("正在连接到机器人...")
    try:
        async with websockets.connect(ws_url) as websocket:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"已连接到机器人。当前时间: {current_time}")
            await authenticate(websocket)
            await send_private_msg(
                websocket, owner_id, f"机器人已连接。当前时间: {current_time}"
            )

            async for message in websocket:
                logging.info(f"收到消息: {message}")
                await handle_message(websocket, message)
    except Exception as e:
        logging.error(f"连接到机器人时出错: {e}")


if __name__ == "__main__":
    asyncio.run(connect_to_bot())

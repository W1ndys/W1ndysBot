# bot.py

import logging
import asyncio
import websockets
from config import ws_url
from handlers.authentication import authenticate
from handlers.message_handler import handle_message
from logger import setup_logger

setup_logger()


async def connect_to_bot():
    logging.info("正在连接到机器人...")
    async with websockets.connect(ws_url) as websocket:
        logging.info("已连接到机器人。")
        await authenticate(websocket)

        async for message in websocket:
            logging.info(f"收到消息: {message}")
            await handle_message(websocket, message)


if __name__ == "__main__":
    asyncio.run(connect_to_bot())

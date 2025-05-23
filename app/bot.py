import logging
import websockets
from config import *

from handle_events import EventHandler

handler = None


async def connect_to_bot():
    """连接到机器人并开始接收消息"""
    global handler
    handler = EventHandler()  # 只创建一次

    logging.info("正在连接到机器人...")

    # 如果 token 不为 None，则在 URL 中添加 token 参数
    connection_url = WS_URL
    if TOKEN is not None:
        connection_url = f"{WS_URL}?access_token={TOKEN}"

    logging.info(f"连接地址: {connection_url}")

    try:
        # 连接到 WebSocket
        async with websockets.connect(connection_url) as websocket:
            try:
                async for message in websocket:
                    try:
                        # 处理消息
                        await handler.handle_message(websocket, message)
                    except Exception as e:
                        logging.error(f"处理消息时出错: {e}")
                        logging.error(f"消息内容: {message}")
            except Exception as e:
                logging.error(f"WebSocket连接出错: {e}")
                raise
    except Exception as e:
        logging.error(f"WebSocket连接失败: {e}")
        return None

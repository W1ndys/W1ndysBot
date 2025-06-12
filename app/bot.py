import websockets
from config import WS_URL, TOKEN
from logger import logger
from handle_events import EventHandler
import asyncio


async def connect_to_bot():
    """连接到机器人并开始接收消息"""

    if WS_URL is None:
        logger.error("WS_URL未设置，请在环境变量中设置")
        exit()

    # 如果 token 不为 None，则在 URL 中添加 token 参数
    connection_url = WS_URL
    if TOKEN is not None:
        connection_url = f"{WS_URL}?access_token={TOKEN}"

    logger.info(f"正在连接到机器人,连接地址: {connection_url}")

    try:
        # 连接到 WebSocket
        async with websockets.connect(connection_url) as websocket:
            try:
                handler = EventHandler(websocket)  # 为每个连接创建一个独立实例
                async for message in websocket:
                    try:
                        # 异步处理消息，不阻塞当前循环
                        # 使用create_task确保即使处理消息耗时，也不会阻塞后续消息接收
                        asyncio.create_task(handler.handle_message(websocket, message))
                    except Exception as e:
                        logger.error(f"处理消息时出错: {e}")
                        logger.error(f"消息内容: {message}")
            except Exception as e:
                logger.error(f"WebSocket连接出错: {e}")
                raise
    except Exception as e:
        logger.error(f"WebSocket连接失败: {e}")
        return None

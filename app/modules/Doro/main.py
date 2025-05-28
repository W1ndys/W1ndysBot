import logger
from . import MODULE_NAME
from .handle_meta_event import MetaEventHandler
from .handle_message import MessageHandler


async def handle_events(websocket, msg):
    """统一事件处理入口

    通过组合模式，将不同类型的事件分发到各个专门的处理器

    Args:
        websocket: WebSocket连接对象
        msg: 接收到的消息字典
    """
    try:

        # 基于事件类型分发到不同的处理器
        post_type = msg.get("post_type", "")

        # 处理元事件
        if post_type == "meta_event":
            await MetaEventHandler(websocket, msg).handle()

        # 处理消息事件
        elif post_type == "message":
            await MessageHandler(websocket, msg).handle()

    except Exception as e:
        # 获取基本事件类型用于错误日志
        logger.error(f"[{MODULE_NAME}]处理{MODULE_NAME}{post_type}事件失败: {e}")

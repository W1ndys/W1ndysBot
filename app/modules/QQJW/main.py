from logger import logger
from . import MODULE_NAME
from .handlers.handle_message import MessageHandler
from .handlers.handle_notice import NoticeHandler
from .handlers.handle_notice_group import GroupNoticeHandler  # 新增导入


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

        # 处理消息事件（群聊开关、管理员命令）
        if post_type == "message":
            await MessageHandler(websocket, msg).handle()

        # 处理通知事件（监听入群、群号引导）
        elif post_type == "notice":
            await NoticeHandler(websocket, msg).handle()

        elif post_type == "meta_event":
            # 在元事件（如心跳/连接建立）时执行群成员列表初始化复制
            try:
                await GroupNoticeHandler(
                    websocket, msg
                )._initialize_group_member_lists()
                logger.info(f"[{MODULE_NAME}]meta_event 触发群成员列表初始化完成")
            except Exception as e:
                logger.error(f"[{MODULE_NAME}]meta_event 初始化群成员列表失败: {e}")

    except Exception as e:
        # 获取基本事件类型用于错误日志
        logger.error(f"[{MODULE_NAME}]处理{MODULE_NAME}{post_type}事件失败: {e}")

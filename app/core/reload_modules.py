import logger
from core.auth import is_system_owner
from api.generate import generate_reply_message, generate_text_message
from api.message import send_group_msg, send_private_msg


MODULE_NAME = "Core"

# 需要获取 EventHandler 实例
from handle_events import EventHandler

# 全局 EventHandler 实例缓存
_event_handler_instance = None


def get_event_handler():
    global _event_handler_instance
    if _event_handler_instance is None:
        _event_handler_instance = EventHandler()
    return _event_handler_instance


async def handle_events(websocket, message):
    try:
        # 只允许系统管理员使用 reload 命令
        if not is_system_owner(str(message.get("user_id", ""))):
            return
        # 只处理文本消息
        if message.get("post_type") != "message":
            return
        raw_message = message.get("raw_message", "").strip().lower()
        if raw_message != "reload":
            return
        message_type = message.get("message_type", "")
        reply_message = generate_reply_message(message.get("message_id", ""))
        try:
            # 重新加载模块
            handler = get_event_handler()
            handler._load_modules_dynamically()
            text_message = generate_text_message(f"[{MODULE_NAME}]模块热更新成功！")
            logger.success(f"[{MODULE_NAME}]模块热更新成功！")
        except Exception as e:
            text_message = generate_text_message(f"[{MODULE_NAME}]模块热更新失败: {e}")
            logger.error(f"[{MODULE_NAME}]模块热更新失败: {e}")
        if message_type == "group":
            group_id = str(message.get("group_id", ""))
            await send_group_msg(
                websocket, group_id, [reply_message, text_message], note="del_msg=10"
            )
        elif message_type == "private":
            user_id = str(message.get("user_id", ""))
            await send_private_msg(
                websocket, user_id, [reply_message, text_message], note="del_msg=10"
            )
    except Exception as e:
        logger.error(f"[{MODULE_NAME}]处理重载命令失败: {e}")

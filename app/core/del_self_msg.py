"""
自动撤回自己发送的消息
"""

import logger
import re
import asyncio
from api.message import delete_msg


async def del_self_msg(websocket, msg_id, del_time):
    """
    定时撤回消息
    """
    logger.info(f"自动撤回消息: {msg_id} 将在 {del_time} 秒后撤回")
    await asyncio.sleep(del_time)
    await delete_msg(websocket, msg_id)


async def handle_events(websocket, msg):
    """
    处理回应事件
    """
    try:
        if msg.get("status") == "ok":
            echo = msg.get("echo", {})
            # 格式：del_msg_秒数
            res = re.search(r"del_msg_(\d+)", echo)
            if res:
                del_time = int(res.group(1))
                message_id = msg.get("data", {}).get("message_id")
                if del_time > 0:
                    # 新开一个线程，定时撤回消息
                    asyncio.create_task(del_self_msg(websocket, message_id, del_time))
    except Exception as e:
        logger.error(f"自动撤回发送的消息失败: {e}")

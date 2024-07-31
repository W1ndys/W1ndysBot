# handlers/message_handler.py

import json
import logging
from config import owner, owner_group
from handlers.sender import send_group_msg


async def handle_message(websocket, message):
    try:
        msg = json.loads(message)
        logging.info(f"\n\n{msg}\n\n")

        if "post_type" in msg and msg["post_type"] == "meta_event":
            logging.info(f"心跳包事件: {msg}")

        elif (
            "post_type" in msg
            and msg["post_type"] == "message"
            and msg["message_type"] == "group"
            and msg["group_id"] == owner_group
        ):
            user_id = msg["sender"]["user_id"]
            group_id = msg["group_id"]
            raw_message = msg["raw_message"]

            if user_id in owner and (raw_message == "测试" or raw_message == "test"):
                logging.info("收到管理员的测试消息。")
                await send_group_msg(websocket, group_id, "测试成功")

        elif "post_type" in msg and msg["message_type"] == "private":
            user_id = msg["sender"]["user_id"]
            raw_message = msg["raw_message"]
            logging.info(f"收到私聊消息: {raw_message}")

        else:
            logging.info(f"收到消息: {msg}")

    except Exception as e:
        logging.error(f"处理消息时出错: {e}")

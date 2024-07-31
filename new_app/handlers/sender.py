# handlers/sender.py

import json
import logging


async def send_group_msg(websocket, group_id, content):
    message = {
        "action": "send_group_msg",
        "params": {"group_id": group_id, "message": content},
    }
    await websocket.send(json.dumps(message))
    logging.info(f"已发送消息到群 {group_id}: {content}")


async def send_msg(websocket, message_type, user_id, group_id, message):
    message = {
        "action": "send_msg",
        "params": {
            "message_type": message_type,
            "user_id": user_id,
            "group_id": group_id,
            "message": message,
        },
    }
    await websocket.send(json.dumps(message))
    logging.info(f"已发送消息: {message}")

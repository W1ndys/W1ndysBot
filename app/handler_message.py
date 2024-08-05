# handlers/message_handler.py

import json
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from app.scripts.anonymous_handler.main import handle_anonymous_message
from scripts.GroupManager.main import handle_group_message, handle_group_notice
from scripts.Crypto.main import (
    handle_crypto_group_message,
    handle_crypto_private_message,
)
from scripts.Tools.main import (
    handle_group_message as handle_tools_group_message,
    handle_private_message as handle_tools_private_message,
)

from scripts.AI.qwen import handle_qwen_message_private, handle_qwen_message_group


# 处理消息事件的逻辑
async def handle_message_event(websocket, msg):
    try:
        # 处理群消息
        if msg.get("message_type") == "group":

            group_id = msg["group_id"]
            logging.info(f"处理群消息,群ID:{group_id}")
            logging.info(f"原消息内容:{msg}")
            await handle_group_message(websocket, msg)

            # 编解码功能
            await handle_crypto_group_message(websocket, msg)

            # 实用的API工具功能
            await handle_tools_group_message(websocket, msg)

            # 处理通义千问
            await handle_qwen_message_group(websocket, msg)

        # 处理私聊消息
        elif msg.get("message_type") == "private":
            user_id = msg.get("user_id")
            # 编解码功能
            await handle_crypto_private_message(websocket, msg)

            # 实用的API工具功能
            await handle_tools_private_message(websocket, msg)

            # 处理通义千问
            await handle_qwen_message_private(websocket, user_id, msg)

        else:
            logging.info(f"收到未知消息类型: {msg}")

    except KeyError as e:
        logging.error(f"处理消息事件的逻辑错误: {e}")


# 处理通知事件的逻辑
async def handle_notice_event(websocket, msg):

    # 处理群通知
    if msg.get("post_type") == "notice":
        group_id = msg["group_id"]
        logging.info(f"处理群通知事件, 群ID: {group_id}")
        if handle_group_notice is not None:
            await handle_group_notice(websocket, msg)
        else:
            logging.error("handle_group_notice is None")


# 处理请求事件的逻辑
async def handle_request_event(websocket, msg):
    pass


# 处理元事件的逻辑
async def handle_meta_event(websocket, msg):
    pass


# 处理消息
async def handle_message(websocket, message):

    msg = json.loads(message)

    logging.info(f"处理消息: {msg}")

    if "post_type" in msg:
        if msg["post_type"] == "message":
            # 处理消息事件
            await handle_message_event(websocket, msg)
        elif msg["post_type"] == "notice":
            # 处理通知事件
            await handle_notice_event(websocket, msg)
        elif msg["post_type"] == "request":
            # 处理请求事件
            await handle_request_event(websocket, msg)
        elif msg["post_type"] == "meta_event":
            # 处理元事件
            await handle_meta_event(websocket, msg)
    # 收到非事件消息
    else:
        pass

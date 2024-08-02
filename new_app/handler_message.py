# handlers/message_handler.py

import json
import logging
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from app.scripts.anonymous_handler.main import handle_anonymous_message
from scripts.group.main import handle_group_message


# 处理消息事件的逻辑
async def handle_message_event(websocket, msg):
    try:
        # 处理群消息
        if msg["message_type"] == "group":
            group_id = msg["group_id"]
            logging.info(f"处理群消息, 群ID: {group_id}")
            await handle_group_message(websocket, msg)
        # 处理私聊消息
        elif msg["message_type"] == "private":
            pass
            # await handle_private_message()
            # await handle_anonymous_message(websocket, user_id, raw_message) # 关闭匿名系统
        else:
            logging.info(f"收到未知消息类型: {msg}")

    except KeyError as e:
        logging.error(f"消息中缺少键: {e}")


# 处理通知事件的逻辑
async def handle_notice_event(websocket, msg):
    pass


# 处理请求事件的逻辑
async def handle_request_event(websocket, msg):
    pass


# 处理元事件的逻辑
async def handle_meta_event(websocket, msg):
    pass


# 处理消息
async def handle_message(websocket, message):

    msg = json.loads(message)

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
    else:
        logging.info(f"收到消息: {msg}")

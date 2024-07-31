# handlers/message_handler.py

import json
import logging
import asyncio
from config import owner_id
from handlers.api import send_group_msg, send_private_msg
from scripts.anonymous_handler import (
    handle_anonymous_message,
    handle_reply_message,
    handle_private_message,
)


# 处理消息事件的逻辑
async def handle_message_event(websocket, msg):
    try:
        # 处理群消息
        if msg["message_type"] == "group":

            # 获取消息的基本信息
            group_id = msg["group_id"]  # 获取群组ID
            user_id = msg["user_id"]  # 获取用户ID
            raw_message = msg["raw_message"]  # 获取原始消息
            sender = msg["sender"]  # 获取发送者信息
            sender_user_id = sender.get("user_id")  # 获取发送者用户ID
            sender_nickname = sender.get("nickname")  # 获取发送者昵称

        # 处理私聊消息
        elif msg["message_type"] == "private":

            # 获取消息的基本信息
            user_id = msg["user_id"]  # 获取用户ID
            raw_message = msg["raw_message"]  # 获取原始消息
            sender = msg["sender"]  # 获取发送者信息
            sender_user_id = sender["user_id"]  # 获取发送者用户ID
            sender_nickname = sender["nickname"]  # 获取发送者昵称

            await handle_private_message(
                websocket,
                user_id,
                raw_message,
                sender_user_id,
                sender_nickname,
            )
        else:
            logging.info(f"收到未知消息类型: {msg}")
    except Exception as e:
        logging.error(f"处理消息事件时出错: {e}")


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
    try:
        msg = json.loads(message)
        logging.info(f"\n\n{msg}\n\n")
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

    except Exception as e:
        logging.error(f"处理消息时出错: {e}")

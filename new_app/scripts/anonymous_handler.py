import json
import logging
import random
import datetime
from collections import defaultdict
import re
from handlers.api import send_group_msg, send_private_msg

# 存储匿名ID和用户ID的映射
anonymous_ids = defaultdict(dict)
user_last_message_time = {}


# 生成匿名ID
def generate_anonymous_id():
    return random.randint(1000, 9999)


# 获取当前日期
def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")


# 获取匿名ID
def get_anonymous_id(user_id, group_id):
    current_date = get_current_date()
    if (
        user_id not in anonymous_ids
        or anonymous_ids[user_id].get("date") != current_date
    ):
        anonymous_ids[user_id] = {"date": current_date, "groups": {}}
    if group_id not in anonymous_ids[user_id]["groups"]:
        anonymous_id = generate_anonymous_id()
        anonymous_ids[user_id]["groups"][group_id] = anonymous_id
    return anonymous_ids[user_id]["groups"][group_id]


# 处理匿名消息
async def handle_anonymous_message(websocket, user_id, group_id, raw_message):
    anonymous_id = get_anonymous_id(user_id, group_id)
    message = f"[匿名{anonymous_id}]：\n{raw_message}"
    await send_group_msg(websocket, group_id, message)
    logging.info(f"已发布至[群{group_id}]，你今日在本群内id为{anonymous_id}。")
    return anonymous_id


# 处理回复消息
async def handle_reply_message(websocket, user_id, group_id, raw_message):
    match = re.match(r"回复(\d+)\s+(.*)", raw_message)
    if match:
        target_id = match.group(1)
        reply_message = match.group(2)
        anonymous_id = get_anonymous_id(user_id, group_id)
        message = f"[匿名{anonymous_id}]：\n回复{target_id} {reply_message}"
        await send_group_msg(websocket, group_id, message)
        logging.info(
            f"识别到四位编号，已通知到[匿名{target_id}]，且已发布在[群{group_id}]，你今日在本群内id为{anonymous_id}。"
        )
        return anonymous_id, target_id
    return None, None


# 发送私聊消息
async def send_private_msg(websocket, user_id, content):
    message = {
        "action": "send_private_msg",
        "params": {"user_id": user_id, "message": content},
    }
    await websocket.send(json.dumps(message))
    logging.info(f"已发送消息到用户 {user_id}: {content}")


# 处理私聊消息
async def handle_private_message(
    websocket,
    user_id,
    raw_message,
    sender_user_id,
    sender_nickname,
):
    if user_id not in user_last_message_time:
        welcome_message = "欢迎使用匿名消息功能。你可以通过发送'匿名消息到[群号] 内容'来发送匿名消息。"
        await send_private_msg(websocket, user_id, welcome_message)
    user_last_message_time[user_id] = datetime.datetime.now()

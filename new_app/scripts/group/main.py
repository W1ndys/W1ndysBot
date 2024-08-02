# 群管系统
import json
import logging
import asyncio
import websockets
import re
import colorlog
import os
import random
import sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
)
from new_app.api import *
from new_app.config import owner_id


# 判断用户是否是QQ群群主
async def is_qq_owner(role):
    if role == "owner":
        return True
    else:
        return False


# 判断用户是否是QQ群管理员
async def is_qq_admin(role):
    if role == "admin":
        return True
    else:
        return False


# 禁言自己随机时间
async def banme_random_time(websocket, group_id, user_id):

    logging.info(f"执行禁言自己随机时间")
    # 随机时间
    ban_time = random.randint(1, 600)
    # 执行
    await set_group_ban(websocket, group_id, user_id, ban_time)

    logging.info(f"禁言{user_id} {ban_time} 秒。")


# 禁言指定用户
async def ban_user(websocket, group_id, message):

    # 初始化
    ban_qq = None
    ban_duration = None

    # 遍历message列表，查找type为'at'的项并读取qq字段
    for i, item in enumerate(message):
        if item["type"] == "at":
            ban_qq = item["data"]["qq"]
            # 检查下一个元素是否存在且类型为'text'
            if i + 1 < len(message) and message[i + 1]["type"] == "text":
                ban_duration = int(message[i + 1]["data"]["text"].strip())
            else:
                ban_duration = 60  # 默认60秒

    if ban_qq and ban_duration:
        # 执行
        await set_group_ban(websocket, group_id, ban_qq, ban_duration)


# 解禁
async def unban_user(websocket, group_id, message):
    logging.info("收到管理员的解禁消息。")
    # 初始化
    unban_qq = None
    # 遍历message列表，查找type为'at'的项并读取qq字段
    for item in message:
        if item["type"] == "at":
            unban_qq = item["data"]["qq"]
    # 执行
    await set_group_ban(websocket, group_id, unban_qq, 0)


# 随机禁言
async def ban_random_user(websocket, group_id, message):
    logging.info("收到管理员的随机禁言一个有缘人消息。")

    # 获取群成员列表
    response_data = await get_group_member_list(websocket, group_id, no_cache=True)
    logging.info(f"response_data: {response_data}")
    if response_data["status"] == "ok" and response_data["retcode"] == 0:
        members = response_data["data"]
        if members:
            # 过滤掉群主和管理员
            members = [
                member for member in members if member["role"] not in ["owner", "admin"]
            ]
            if members:
                # 随机选择一个成员
                random_member = random.choice(members)
                ban_qq = random_member["user_id"]
                ban_duration = random.randint(1, 600)  # 禁言该成员1分钟
                ban_message = f"让我们恭喜 [CQ:at,qq={ban_qq}] 被禁言了 {ban_duration} 秒。\n注：群主及管理员无法被禁言。"
                await set_group_ban(websocket, group_id, ban_qq, ban_duration)
            else:
                logging.info("没有可禁言的成员。")
                ban_message = "没有可禁言的成员。"
        else:
            logging.info("群成员列表为空。")
            ban_message = "群成员列表为空。"

        await send_group_msg(websocket, group_id, ban_message)
    else:
        logging.error(f"处理消息时出错: {response_data}")


async def handle_group_message(websocket, msg):
    try:
        # 读取消息信息
        user_id = msg["sender"]["user_id"]
        group_id = msg["group_id"]
        raw_message = msg["raw_message"]
        role = msg["sender"]["role"]

        # 鉴权
        is_admin = await is_qq_admin(role)
        is_owner = await is_qq_owner(role)
        is_authorized = (is_admin or is_owner) or (user_id in owner_id)

        # 全员禁言
        if raw_message == "全员禁言" and is_authorized:
            await set_group_whole_ban(websocket, group_id, True)  # 全员禁言

        # 全员解禁
        if raw_message == "全员解禁" and is_authorized:
            await set_group_whole_ban(websocket, group_id, False)  # 全员解禁

        # 踢人
        if is_authorized and (
            re.match(r"kick.*", raw_message)
            or re.match(r"t.*", raw_message)
            or re.match(r"踢.*", raw_message)
        ):
            # 初始化
            kick_qq = None

            # 遍历message列表，查找type为'at'的项并读取qq字段
            for i, item in enumerate(msg["message"]):
                if item["type"] == "at":
                    kick_qq = item["data"]["qq"]
                    break
            # 执行
            if kick_qq:
                await set_group_kick(websocket, group_id, kick_qq)

        # 禁言命令
        if re.match(r"ban.*", raw_message):

            # 禁言自己随机时间
            if raw_message == "banme":
                await banme_random_time(websocket, group_id, user_id)

            # 禁言指定用户
            if re.match(r"ban.*", raw_message) and is_authorized:
                await ban_user(websocket, group_id, msg["message"])

            # 随机禁言一个有缘人
            if raw_message == "banrandom" and is_authorized:
                await ban_random_user(websocket, group_id, msg["message"])

        # 解禁
        if re.match(r"unban.*", raw_message) and is_authorized:
            await unban_user(websocket, group_id, msg["message"])

    except Exception as e:
        logging.error(f"处理群消息时出错: {e}")

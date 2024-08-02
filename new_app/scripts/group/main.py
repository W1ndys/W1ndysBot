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
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )  # 获取了文件上级四层路径
    )
)
from new_app.api import *
from new_app.config import owner_id


# 读取违禁词列表
def load_banned_words(group_id):
    try:
        with open(
            f"{os.path.dirname(os.path.abspath(__file__))}/banned_words_{group_id}.json",
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


# 保存违禁词列表
def save_banned_words(group_id, banned_words):
    with open(
        f"{os.path.dirname(os.path.abspath(__file__))}/banned_words_{group_id}.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(banned_words, f, ensure_ascii=False, indent=4)


# 读取违禁词检测状态
def load_banned_words_status(group_id):
    try:
        with open(
            f"{os.path.dirname(os.path.abspath(__file__))}/banned_words_status_{group_id}.json",
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f).get("status", True)
    except FileNotFoundError:
        return True  # 默认开启


# 保存违禁词检测状态
def save_banned_words_status(group_id, status):
    with open(
        f"{os.path.dirname(os.path.abspath(__file__))}/banned_words_status_{group_id}.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump({"status": status}, f, ensure_ascii=False, indent=4)


# 查看违禁词列表
async def list_banned_words(websocket, group_id):
    banned_words = load_banned_words(group_id)
    if banned_words:
        banned_words_message = "违禁词列表:\n" + "\n".join(banned_words)
    else:
        banned_words_message = "违禁词列表为空。"
    await send_group_msg(websocket, group_id, banned_words_message)


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


# 检查违禁词
async def check_banned_words(websocket, group_id, msg):
    if not load_banned_words_status(group_id):
        return False  # 如果违禁词检测关闭，直接返回

    banned_words = load_banned_words(group_id)
    raw_message = msg["raw_message"]

    for word in banned_words:
        if word in raw_message:
            # 撤回消息
            message_id = int(msg["message_id"])
            await delete_msg(websocket, message_id)
            # 发送警告文案
            warning_message = f"""警告：请不要发送违禁词！
如有误删是发的内容触发了违禁词，请及时联系管理员处理。

有新的事件被处理了，请查看是否正常处理[CQ:at,qq=2769731875]"""
            await send_group_msg(websocket, group_id, warning_message)
            # 禁言1分钟
            user_id = msg["sender"]["user_id"]
            await set_group_ban(websocket, group_id, user_id, 60)
            return True
    # 检查是否包含视频
    if any(item["type"] == "video" for item in msg["message"]):

        # 撤回消息
        message_id = int(msg["message_id"])
        await delete_msg(websocket, message_id)
        await send_group_msg(websocket, group_id, "为防止广告，本群禁止发送视频")
        return True

    return False


async def handle_group_message(websocket, msg):
    try:
        # 读取消息信息
        user_id = msg["sender"]["user_id"]
        group_id = msg["group_id"]
        raw_message = msg["raw_message"]
        role = msg["sender"]["role"]
        message_id = int(msg["message_id"])

        # 鉴权
        is_admin = await is_qq_admin(role)
        is_owner = await is_qq_owner(role)
        is_authorized = (is_admin or is_owner) or (user_id in owner_id)

        # 检查是否为管理员发送的"测试"消息
        if is_authorized and (raw_message == "测试" or raw_message == "test"):
            logging.info("收到管理员的测试消息。")
            if raw_message == "测试":
                await send_group_msg(websocket, group_id, "测试成功")
            elif raw_message == "test":
                await send_group_msg(websocket, group_id, "Test successful")

        # 检查违禁词
        if await check_banned_words(websocket, group_id, msg):
            return

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
            # 随机禁言随机秒
            if raw_message == "banrandom" and is_authorized:
                await ban_random_user(websocket, group_id, msg["message"])

        # 解禁
        if re.match(r"unban.*", raw_message) and is_authorized:
            await unban_user(websocket, group_id, msg["message"])

        # 撤回消息
        if "recall" in raw_message and is_authorized:
            message_id = int(msg["message"][0]["data"]["id"])  # 获取回复消息的消息id
            await delete_msg(websocket, message_id)

        # 管理违禁词
        if is_authorized:
            if raw_message.startswith("add_banned_word "):
                new_word = raw_message.split(" ", 1)[1].strip()
                banned_words = load_banned_words(group_id)
                if new_word not in banned_words:
                    banned_words.append(new_word)
                    save_banned_words(group_id, banned_words)
                    await send_group_msg(
                        websocket, group_id, f"已添加违禁词: {new_word}"
                    )
            elif raw_message.startswith("remove_banned_word "):
                remove_word = raw_message.split(" ", 1)[1].strip()
                banned_words = load_banned_words(group_id)
                if remove_word in banned_words:
                    banned_words.remove(remove_word)
                    save_banned_words(group_id, banned_words)
                    await send_group_msg(
                        websocket, group_id, f"已移除违禁词: {remove_word}"
                    )
            elif raw_message == "list_banned_words":
                await list_banned_words(websocket, group_id)

        # 管理违禁词检测状态
        if is_authorized:
            if raw_message == "enable_banned_words":
                save_banned_words_status(group_id, True)
                await send_group_msg(websocket, group_id, "已开启违禁词检测。")
            elif raw_message == "disable_banned_words":
                save_banned_words_status(group_id, False)
                await send_group_msg(websocket, group_id, "已关闭违禁词检测。")

    except Exception as e:
        logging.error(f"处理群消息时出错: {e}")

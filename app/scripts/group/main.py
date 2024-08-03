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
from datetime import datetime

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )  # 获取了文件上级四层路径
    )
)
from app.api import *
from app.config import owner_id


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


# 读取入群欢迎状态
def load_welcome_status(group_id):
    try:
        with open(
            f"{os.path.dirname(os.path.abspath(__file__))}/welcome_status_{group_id}.json",
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f).get("status", True)
    except FileNotFoundError:
        return True  # 默认开启


# 保存入群欢迎状态
def save_welcome_status(group_id, status):
    with open(
        f"{os.path.dirname(os.path.abspath(__file__))}/welcome_status_{group_id}.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump({"status": status}, f, ensure_ascii=False, indent=4)
    # 同步设置退群欢送状态
    save_farewell_status(group_id, status)


# 保存退群欢送状态
def save_farewell_status(group_id, status):
    with open(
        f"{os.path.dirname(os.path.abspath(__file__))}/farewell_status_{group_id}.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump({"status": status}, f, ensure_ascii=False, indent=4)


# 读取退群欢送状态
def load_farewell_status(group_id):
    try:
        with open(
            f"{os.path.dirname(os.path.abspath(__file__))}/farewell_status_{group_id}.json",
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f).get("status", True)
    except FileNotFoundError:
        return True  # 默认开启


# 读取邀请链状态
def load_invite_chain_status(group_id):
    try:
        with open(
            f"{os.path.dirname(os.path.abspath(__file__))}/invite_chain_status_{group_id}.json",
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f).get("status", True)
    except FileNotFoundError:
        return True  # 默认开启


# 保存邀请链状态
def save_invite_chain_status(group_id, status):
    with open(
        f"{os.path.dirname(os.path.abspath(__file__))}/invite_chain_status_{group_id}.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump({"status": status}, f, ensure_ascii=False, indent=4)


# 扫描邀请链
async def view_invite_chain(websocket, group_id, target_user_id):
    if not load_invite_chain_status(group_id):
        await send_group_msg(websocket, group_id, "邀请链功能已关闭。")
        return

    invite_chain = load_invite_chain(group_id)
    if not invite_chain:
        await send_group_msg(websocket, group_id, "没有找到邀请链。")
        return

    def find_invite_chain(target_user_id, chain, visited):
        for inviter in invite_chain:
            if (
                inviter["user_id"] == target_user_id
                and inviter["user_id"] not in visited
            ):
                chain.append(inviter)
                visited.add(inviter["user_id"])
                find_invite_chain(inviter["operator_id"], chain, visited)

    chain = []
    visited = set()
    find_invite_chain(target_user_id, chain, visited)

    if chain:
        invite_chain_message = "邀请链:\n\n"
        for inviter in chain:
            invite_chain_message += f"【{inviter['operator_id']}】邀请了【{inviter['user_id']}】\n邀请时间：{inviter['date']}\n\n"
    else:
        invite_chain_message = "没有找到相关的邀请链。"

    await send_group_msg(websocket, group_id, invite_chain_message)


# 记录邀请链
async def save_invite_chain(group_id, user_id, operator_id):
    if not load_invite_chain_status(group_id):
        return

    # 加载整个群的邀请链
    invite_chain = load_invite_chain(group_id)

    # 更新特定用户的邀请链
    invite_chain.append(
        {
            "user_id": str(user_id),
            "operator_id": str(operator_id),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )

    # 保存整个群的邀请链
    with open(
        f"{os.path.dirname(os.path.abspath(__file__))}/invite_chain_{group_id}.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(invite_chain, f, ensure_ascii=False, indent=4)


# 删除邀请链
async def delete_invite_chain(group_id, user_id):
    invite_chain = load_invite_chain(group_id)
    if user_id in invite_chain:
        invite_chain.remove(user_id)
        with open(
            f"{os.path.dirname(os.path.abspath(__file__))}/invite_chain_{group_id}.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(invite_chain, f, ensure_ascii=False, indent=4)


# 读取邀请链
def load_invite_chain(group_id):
    try:
        with open(
            f"{os.path.dirname(os.path.abspath(__file__))}/invite_chain_{group_id}.json",
            "r",
            encoding="utf-8",
        ) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


# 处理入群欢迎
async def handle_welcome_message(
    websocket,
    group_id,
    user_id,
):
    if load_welcome_status(group_id):
        welcome_message = f"欢迎[CQ:at,qq={user_id}]入群"
        if welcome_message:
            await send_group_msg(websocket, group_id, f"{welcome_message}")


# 处理退群欢送
async def handle_farewell_message(websocket, group_id, user_id, sub_type):
    if load_farewell_status(group_id):
        if sub_type == "kick":
            farewell_message = f"{user_id} 已被踢出群聊🎉"
            if farewell_message:
                await send_group_msg(websocket, group_id, f"{farewell_message}")
        elif sub_type == "leave":
            farewell_message = f"{user_id} 退群了😭"
            if farewell_message:
                await send_group_msg(websocket, group_id, f"{farewell_message}")


# 处理群事件
async def handle_group_notice(websocket, msg):
    operator_id = msg["operator_id"]  # 入群操作者id
    sub_type = msg["sub_type"]  # 事件子类型
    user_id = msg["user_id"]
    group_id = msg["group_id"]

    # 入群消息
    if msg["notice_type"] == "group_increase":
        # 处理入群欢迎
        await handle_welcome_message(websocket, group_id, user_id)
        # 记录邀请链
        if sub_type == "invite" and load_invite_chain_status(group_id):
            await save_invite_chain(group_id, user_id, operator_id)
            await send_group_msg(
                websocket,
                group_id,
                f"已记录[CQ:at,qq={user_id}]的邀请链，邀请者为[CQ:at,qq={operator_id}]，请勿在群内发送违规信息",
            )

    # 退群消息
    if msg["notice_type"] == "group_decrease":
        await handle_farewell_message(websocket, group_id, user_id, sub_type)
        # 删除邀请链
        # 由于删除会导致邀请链断开, 所以不设置退群删除
        # await delete_invite_chain(group_id, user_id)
        # await send_group_msg(
        #     websocket,
        #     group_id,
        #     f"已删除{user_id}的邀请链",
        # )


# 处理群消息
async def handle_group_message(websocket, msg):
    try:
        # 读取消息信息
        user_id = msg["user_id"]
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

        # 管理入群欢迎信息
        if is_authorized:
            if raw_message == "enable_welcome_message":
                save_welcome_status(group_id, True)
                await send_group_msg(websocket, group_id, "已开启入群欢迎和退群欢送。")
            elif raw_message == "disable_welcome_message":
                save_welcome_status(group_id, False)
                await send_group_msg(websocket, group_id, "已关闭入群欢迎和退群欢送。")

        # 管理邀请链状态
        if is_authorized:
            if raw_message == "enable_invite_chain":
                save_invite_chain_status(group_id, True)
                await send_group_msg(websocket, group_id, "已开启邀请链功能。")
            elif raw_message == "disable_invite_chain":
                save_invite_chain_status(group_id, False)
                await send_group_msg(websocket, group_id, "已关闭邀请链功能。")

        # 扫描邀请链
        if raw_message.startswith("view_invite_chain ") or raw_message.startswith(
            "查看邀请链 "
        ):
            target_user_id = raw_message.split(" ", 1)[1].strip()
            await view_invite_chain(websocket, group_id, target_user_id)

    except Exception as e:
        logging.error(f"处理群消息时出错: {e}")

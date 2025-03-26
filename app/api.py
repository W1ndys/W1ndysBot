# api.py

import json
import logging
import os
import uuid
from datetime import datetime
import asyncio
from config import *

SWITCH_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "Switch",
)


# 检查是否是群主
def is_group_owner(role):
    try:
        return role == "owner"
    except Exception as e:
        logging.error(f"[API]检查群主权限失败: {e}")
        return False


# 检查是否是管理员
def is_group_admin(role):
    try:
        return role == "admin"
    except Exception as e:
        logging.error(f"[API]检查管理员权限失败: {e}")
        return False


# 检查是否有权限（管理员、群主或root管理员）
def is_authorized(role, user_id):
    try:
        is_admin = is_group_admin(role)
        is_owner = is_group_owner(role)
        return (is_admin or is_owner) or (user_id in owner_id)
    except Exception as e:
        logging.error(f"[API]检查权限失败: {e}")
        return False


# 发送私聊消息，解析cq码
async def send_private_msg(websocket, user_id, content):
    try:
        # 给content添加随机字符串防止频繁
        random_str = str(uuid.uuid4())
        content = f"{content}\n{random_str}"
        message = {
            "action": "send_private_msg",
            "params": {"user_id": user_id, "message": content},
            "echo": "send_private_msg",
        }
        await websocket.send(json.dumps(message))
        logging.info(f"[API]已发送消息到用户 {user_id}")
        await asyncio.sleep(0.5)
    except Exception as e:
        logging.error(f"[API]发送私聊消息失败: {e}")


# 发送私聊消息，不解析cq码
async def send_private_msg_no_cq(websocket, user_id, content, auto_escape=True):
    try:
        # 给content添加随机字符串防止频繁
        random_str = str(uuid.uuid4())
        content = f"{content}\n{random_str}"
        message = {
            "action": "send_private_msg",
            "params": {
                "user_id": user_id,
                "message": content,
                "auto_escape": auto_escape,
            },
            "echo": "send_private_msg_no_cq",
        }
        await websocket.send(json.dumps(message))
        logging.info(f"[API]已发送消息到用户 {user_id}")
    except Exception as e:
        logging.error(f"[API]发送私聊消息失败: {e}")


# 发送私聊消息，并获取消息ID
async def send_private_msg_with_reply(websocket, user_id, content):
    try:
        # 给content添加随机字符串防止频繁
        random_str = str(uuid.uuid4())
        content = f"{content}\n{random_str}"
        message = {
            "action": "send_private_msg",
            "params": {"user_id": user_id, "message": content},
            "echo": "send_private_msg_with_reply",
        }
        await websocket.send(json.dumps(message))
        logging.info(f"[API]已发送消息到用户 {user_id}")
    except Exception as e:
        logging.error(f"[API]发送私聊消息失败: {e}")


# 发送群消息
async def send_group_msg(websocket, group_id, content):
    try:
        # 给content添加随机字符串防止频繁
        random_str = str(uuid.uuid4())
        content = f"{content}\n{random_str}"
        message = {
            "action": "send_group_msg",
            "params": {"group_id": group_id, "message": content},
            "echo": f"send_group_msg_{content}",
        }
        await websocket.send(json.dumps(message))
        logging.info(f"[API]已发送群消息到群 {group_id}")
        await asyncio.sleep(0.5)
    except Exception as e:
        logging.error(f"[API]发送群消息失败: {e}")


# 发送群消息，不解析cq码
async def send_group_msg_no_cq(websocket, group_id, content, auto_escape=True):
    try:
        message = {
            "action": "send_group_msg",
            "params": {
                "group_id": group_id,
                "message": content,
                "auto_escape": auto_escape,
            },
            "echo": "send_group_msg_no_cq",
        }
        await websocket.send(json.dumps(message))
        logging.info(f"[API]已发送无CQ码的群消息到群 {group_id}")
    except Exception as e:
        logging.error(f"[API]发送无CQ码的群消息失败: {e}")


# 给群分享推荐好友
async def send_ArkSharePeer_group(websocket, user_id, group_id):
    try:
        message = {
            "action": "ArkSharePeer",
            "params": {"user_id": str(user_id)},
            "echo": "send_ArkSharePeer_group",
        }
        await websocket.send(json.dumps(message))
        logging.info(f"[API]已发送推荐好友到群 {group_id}")
    except Exception as e:
        logging.error(f"[API]发送推荐好友失败: {e}")


# 给群分享加群卡片
async def send_ArkShareGroupEx_group(websocket, group_id, target_group_id):
    try:
        message = {
            "action": "ArkShareGroupEx",
            "params": {"group_id": str(group_id)},
            "echo": "send_ArkShareGroupEx_group",
        }
        await websocket.send(json.dumps(message))
        logging.info(f"[API]已发送加群卡片到群 {target_group_id}")
    except Exception as e:
        logging.error(f"[API]发送加群卡片失败: {e}")


# 给私聊分享加群卡片
async def send_ArkShareGroupEx_private(websocket, user_id):
    try:
        message = {
            "action": "ArkShareGroupEx",
            "params": {"user_id": str(user_id)},
            "echo": "send_ArkShareGroupEx_private",
        }
        await websocket.send(json.dumps(message))
        logging.info(f"[API]已发送加群卡片到私聊 {user_id}")
    except Exception as e:
        logging.error(f"[API]发送加群卡片失败: {e}")


# 给私聊分享推荐好友
async def send_ArkSharePeer_private(websocket, user_id):
    try:
        message = {
            "action": "ArkSharePeer",
            "params": {"user_id": str(user_id)},
            "echo": "send_ArkSharePeer_private",
        }
        await websocket.send(json.dumps(message))
        logging.info(f"[API]已发送推荐好友到私聊 {user_id}")
    except Exception as e:
        logging.error(f"[API]发送推荐好友失败: {e}")


# 向群发送JSON消息
async def send_json_msg_group(websocket, group_id, data):
    try:
        message = {
            "type": "json",
            "data": {"data": data},
            "echo": "send_json_msg_group",
        }  # 注意这边两层data，详情可见https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#json-%E6%B6%88%E6%81%AF
        await send_group_msg(websocket, group_id, message)
    except Exception as e:
        logging.error(f"[API]发送JSON消息失败: {e}")


# 向私聊发送JSON消息
async def send_json_msg_private(websocket, user_id, data):
    try:
        message = {
            "type": "json",
            "data": {"data": data},
            "echo": "send_json_msg_private",
        }
        await send_private_msg(websocket, user_id, message)
    except Exception as e:
        logging.error(f"[API]发送JSON消息失败: {e}")


# 发送消息
async def send_msg(websocket, message_type, user_id, group_id, message):
    try:
        message = {
            "action": "send_msg",
            "params": {
                "message_type": message_type,
                "user_id": user_id,
                "group_id": group_id,
                "message": message,
            },
            "echo": "send_msg",
        }
        await websocket.send(json.dumps(message))
        logging.info(f"[API]已发送消息: {message}")
    except Exception as e:
        logging.error(f"[API]发送消息失败: {e}")


# 发送合并转发消息
async def send_forward_msg(websocket, group_id, content):
    try:
        message = {
            "action": "send_forward_msg",
            "params": {"group_id": group_id, "message": content},
            "echo": "send_forward_msg",
        }
        await websocket.send(json.dumps(message))
        logging.info(f"[API]已发送合并转发消息到群 {group_id}")
    except Exception as e:
        logging.error(f"[API]发送合并转发消息失败: {e}")


# 撤回消息
async def delete_msg(websocket, message_id):
    try:
        delete_msg = {
            "action": "delete_msg",
            "params": {"message_id": message_id},
            "echo": "delete_msg",
        }
        await websocket.send(json.dumps(delete_msg))
        logging.info(f"[API]已撤回消息 {message_id}")
    except Exception as e:
        logging.error(f"[API]撤回消息失败: {e}")


# 获取消息
async def get_msg(websocket, message_id):
    try:
        get_msg = {
            "action": "get_msg",
            "params": {"message_id": message_id},
            "echo": "get_msg",
        }
        await websocket.send(json.dumps(get_msg))
        logging.info(f"[API]已获取消息 {message_id}。")
    except Exception as e:
        logging.error(f"[API]获取消息失败: {e}")


# 获取合并转发消息
async def get_forward_msg(websocket, id):
    try:
        get_forward_msg = {
            "action": "get_forward_msg",
            "params": {"message_id": id},
            "echo": "get_forward_msg",
        }
        await websocket.send(json.dumps(get_forward_msg))
        logging.info(f"[API]已获取合并转发消息 {id}。")
    except Exception as e:
        logging.error(f"[API]获取合并转发消息失败: {e}")


# 发送好友赞
async def send_like(websocket, user_id, times):
    try:
        like_msg = {
            "action": "send_like",
            "params": {"user_id": user_id, "times": times},
            "echo": "send_like",
        }
        await websocket.send(json.dumps(like_msg))
        logging.info(f"[API]已发送好友赞 {user_id} {times} 次。")
    except Exception as e:
        logging.error(f"[API]发送好友赞失败: {e}")


# 群组踢人,拒绝加群请求，新增参数reject_add_request，默认True
async def set_group_kick(websocket, group_id, user_id, reject_add_request=True):
    try:
        kick_msg = {
            "action": "set_group_kick",
            "params": {
                "group_id": group_id,
                "user_id": user_id,
                "reject_add_request": reject_add_request,
            },
            "echo": f"set_group_kick_{group_id}_{user_id}",
        }
        await websocket.send(json.dumps(kick_msg))
        logging.info(f"[API]已踢出群 {group_id} 的用户 {user_id}。")
    except Exception as e:
        logging.error(f"[API]踢出用户失败: {e}")


# 群组单人禁言
async def set_group_ban(websocket, group_id, user_id, duration):
    try:
        ban_msg = {
            "action": "set_group_ban",
            "params": {"group_id": group_id, "user_id": user_id, "duration": duration},
            "echo": "set_group_ban",
        }
        await websocket.send(json.dumps(ban_msg))
        if duration == 0:
            logging.info(f"[API]执行解除 [CQ:at,qq={user_id}] 禁言。")
        else:
            logging.info(f"[API]执行禁言 [CQ:at,qq={user_id}] {duration} 秒。")
    except Exception as e:
        logging.error(f"[API]设置禁言失败: {e}")


# 群组匿名用户禁言
async def set_group_anonymous_ban(websocket, group_id, anonymous_flag, duration):
    try:
        anonymous_ban_msg = {
            "action": "set_group_anonymous_ban",
            "params": {
                "group_id": group_id,
                "flag": anonymous_flag,
                "duration": duration,
            },
            "echo": "set_group_anonymous_ban",
        }
        await websocket.send(json.dumps(anonymous_ban_msg))
        if duration == 0:
            logging.info(f"[API]已解除 [CQ:anonymous,flag={anonymous_flag}] 禁言。")
            message = f"已解除 [CQ:anonymous,flag={anonymous_flag}] 禁言。"
        else:
            logging.info(f"[API]已禁止匿名用户 {anonymous_flag} {duration} 秒。")
            message = f"已禁止匿名用户 {anonymous_flag} {duration} 秒。"
        await send_group_msg(websocket, group_id, message)
    except Exception as e:
        logging.error(f"[API]设置匿名用户禁言失败: {e}")


# 群组全员禁言
async def set_group_whole_ban(websocket, group_id, enable):
    try:
        whole_ban_msg = {
            "action": "set_group_whole_ban",
            "params": {"group_id": group_id, "enable": enable},
            "echo": "set_group_whole_ban",
        }
        await websocket.send(json.dumps(whole_ban_msg))
        logging.info(f"[API]已{'开启' if enable else '解除'}群 {group_id} 的全员禁言。")
        await send_group_msg(
            websocket,
            group_id,
            f"已{'开启' if enable else '解除'}群 {group_id} 的全员禁言。",
        )
    except Exception as e:
        logging.error(f"[API]设置全员禁言失败: {e}")


# 群组设置管理员
async def set_group_admin(websocket, group_id, user_id, enable):
    try:
        admin_msg = {
            "action": "set_group_admin",
            "params": {"group_id": group_id, "user_id": user_id, "enable": enable},
            "echo": "set_group_admin",
        }
        await websocket.send(json.dumps(admin_msg))
        logging.info(
            f"已{'授予' if enable else '解除'}群 {group_id} 的管理员 {user_id} 的权限。"
        )
    except Exception as e:
        logging.error(f"[API]设置管理员失败: {e}")


# 群组匿名
async def set_group_anonymous(websocket, group_id, enable):
    try:
        anonymous_msg = {
            "action": "set_group_anonymous",
            "params": {"group_id": group_id, "enable": enable},
            "echo": "set_group_anonymous",
        }
        await websocket.send(json.dumps(anonymous_msg))
        logging.info(f"[API]已{'开启' if enable else '关闭'}群 {group_id} 的匿名。")
    except Exception as e:
        logging.error(f"[API]设置群匿名失败: {e}")


# 设置群名片（群备注）
async def set_group_card(websocket, group_id, user_id, card):
    try:
        card_msg = {
            "action": "set_group_card",
            "params": {"group_id": group_id, "user_id": user_id, "card": card},
            "echo": "set_group_card",
        }
        await websocket.send(json.dumps(card_msg))
        logging.info(f"[API]已设置群 {group_id} 的用户 {user_id} 的群名片为 {card}。")
    except Exception as e:
        logging.error(f"[API]设置群名片失败: {e}")


# 设置群名
async def set_group_name(websocket, group_id, group_name):
    try:
        name_msg = {
            "action": "set_group_name",
            "params": {"group_id": group_id, "group_name": group_name},
            "echo": "set_group_name",
        }
        await websocket.send(json.dumps(name_msg))
        logging.info(f"[API]已设置群 {group_id} 的群名为 {group_name}。")
    except Exception as e:
        logging.error(f"[API]设置群名失败: {e}")


# 退出群组
async def set_group_leave(websocket, group_id, is_dismiss):
    try:
        leave_msg = {
            "action": "set_group_leave",
            "params": {"group_id": group_id, "is_dismiss": is_dismiss},
            "echo": "set_group_leave",
        }
        await websocket.send(json.dumps(leave_msg))
        logging.info(f"[API]已退出群 {group_id}。")
    except Exception as e:
        logging.error(f"[API]退出群组失败: {e}")


# 设置群组专属头衔
async def set_group_special_title(websocket, group_id, user_id, special_title):
    try:
        special_title_msg = {
            "action": "set_group_special_title",
            "params": {
                "group_id": group_id,
                "user_id": user_id,
                "special_title": special_title,
            },
            "echo": f"set_group_special_title_{group_id}_{user_id}_{special_title}",
        }
        await websocket.send(json.dumps(special_title_msg))
        logging.info(
            f"[API]已设置群 {group_id} 的用户 {user_id} 的专属头衔为 {special_title}。"
        )
    except Exception as e:
        logging.error(f"[API]设置群专属头衔失败: {e}")


# 处理加好友请求
async def set_friend_add_request(websocket, flag, approve):
    try:
        request_msg = {
            "action": "set_friend_add_request",
            "params": {"flag": flag, "approve": approve},
            "echo": "set_friend_add_request",
        }
        await websocket.send(json.dumps(request_msg))
        logging.info(f"[API]已{'同意' if approve else '拒绝'}好友请求。")
    except Exception as e:
        logging.error(f"[API]处理好友请求失败: {e}")


# 处理加群请求／邀请
async def set_group_add_request(websocket, flag, type, approve, reason):
    try:
        request_msg = {
            "action": "set_group_add_request",
            "params": {
                "flag": flag,
                "type": type,
                "approve": approve,
                "reason": reason,
            },
            "echo": "set_group_add_request",
        }
        await websocket.send(json.dumps(request_msg))
        logging.info(f"[API]已{'同意' if approve else '拒绝'}群 {type} 请求。")
    except Exception as e:
        logging.error(f"[API]处理入群请求失败: {e}")


# 获取群历史消息，注意count是int类型
async def get_group_msg_history(websocket, group_id, count, user_id):
    try:
        history_msg = {
            "action": "get_group_msg_history",
            "params": {"group_id": group_id, "count": count},
            "echo": f"get_group_msg_history_{group_id}_{user_id}",
        }
        await websocket.send(json.dumps(history_msg))
        logging.info(f"[API]已获取群 {group_id} 的历史消息。")
    except Exception as e:
        logging.error(f"[API]获取群历史消息失败: {e}")


# 获取登录号信息
async def get_login_info(websocket):
    try:
        login_info_msg = {
            "action": "get_login_info",
            "params": {},
            "echo": "get_login_info",
        }
        await websocket.send(json.dumps(login_info_msg))
        logging.info("已获取登录号信息。")
    except Exception as e:
        logging.error(f"[API]获取登录信息失败: {e}")


# 获取陌生人信息
async def get_stranger_info(websocket, user_id, no_cache=False):
    try:
        stranger_info_msg = {
            "action": "get_stranger_info",
            "params": {"user_id": user_id, "no_cache": no_cache},
            "echo": "get_stranger_info",
        }
        await websocket.send(json.dumps(stranger_info_msg))
        logging.info(f"[API]已获取陌生人 {user_id} 信息。")
    except Exception as e:
        logging.error(f"获取陌生人信息失败: {e}")
        return {}


# 获取好友列表
async def get_friend_list(websocket):
    try:
        friend_list_msg = {
            "action": "get_friend_list",
            "params": {},
            "echo": "get_friend_list",
        }
        await websocket.send(json.dumps(friend_list_msg))
        logging.info("已获取好友列表。")
    except Exception as e:
        logging.error(f"[API]获取好友列表失败: {e}")


# 获取群信息
async def get_group_info(websocket, group_id):
    try:
        group_info_msg = {
            "action": "get_group_info",
            "params": {"group_id": group_id},
            "echo": "get_group_info",
        }
        await websocket.send(json.dumps(group_info_msg))
        logging.info(f"[API]已获取群 {group_id} 信息。")
    except Exception as e:
        logging.error(f"[API]获取群信息失败: {e}")


# 获取群列表
async def get_group_list(websocket):
    try:
        group_list_msg = {
            "action": "get_group_list",
            "params": {},
            "echo": "get_group_list",
        }
        await websocket.send(json.dumps(group_list_msg))
        logging.info("已获取群列表。")
    except Exception as e:
        logging.error(f"[API]获取群列表失败: {e}")


# 获取群成员信息
async def get_group_member_info(websocket, group_id, user_id, no_cache=False):
    try:
        group_member_info_msg = {
            "action": "get_group_member_info",
            "params": {"group_id": group_id, "user_id": user_id, "no_cache": no_cache},
            "echo": f"get_group_member_info_{group_id}_{user_id}",
        }
        await websocket.send(json.dumps(group_member_info_msg))
        logging.info(f"[API]已获取群 {group_id} 的用户 {user_id} 信息。")
    except Exception as e:
        logging.error(f"[API]获取群成员信息失败: {e}")
        return None


# 获取群成员入群时间戳并转换为日期时间
def get_group_member_join_time(group_id, user_id, group_member_info):
    try:
        join_time = group_member_info.get("data", {}).get("join_time", 0)
        # 将时间戳转换为日期时间
        join_time_datetime = datetime.fromtimestamp(join_time)
        logging.info(
            f"[API]已获取群 {group_id} 的用户 {user_id} 入群时间戳: {join_time}, 转换后时间: {join_time_datetime}"
        )
        return join_time_datetime
    except Exception as e:
        logging.error(f"[API]获取入群时间失败: {e}")
        return None


# 获取群成员列表
async def get_group_member_list(websocket, group_id, no_cache=False):
    try:
        group_member_list_msg = {
            "action": "get_group_member_list",
            "params": {"group_id": group_id},
            "echo": "get_group_member_list",
        }
        await websocket.send(json.dumps(group_member_list_msg))
        logging.info(f"[API]已获取群 {group_id} 的成员列表。")
    except Exception as e:
        logging.error(f"[API]获取群成员列表失败: {e}")
        return []


# 获取群荣誉信息
async def get_group_honor_info(websocket, group_id, type):
    try:
        honor_info_msg = {
            "action": "get_group_honor_info",
            "params": {"group_id": group_id, "type": type},
            "echo": "get_group_honor_info",
        }
        await websocket.send(json.dumps(honor_info_msg))
        logging.info(f"[API]已获取群 {group_id} 的 {type} 荣誉信息。")
    except Exception as e:
        logging.error(f"[API]获取群荣誉信息失败: {e}")


# 获取 Cookies
async def get_cookies(websocket):
    try:
        cookies_msg = {"action": "get_cookies", "params": {}, "echo": "get_cookies"}
        await websocket.send(json.dumps(cookies_msg))
        logging.info("已获取 Cookies。")
    except Exception as e:
        logging.error(f"[API]获取Cookies失败: {e}")


# 获取 CSRF Token
async def get_csrf_token(websocket):
    try:
        csrf_token_msg = {
            "action": "get_csrf_token",
            "params": {},
            "echo": "get_csrf_token",
        }
        await websocket.send(json.dumps(csrf_token_msg))
        logging.info("已获取 CSRF Token。")
    except Exception as e:
        logging.error(f"[API]获取CSRF Token失败: {e}")


# 获取 QQ 相关接口凭证
async def get_credentials(websocket):
    try:
        credentials_msg = {
            "action": "get_credentials",
            "params": {},
            "echo": "get_credentials",
        }
        await websocket.send(json.dumps(credentials_msg))
        logging.info("已获取 QQ 相关接口凭证。")
    except Exception as e:
        logging.error(f"[API]获取QQ接口凭证失败: {e}")


# 获取语音
async def get_record(websocket, file, out_format, full_path):
    try:
        record_msg = {
            "action": "get_record",
            "params": {"file": file, "out_format": out_format, "full_path": full_path},
            "echo": "get_record",
        }
        await websocket.send(json.dumps(record_msg))
        logging.info(f"[API]已获取语音 {file}。")
    except Exception as e:
        logging.error(f"[API]获取语音失败: {e}")


# 获取图片
async def get_image(websocket, file, out_format, full_path):
    try:
        image_msg = {
            "action": "get_image",
            "params": {"file": file, "out_format": out_format, "full_path": full_path},
            "echo": "get_image",
        }
        await websocket.send(json.dumps(image_msg))
        logging.info(f"[API]已获取图片 {file}。")
    except Exception as e:
        logging.error(f"[API]获取图片失败: {e}")


# 检查是否可以发送图片
async def can_send_image(websocket):
    try:
        can_send_image_msg = {
            "action": "can_send_image",
            "params": {},
            "echo": "can_send_image",
        }
        await websocket.send(json.dumps(can_send_image_msg))
        logging.info("已检查是否可以发送图片。")
    except Exception as e:
        logging.error(f"[API]检查发送图片权限失败: {e}")


# 检查是否可以发送语音
async def can_send_record(websocket):
    try:
        can_send_record_msg = {
            "action": "can_send_record",
            "params": {},
            "echo": "can_send_record",
        }
        await websocket.send(json.dumps(can_send_record_msg))
        logging.info("已检查是否可以发送语音。")
    except Exception as e:
        logging.error(f"[API]检查发送语音权限失败: {e}")


# 获取运行状态
async def get_status(websocket):
    try:
        status_msg = {"action": "get_status", "params": {}, "echo": "get_status"}
        await websocket.send(json.dumps(status_msg))
        logging.info("已获取运行状态。")
    except Exception as e:
        logging.error(f"[API]获取运行状态失败: {e}")


# 获取版本信息
async def get_version_info(websocket):
    try:
        version_info_msg = {
            "action": "get_version_info",
            "params": {},
            "echo": "get_version_info",
        }
        await websocket.send(json.dumps(version_info_msg))
        logging.info("已获取版本信息。")
    except Exception as e:
        logging.error(f"[API]获取版本信息失败: {e}")


# 重启 OneBot 实现
async def set_restart(websocket, delay=0):
    try:
        restart_onebot_msg = {
            "action": "set_restart",
            "params": {"delay": delay},
            "echo": "set_restart",
        }
        await websocket.send(json.dumps(restart_onebot_msg))
        logging.info("已重启 OneBot 实现。")
    except Exception as e:
        logging.error(f"[API]重启OneBot失败: {e}")


# 清理缓存
async def clean_cache(websocket):
    try:
        clean_cache_msg = {"action": "clean_cache", "params": {}, "echo": "clean_cache"}
        await websocket.send(json.dumps(clean_cache_msg))
        logging.info("已清理缓存。")
    except Exception as e:
        logging.error(f"[API]清理缓存失败: {e}")


######## 下面是NapCatQQ的扩展API


# 发送表情回应
# https://bot.q.qq.com/wiki/develop/api-v2/openapi/emoji/model.html#/EmojiType
async def set_msg_emoji_like(websocket, message_id, emoji_id, set=True):
    try:
        set_msg_emoji_like_msg = {
            "action": "set_msg_emoji_like",
            "params": {"message_id": message_id, "emoji_id": emoji_id, "set": set},
            "echo": "set_msg_emoji_like",
        }
        await websocket.send(json.dumps(set_msg_emoji_like_msg))
        logging.info(f"[API]已发送表情回应 {message_id} {emoji_id}。")
    except Exception as e:
        logging.error(f"[API]发送表情回应失败: {e}")

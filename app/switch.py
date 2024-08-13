# 群组开关

import json
import os
import sys

# 添加项目根目录到sys.path
sys.path.append((os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.config import owner_id
from app.api import *


SWITCH_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "app",
    "data",
    "GroupSwitch",
)

print(SWITCH_DATA_DIR)


# 是否是群主
def is_group_owner(role):
    return role == "owner"


# 是否是管理员
def is_group_admin(role):
    return role == "admin"


# 是否是管理员或群主或root管理员
def is_authorized(role, user_id):
    is_admin = is_group_admin(role)
    is_owner = is_group_owner(role)
    return (is_admin or is_owner) or (user_id in owner_id)


def load_switch(group_id, key):
    try:
        with open(
            os.path.join(SWITCH_DATA_DIR, f"{group_id}.json"), "r", encoding="utf-8"
        ) as f:
            switches = json.load(f)
    except FileNotFoundError:
        # 创建文件并写入空字典
        switches = {}
        with open(
            os.path.join(SWITCH_DATA_DIR, f"{group_id}.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(switches, f, ensure_ascii=False, indent=4)

    return switches.get(key, False)


def save_switch(group_id, key, switch):
    try:
        with open(
            os.path.join(SWITCH_DATA_DIR, f"{group_id}.json"), "r", encoding="utf-8"
        ) as f:
            switches = json.load(f)
    except FileNotFoundError:
        switches = {}

    switches[key] = switch

    with open(
        os.path.join(SWITCH_DATA_DIR, f"{group_id}.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(switches, f, ensure_ascii=False, indent=4)


# 获取群组开关
def GroupSwitch(group_id):
    try:
        os.makedirs(SWITCH_DATA_DIR, exist_ok=True)
        with open(
            os.path.join(SWITCH_DATA_DIR, f"{group_id}.json"), "r", encoding="utf-8"
        ) as f:
            switches = json.load(f)
            return switches
    except FileNotFoundError:
        return None


# 查看群所有状态
async def view_group_status(websocket, group_id, raw_message, message_id):
    if raw_message == "groupswitch":
        group_status = GroupSwitch(group_id)

        if group_status:
            status_message = f"[CQ:reply,id={message_id}]群 {group_id} 的状态:\n\n"
            for key, value in group_status.items():
                status_message += f"{key}: {value}\n"
        else:
            status_message = (
                f"[CQ:reply,id={message_id}]未找到群 {group_id} 的状态信息。"
            )

        await send_group_msg(websocket, group_id, status_message)


# 处理群消息
async def handle_GroupSwitch_group_message(websocket, msg):

    # 确保数据目录存在
    os.makedirs(SWITCH_DATA_DIR, exist_ok=True)

    user_id = msg["user_id"]
    group_id = msg["group_id"]
    raw_message = msg["raw_message"]
    role = msg["sender"]["role"]
    message_id = int(msg["message_id"])

    await view_group_status(websocket, group_id, raw_message, message_id)

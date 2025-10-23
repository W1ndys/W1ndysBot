import asyncio
import re
from logger import logger
from config import OWNER_ID
from api.group import get_group_member_list
from api.message import send_private_msg
import os
import json
import time
from .get_group_list import get_all_group_ids

DATA_DIR = os.path.join("data", "Core", "group_member_list")

# 全局变量，记录上次请求时间
last_request_time = 0
REQUEST_INTERVAL = 300  # 5分钟，单位：秒


def save_group_member_list_to_file(group_id, data):
    """
    保存群成员列表信息到文件，确保文件夹存在
    """
    # 文件路径
    file_path = os.path.join(DATA_DIR, f"{group_id}.json")
    # 确保文件夹存在
    os.makedirs(DATA_DIR, exist_ok=True)
    # 保存数据
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_group_member_user_ids(group_id):
    """
    根据群号获取群成员QQ号列表

    Args:
        group_id (str或int): 群号

    Returns:
        list: QQ号列表，如果找不到则返回空列表，QQ号是str类型
    """
    try:
        # 确保群号是字符串格式
        group_id = str(group_id)

        # 构建文件路径
        file_path = os.path.join(DATA_DIR, f"{group_id}.json")

        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"[Core]群成员列表文件不存在: {file_path}")
            return []

        # 读取群成员列表文件
        with open(file_path, "r", encoding="utf-8") as f:
            member_list = json.load(f)

        # 提取所有成员的QQ号
        user_ids = []
        for member in member_list:
            user_id = member.get("user_id")
            if user_id:
                user_ids.append(str(user_id))

        logger.info(
            f"[Core]成功获取群 {group_id} 的成员QQ号列表，共 {len(user_ids)} 个成员"
        )
        return user_ids

    except Exception as e:
        logger.error(f"[Core]获取群成员QQ号列表失败: {e}")
        return []


def get_group_name_by_id(group_id):
    """
    根据群号获取群名

    Args:
        group_id (str或int): 群号

    Returns:
        str: 群名称，如果找不到则返回None
    """
    try:
        # 确保群号是字符串格式
        group_id = str(group_id)

        # 构建文件路径
        file_path = os.path.join(DATA_DIR, f"{group_id}.json")

        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"[Core]群成员列表文件不存在: {file_path}")
            return None

        # 读取群成员列表文件
        with open(file_path, "r", encoding="utf-8") as f:
            member_list = json.load(f)

        # 从第一个成员中获取群号，验证是否匹配
        if member_list and len(member_list) > 0:
            stored_group_id = str(member_list[0].get("group_id", ""))
            if stored_group_id == group_id:
                # 这里需要从群列表中获取群名，而不是从成员列表
                # 成员列表中没有群名信息，需要调用群列表相关函数
                from .get_group_list import get_group_name_by_id as get_name_from_list

                return get_name_from_list(group_id)

        logger.warning(f"[Core]未找到群号 {group_id} 对应的群成员信息")
        return None

    except Exception as e:
        logger.error(f"[Core]获取群名失败: {e}")
        return None


async def handle_events(websocket, msg):
    """
    处理群成员列表回应事件
    响应示例（群成员列表）:
    {
        "status": "ok",              # 状态，"ok"表示成功
        "retcode": 0,                # 返回码，0通常表示成功
        "data": [                    # 群成员信息数组
            {
                "group_id": "******",        # 群号（已脱敏）
                "user_id": "******",         # 用户QQ号（已脱敏）
                "nickname": "示例昵称",      # QQ昵称（已脱敏）
                "card": "",                  # 群名片
                "sex": "unknown",            # 性别（male/female/unknown）
                "age": 0,                    # 年龄
                "area": "",                  # 地区
                "level": "2",                # 群等级
                "qq_level": 0,               # QQ等级
                "join_time": 1751899434,     # 加群时间（时间戳）
                "last_sent_time": 1751949220,# 最后发言时间（时间戳）
                "title_expire_time": 0,      # 头衔过期时间（时间戳）
                "unfriendly": false,         # 是否不友好
                "card_changeable": true,     # 群名片是否可修改
                "is_robot": false,           # 是否为机器人
                "shut_up_timestamp": 0,      # 禁言到期时间（时间戳）
                "role": "member",            # 成员角色（owner/admin/member）
                "title": ""                  # 专属头衔
            }
        ],
        "message": "",                # 状态消息
        "wording": "",                # 补充信息或提示
        "echo": null                  # 回显字段，用于请求和响应的匹配
    }
    """
    global last_request_time
    try:
        current_time = int(time.time())
        # 检查距离上次请求是否已超过指定时间
        if current_time - last_request_time >= REQUEST_INTERVAL:
            last_request_time = current_time
            # 延迟2秒让群列表更新
            await asyncio.sleep(2)
            group_ids = get_all_group_ids()
            for group_id in group_ids:
                await get_group_member_list(websocket, group_id)

        # 群通知事件
        # 如果有进群退群的通知（系统触发，不受请求间隔限制）
        if (
            msg.get("notice_type") == "group_increase"
            or msg.get("notice_type") == "group_decrease"
        ):
            group_id = str(msg.get("group_id"))
            # 发送获取该群的群成员列表的请求
            await get_group_member_list(websocket, group_id)

        # 回应消息事件
        if msg.get("status") == "ok":
            echo = msg.get("echo", "")
            if echo.startswith("get_group_member_list"):
                # 正则提取group_id
                group_id = re.search(r"group_id=(\d+)", echo)
                if group_id:
                    if msg.get("data", []):
                        # 保存data
                        save_group_member_list_to_file(
                            group_id.group(1), msg.get("data", [])
                        )
                        logger.info(f"[Core]已保存群 {group_id.group(1)} 的成员列表")
                    else:
                        logger.warning(
                            f"[Core]群 {group_id.group(1)} 的成员列表为空，跳过保存，可能是机器人非管理员"
                        )
                else:
                    logger.error(f"[Core]无法提取群号: {echo}")
    except Exception as e:
        logger.error(f"[Core]获取群成员列表失败: {e}")
        await send_private_msg(websocket, OWNER_ID, f"[Core]获取群成员列表失败: {e}")


def get_user_role_in_group(group_id, user_id):
    """
    根据群号和QQ号获取该用户在群内的身份

    Args:
        group_id (str或int): 群号
        user_id (str或int): 用户QQ号

    Returns:
        str: 用户角色，可能的值：
             - "owner": 群主
             - "admin": 管理员
             - "member": 普通成员
             - None: 用户不在群内或获取失败
    """
    try:
        # 确保群号和用户ID都是字符串格式
        group_id = str(group_id)
        user_id = str(user_id)

        # 构建文件路径
        file_path = os.path.join(DATA_DIR, f"{group_id}.json")

        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"[Core]群成员列表文件不存在: {file_path}")
            return None

        # 读取群成员列表文件
        with open(file_path, "r", encoding="utf-8") as f:
            member_list = json.load(f)

        # 查找指定用户
        for member in member_list:
            if str(member.get("user_id")) == user_id:
                role = member.get("role", "member")
                logger.info(f"[Core]用户 {user_id} 在群 {group_id} 中的身份为: {role}")
                return role

        # 用户不在群内
        logger.warning(f"[Core]用户 {user_id} 不在群 {group_id} 中")
        return None

    except Exception as e:
        logger.error(f"[Core]获取用户群内身份失败: {e}")
        return None


def is_user_admin_or_owner(group_id, user_id):
    """
    判断用户是否为群主或管理员

    Args:
        group_id (str或int): 群号
        user_id (str或int): 用户QQ号

    Returns:
        bool: True表示是群主或管理员，False表示是普通成员或不在群内
    """
    role = get_user_role_in_group(group_id, user_id)
    return role in ["owner", "admin"]


def is_user_owner(group_id, user_id):
    """
    判断用户是否为群主

    Args:
        group_id (str或int): 群号
        user_id (str或int): 用户QQ号

    Returns:
        bool: True表示是群主，False表示不是群主
    """
    role = get_user_role_in_group(group_id, user_id)
    return role == "owner"

import logger
from config import OWNER_ID
from api.group import get_group_list
from api.message import send_private_msg
import os
import json
import time

DATA_DIR = os.path.join("data", "Core", "get_group_list.json")

# 全局变量，记录上次请求时间
last_request_time = 0
REQUEST_INTERVAL = 300  # 5分钟，单位：秒


def save_group_list_to_file(item):
    """
    保存群列表信息到文件，确保文件夹存在
    """
    dir_path = os.path.dirname(DATA_DIR)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    with open(DATA_DIR, "w", encoding="utf-8") as f:
        json.dump(item, f, ensure_ascii=False, indent=2)


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

        # 检查文件是否存在
        if not os.path.exists(DATA_DIR):
            logger.warning(f"[Core]群列表文件不存在: {DATA_DIR}")
            return None

        # 读取群列表文件
        with open(DATA_DIR, "r", encoding="utf-8") as f:
            group_list = json.load(f)

        # 查找匹配的群号
        for group in group_list:
            if str(group.get("group_id")) == group_id:
                return group.get("group_name")

        logger.warning(f"[Core]未找到群号 {group_id} 对应的群名")
        return None

    except Exception as e:
        logger.error(f"[Core]获取群名失败: {e}")
        return None


def get_all_group_ids():
    """
    获取所有群号

    Returns:
        list: 群号列表，如果获取失败则返回空列表
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(DATA_DIR):
            logger.warning(f"[Core]群列表文件不存在: {DATA_DIR}")
            return []

        # 读取群列表文件
        with open(DATA_DIR, "r", encoding="utf-8") as f:
            group_list = json.load(f)

        # 提取所有群号
        group_ids = [
            str(group.get("group_id")) for group in group_list if group.get("group_id")
        ]

        logger.success(f"[Core]获取到 {len(group_ids)} 个群号, 群号列表: {group_ids}")
        return group_ids

    except Exception as e:
        logger.error(f"[Core]获取所有群号失败: {e}")
        return []


async def handle_events(websocket, msg):
    """
    处理回应事件
    响应示例:
    {
        "status": "ok",            // 状态，"ok"表示成功
        "retcode": 0,              // 返回码，0通常表示成功
        "data": [                  // 包含多个群组信息的数组
            {
                "group_all_shut": 0,        // 群禁言状态，0表示未全员禁言，1表示已全员禁言，-1表示未知或不适用
                "group_remark": "",         // 群备注名
                "group_id": "********",     // 群号 (已脱敏)
                "group_name": "********",   // 群名称 (已脱敏)
                "member_count": 41,         // 当前群成员数量
                "max_member_count": 200     // 群最大成员数量限制
            }
        ],
        "message": "",              // 状态消息，通常在出错时包含错误信息
        "wording": "",              // 补充信息或提示
        "echo": null                // 回显字段，通常用于请求和响应的匹配
    }
    """
    global last_request_time
    try:
        current_time = int(time.time())
        # 检查距离上次请求是否已超过指定时间
        if current_time - last_request_time >= REQUEST_INTERVAL:
            # 发送获取群列表的请求
            await get_group_list(websocket, no_cache=True)
            last_request_time = current_time

        # 如果有修改群名的通知
        if msg.get("sub_type") == "group_name":
            # 发送获取群列表的请求
            await get_group_list(websocket, no_cache=True)
            last_request_time = current_time

        if msg.get("status") == "ok":
            echo = msg.get("echo", "")
            if echo == "get_group_list":
                # 保存data
                save_group_list_to_file(msg.get("data", []))
                logger.success(f"[Core]已保存群列表")
    except Exception as e:
        logger.error(f"[Core]获取群列表失败: {e}")
        await send_private_msg(websocket, OWNER_ID, f"[Core]获取群列表失败: {e}")
